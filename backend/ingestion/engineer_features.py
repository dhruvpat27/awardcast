import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'db'))

import pandas as pd
from connection import SessionLocal
from sqlalchemy import text

def load_player_stats(db):
    result = db.execute(text("""
        SELECT 
            ps.player_id,
            ps.season_id,
            ps.team_id,
            ps.games_played,
            ps.points_per_game,
            ps.assists_per_game,
            ps.rebounds_per_game,
            ps.fg_pct,
            ps.fg3_pct,
            ps.ft_pct,
            ps.true_shooting_pct,
            ps.usage_rate,
            ps.per,
            ps.win_shares,
            ps.bpm,
            ps.vorp,
            s.year as season_year,
            t.win_pct as team_win_pct,
            t.conf_rank as team_conf_rank,
            t.wins + t.losses as team_games
        FROM player_season_stats ps
        JOIN seasons s ON s.id = ps.season_id
        LEFT JOIN team_season_stats t ON t.team_id = ps.team_id AND t.season_id = ps.season_id
    """))
    return pd.DataFrame(result.fetchall(), columns=result.keys())

def engineer_features(df):
    # Games played percentage (out of 82)
    df["games_played_pct"] = df["games_played"] / 82.0
    df["award_eligible"] = df["games_played"] >= 65

    # League rankings per season
    df["ppg_rank"] = df.groupby("season_year")["points_per_game"].rank(ascending=False, method="min").astype(int)
    df["apg_rank"] = df.groupby("season_year")["assists_per_game"].rank(ascending=False, method="min").astype(int)
    df["rpg_rank"] = df.groupby("season_year")["rebounds_per_game"].rank(ascending=False, method="min").astype(int)

    # Year over year improvement
    df = df.sort_values(["player_id", "season_year"])
    df["ppg_improvement"] = df.groupby("player_id")["points_per_game"].diff()
    df["apg_improvement"] = df.groupby("player_id")["assists_per_game"].diff()
    df["rpg_improvement"] = df.groupby("player_id")["rebounds_per_game"].diff()

    # Fill NaN improvements with 0 (first season for a player)
    df["ppg_improvement"] = df["ppg_improvement"].fillna(0)
    df["apg_improvement"] = df["apg_improvement"].fillna(0)
    df["rpg_improvement"] = df["rpg_improvement"].fillna(0)

    return df

def save_features(db, df):
    inserted = 0
    for _, row in df.iterrows():
        db.execute(text("""
            INSERT INTO player_season_features (
                player_id, season_id,
                points_per_game, usage_rate, ts_pct,
                team_win_pct, team_conf_rank,
                games_played, games_played_pct,
                ppg_rank, apg_rank, rpg_rank,
                ppg_improvement, apg_improvement, rpg_improvement,
                per, win_shares, bpm, vorp, award_eligible
            )
            VALUES (
                :player_id, :season_id,
                :points_per_game, :usage_rate, :ts_pct,
                :team_win_pct, :team_conf_rank,
                :games_played, :games_played_pct,
                :ppg_rank, :apg_rank, :rpg_rank,
                :ppg_improvement, :apg_improvement, :rpg_improvement,
                :per, :win_shares, :bpm, :vorp, :award_eligible
            )
            ON CONFLICT (player_id, season_id) DO UPDATE
              SET award_eligible = EXCLUDED.award_eligible
        """), {
            "player_id": int(row["player_id"]),
            "season_id": int(row["season_id"]),
            "points_per_game": float(row["points_per_game"]) if pd.notna(row["points_per_game"]) else None,
            "usage_rate": float(row["usage_rate"]) if pd.notna(row["usage_rate"]) else None,
            "ts_pct": float(row["true_shooting_pct"]) if pd.notna(row["true_shooting_pct"]) else None,
            "team_win_pct": float(row["team_win_pct"]) if pd.notna(row["team_win_pct"]) else None,
            "team_conf_rank": int(row["team_conf_rank"]) if pd.notna(row["team_conf_rank"]) else None,
            "games_played": int(row["games_played"]) if pd.notna(row["games_played"]) else None,
            "games_played_pct": float(row["games_played_pct"]) if pd.notna(row["games_played_pct"]) else None,
            "ppg_rank": int(row["ppg_rank"]) if pd.notna(row["ppg_rank"]) else None,
            "apg_rank": int(row["apg_rank"]) if pd.notna(row["apg_rank"]) else None,
            "rpg_rank": int(row["rpg_rank"]) if pd.notna(row["rpg_rank"]) else None,
            "ppg_improvement": float(row["ppg_improvement"]) if pd.notna(row["ppg_improvement"]) else None,
            "apg_improvement": float(row["apg_improvement"]) if pd.notna(row["apg_improvement"]) else None,
            "rpg_improvement": float(row["rpg_improvement"]) if pd.notna(row["rpg_improvement"]) else None,
            "per": float(row["per"]) if pd.notna(row["per"]) else None,
            "win_shares": float(row["win_shares"]) if pd.notna(row["win_shares"]) else None,
            "bpm": float(row["bpm"]) if pd.notna(row["bpm"]) else None,
            "vorp": float(row["vorp"]) if pd.notna(row["vorp"]) else None,
            "award_eligible": bool(row["award_eligible"]),
        })
        inserted += 1

    db.commit()
    print(f"Inserted {inserted} feature rows")

if __name__ == "__main__":
    db = SessionLocal()
    print("Loading player stats...")
    df = load_player_stats(db)
    print(f"Loaded {len(df)} rows")

    print("Engineering features...")
    df = engineer_features(df)

    print("Saving features to DB...")
    save_features(db, df)
    db.close()
    print("Done.")