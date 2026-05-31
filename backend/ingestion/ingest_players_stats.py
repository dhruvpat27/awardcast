import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'db'))
import pandas as pd
import time
from connection import SessionLocal
from sqlalchemy import text
from nba_api.stats.endpoints import leaguedashplayerstats, leaguestandingsv3

def ingest_players_and_stats(season_label):
    db = SessionLocal()

    print(f"Fetching player stats for {season_label}...")
    time.sleep(0.5)

    stats = leaguedashplayerstats.LeagueDashPlayerStats(
        season=season_label,
        per_mode_detailed="PerGame"
    ).get_data_frames()[0]

    # Get season_id from DB
    year = int(season_label[:4]) + 1
    season = db.execute(text("SELECT id FROM seasons WHERE year = :year"), {"year": year}).fetchone()
    if not season:
        print(f"Season {season_label} not found in DB, skipping.")
        db.close()
        return
    season_id = season[0]

    for _, row in stats.iterrows():
        # Upsert player
        db.execute(text("""
            INSERT INTO players (nba_player_id, full_name, is_active)
            VALUES (:nba_player_id, :full_name, TRUE)
            ON CONFLICT (nba_player_id) DO NOTHING
        """), {
            "nba_player_id": int(row["PLAYER_ID"]),
            "full_name": row["PLAYER_NAME"]
        })

        # Get player internal id
        player = db.execute(text("SELECT id FROM players WHERE nba_player_id = :nba_player_id"), {
            "nba_player_id": int(row["PLAYER_ID"])
        }).fetchone()
        player_id = player[0]

        # Get team internal id
        team = db.execute(text("SELECT id FROM teams WHERE nba_team_id = :nba_team_id"), {
            "nba_team_id": int(row["TEAM_ID"])
        }).fetchone()
        team_id = team[0] if team else None

        # Upsert player season stats
        db.execute(text("""
            INSERT INTO player_season_stats (
                player_id, team_id, season_id,
                games_played, points_per_game, assists_per_game,
                rebounds_per_game, steals_per_game, blocks_per_game,
                fg_pct, fg3_pct, ft_pct
            )
            VALUES (
                :player_id, :team_id, :season_id,
                :games_played, :points_per_game, :assists_per_game,
                :rebounds_per_game, :steals_per_game, :blocks_per_game,
                :fg_pct, :fg3_pct, :ft_pct
            )
            ON CONFLICT (player_id, season_id) DO NOTHING
        """), {
            "player_id": player_id,
            "team_id": team_id,
            "season_id": season_id,
            "games_played": int(row["GP"]),
            "points_per_game": float(row["PTS"]),
            "assists_per_game": float(row["AST"]),
            "rebounds_per_game": float(row["REB"]),
            "steals_per_game": float(row["STL"]),
            "blocks_per_game": float(row["BLK"]),
            "fg_pct": float(row["FG_PCT"]),
            "fg3_pct": float(row["FG3_PCT"]),
            "ft_pct": float(row["FT_PCT"])
        })

    db.commit()
    db.close()
    print(f"Done with {season_label}")

def ingest_advanced_stats(season_label):
    db = SessionLocal()

    print(f"Fetching advanced stats for {season_label}...")
    time.sleep(0.5)

    advanced = leaguedashplayerstats.LeagueDashPlayerStats(
        season=season_label,
        measure_type_detailed_defense="Advanced"
    ).get_data_frames()[0]

    year = int(season_label[:4]) + 1
    season = db.execute(text("SELECT id FROM seasons WHERE year = :year"), {"year": year}).fetchone()
    if not season:
        print(f"Season {season_label} not found in DB, skipping.")
        db.close()
        return
    season_id = season[0]

    for _, row in advanced.iterrows():
        player = db.execute(text("SELECT id FROM players WHERE nba_player_id = :nba_player_id"), {
            "nba_player_id": int(row["PLAYER_ID"])
        }).fetchone()
        if not player:
            continue
        player_id = player[0]

        db.execute(text("""
            UPDATE player_season_stats
            SET 
                usage_rate = :usage_rate,
                true_shooting_pct = :ts_pct,
                per = :per
            WHERE player_id = :player_id AND season_id = :season_id
        """), {
            "player_id": player_id,
            "season_id": season_id,
            "usage_rate": float(row["USG_PCT"]) if pd.notna(row["USG_PCT"]) else None,
            "ts_pct": float(row["TS_PCT"]) if pd.notna(row["TS_PCT"]) else None,
            "per": float(row["PIE"]) if pd.notna(row["PIE"]) else None,
        })

    db.commit()
    db.close()
    print(f"Advanced stats done for {season_label}")

def ingest_defensive_stats(season_label):
    db = SessionLocal()

    print(f"Fetching defensive stats for {season_label}...")
    time.sleep(0.5)

    defensive = leaguedashplayerstats.LeagueDashPlayerStats(
        season=season_label,
        measure_type_detailed_defense="Defense"
    ).get_data_frames()[0]

    year = int(season_label[:4]) + 1
    season = db.execute(text("SELECT id FROM seasons WHERE year = :year"), {"year": year}).fetchone()
    if not season:
        print(f"Season {season_label} not found in DB, skipping.")
        db.close()
        return
    season_id = season[0]

    for _, row in defensive.iterrows():
        player = db.execute(text("SELECT id FROM players WHERE nba_player_id = :nba_player_id"), {
            "nba_player_id": int(row["PLAYER_ID"])
        }).fetchone()
        if not player:
            continue
        player_id = player[0]

        db.execute(text("""
            UPDATE player_season_stats
            SET def_rating = :def_rating
            WHERE player_id = :player_id AND season_id = :season_id
        """), {
            "player_id": player_id,
            "season_id": season_id,
            "def_rating": float(row["DEF_RATING"]) if pd.notna(row["DEF_RATING"]) else None,
        })

    db.commit()
    db.close()
    print(f"Defensive stats done for {season_label}")



def ingest_team_stats(season_label):
    db = SessionLocal()

    print(f"Fetching team standings for {season_label}...")
    time.sleep(0.5)

    standings = leaguestandingsv3.LeagueStandingsV3(
        season=season_label
    ).get_data_frames()[0]

    year = int(season_label[:4]) + 1
    season = db.execute(text("SELECT id FROM seasons WHERE year = :year"), {"year": year}).fetchone()
    if not season:
        db.close()
        return
    season_id = season[0]

    for _, row in standings.iterrows():
        team = db.execute(text("SELECT id FROM teams WHERE nba_team_id = :nba_team_id"), {
            "nba_team_id": int(row["TeamID"])
        }).fetchone()
        if not team:
            continue
        team_id = team[0]

        db.execute(text("""
            INSERT INTO team_season_stats (team_id, season_id, wins, losses, win_pct, conf_rank)
            VALUES (:team_id, :season_id, :wins, :losses, :win_pct, :conf_rank)
            ON CONFLICT (team_id, season_id) DO NOTHING
        """), {
            "team_id": team_id,
            "season_id": season_id,
            "wins": int(row["WINS"]),
            "losses": int(row["LOSSES"]),
            "win_pct": float(row["WinPCT"]),
            "conf_rank": int(row["PlayoffRank"])
        })

    db.commit()
    db.close()
    print(f"Team stats done for {season_label}")

if __name__ == "__main__":
    seasons = [
        "2004-05", "2005-06", "2006-07", "2007-08", "2008-09",
        "2009-10", "2010-11", "2011-12", "2012-13", "2013-14",
        "2014-15", "2015-16", "2016-17", "2017-18", "2018-19",
        "2019-20", "2020-21", "2021-22", "2022-23", "2023-24",
        "2024-25"
    ]

    for season in seasons:
        ingest_defensive_stats(season)
        time.sleep(1)

    print("All done.")