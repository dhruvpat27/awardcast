import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'db'))

import time
from connection import SessionLocal
from nba_api.stats.static import teams
from sqlalchemy import text

def ingest_teams():
    db = SessionLocal()
    nba_teams = teams.get_teams()

    for team in nba_teams:
        db.execute(text("""
            INSERT INTO teams (nba_team_id, name, abbreviation, city)
            VALUES (:nba_team_id, :name, :abbreviation, :city)
            ON CONFLICT (nba_team_id) DO NOTHING
        """), {
            "nba_team_id": team["id"],
            "name": team["full_name"],
            "abbreviation": team["abbreviation"],
            "city": team["city"]
        })

    db.commit()
    db.close()
    print(f"Inserted {len(nba_teams)} teams")

def ingest_seasons():
    db = SessionLocal()

    # We'll pull data from 2004-05 through 2023-24
    seasons = []
    for year in range(2005, 2026):
        label = f"{year-1}-{str(year)[2:]}"
        seasons.append({"year": year, "label": label})

    for season in seasons:
        db.execute(text("""
            INSERT INTO seasons (year, label)
            VALUES (:year, :label)
            ON CONFLICT (year) DO NOTHING
        """), season)

    db.commit()
    db.close()
    print(f"Inserted {len(seasons)} seasons")

if __name__ == "__main__":
    print("Ingesting teams...")
    ingest_teams()
    print("Ingesting seasons...")
    ingest_seasons()
    print("Done.")