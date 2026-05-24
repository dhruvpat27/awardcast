import sys
import os

from fastapi import APIRouter
from connection import SessionLocal
from sqlalchemy import text
import numpy as np
import joblib
import tensorflow as tf

router = APIRouter()

# Load model and scaler once at startup
BASE = os.path.join(os.path.dirname(__file__), '..', '..', 'models', 'saved_models')
model = tf.keras.models.load_model(os.path.join(BASE, 'mvp_model.keras'))
scaler = joblib.load(os.path.join(BASE, 'mvp_scaler.pkl'))

FEATURE_COLS = [
    "points_per_game", "usage_rate", "ts_pct", "per",
    "team_win_pct", "team_conf_rank", "games_played_pct",
    "ppg_rank", "apg_rank", "rpg_rank",
    "ppg_improvement", "apg_improvement", "rpg_improvement",
]

@router.get("/{season_year}")
def get_leaderboard(season_year: int):
    db = SessionLocal()
    result = db.execute(text("""
        SELECT
            p.id as player_id,
            p.full_name,
            s.label as season,
            f.points_per_game, f.usage_rate, f.ts_pct, f.per,
            f.team_win_pct, f.team_conf_rank, f.games_played_pct,
            f.ppg_rank, f.apg_rank, f.rpg_rank,
            f.ppg_improvement, f.apg_improvement, f.rpg_improvement
        FROM player_season_features f
        JOIN players p ON p.id = f.player_id
        JOIN seasons s ON s.id = f.season_id
        WHERE s.year = :year AND f.award_eligible = TRUE
    """), {"year": season_year})

    rows = [dict(row._mapping) for row in result]
    db.close()

    if not rows:
        return []

    import pandas as pd
    df = pd.DataFrame(rows)
    X = df[FEATURE_COLS].fillna(0).values
    X_scaled = scaler.transform(X)
    probs = model.predict(X_scaled).flatten()

    df["mvp_probability"] = probs
    df = df.sort_values("mvp_probability", ascending=False)

    return df[["player_id", "full_name", "season", "mvp_probability"]].head(20).to_dict(orient="records")