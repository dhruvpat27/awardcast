import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'db'))

import time
import pandas as pd
from connection import SessionLocal
from sqlalchemy import text

def scrape_mvp_votes(season_year):
    """
    season_year is the ending year, e.g. 2024 for the 2023-24 season
    Basketball Reference URL format: /awards/awards_2024.html
    """
    url = f"https://www.basketball-reference.com/awards/awards_{season_year}.html"
    
    try:
        # pandas read_html pulls all tables from the page
        tables = pd.read_html(url, header=1)
        # MVP table is always the first table on the page
        mvp_df = tables[0]
        print(f"  Found {len(mvp_df)} MVP vote rows for {season_year}")
        return mvp_df
    except Exception as e:
        print(f"  Failed to scrape {season_year}: {e}")
        return None

import unicodedata

def normalize_name(name):
    """Remove accents and normalize special characters"""
    normalized = unicodedata.normalize('NFKD', name)
    normalized = ''.join(c for c in normalized if not unicodedata.combining(c))
    
    # Manual overrides for known mismatches
    overrides = {
        "Jimmy Butler": "Jimmy Butler III",
    }
    return overrides.get(normalized, normalized)


def ingest_mvp_votes(season_year):
    db = SessionLocal()

    # Get season from DB
    season = db.execute(text("SELECT id FROM seasons WHERE year = :year"), 
                       {"year": season_year}).fetchone()
    if not season:
        print(f"  Season {season_year} not found in DB")
        db.close()
        return
    season_id = season[0]

    mvp_df = scrape_mvp_votes(season_year)
    if mvp_df is None:
        db.close()
        return

    # Clean up columns — Basketball Reference uses these names
    mvp_df.columns = [c.strip() for c in mvp_df.columns]

    for rank, row in enumerate(mvp_df.itertuples(), start=1):
        player_name = normalize_name(row.Player)
        # Find player in DB by name
        player = db.execute(text("""
            SELECT id FROM players 
            WHERE translate(lower(full_name), 'čćđšžàáâãäåèéêëìíîïòóôõöùúûüýÿ', 'ccdszaaaaaaeeeeiiiioooooouuuuyy') 
            = lower(:name)
        """), {"name": player_name}).fetchone()
        
        

        if not player:
            print(f"  Player not found in DB: {player_name}")
            continue
        player_id = player[0]

        # Extract vote data safely
        try:
            first_place_votes = int(row._6) if hasattr(row, '_6') else 0
        except:
            first_place_votes = 0

        try:
            total_points = int(row.Pts) if hasattr(row, 'Pts') else 0
        except:
            total_points = 0

        won = (rank == 1)

        db.execute(text("""
            INSERT INTO award_votes (
                player_id, season_id, award_type,
                first_place_votes, total_points, final_rank, won
            )
            VALUES (
                :player_id, :season_id, :award_type,
                :first_place_votes, :total_points, :final_rank, :won
            )
            ON CONFLICT (player_id, season_id, award_type) DO NOTHING
        """), {
            "player_id": player_id,
            "season_id": season_id,
            "award_type": "MVP",
            "first_place_votes": first_place_votes,
            "total_points": total_points,
            "final_rank": rank,
            "won": won
        })

    db.commit()
    db.close()
    print(f"  Done with {season_year}")

if __name__ == "__main__":
    # 2005 = 2004-05 season through 2025 = 2024-25 season
    season_years = list(range(2005, 2026))

    for year in season_years:
        print(f"Scraping MVP votes for {year}...")
        ingest_mvp_votes(year)
        time.sleep(3)  # be respectful to Basketball Reference

    print("All done.")