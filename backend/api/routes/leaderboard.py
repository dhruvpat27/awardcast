import os
import pandas as pd
import numpy as np
import joblib
import tensorflow as tf
from fastapi import APIRouter
from connection import SessionLocal
from sqlalchemy import text

router = APIRouter()

BASE = os.path.join(os.path.dirname(__file__), '..', '..', 'models', 'saved_models')

mvp_model = tf.keras.models.load_model(os.path.join(BASE, 'mvp_model.keras'))
mvp_scaler = joblib.load(os.path.join(BASE, 'mvp_scaler.pkl'))

dpoy_model = tf.keras.models.load_model(os.path.join(BASE, 'dpoy_model.keras'))
dpoy_scaler = joblib.load(os.path.join(BASE, 'dpoy_scaler.pkl'))

MVP_FEATURES = [
    "points_per_game", "usage_rate", "ts_pct", "per",
    "team_win_pct", "team_conf_rank", "games_played_pct",
    "ppg_rank", "apg_rank", "rpg_rank",
    "ppg_improvement", "apg_improvement", "rpg_improvement",
]

DPOY_FEATURES = [
    "blocks_per_game", "steals_per_game", "rebounds_per_game",
    "def_rating", "def_ws", "games_played_pct", "team_win_pct", "team_conf_rank",
    "stocks_per_game", "stocks_rank",
]

@router.get("/{award}/{season_year}")
def get_leaderboard(award: str, season_year: int):
    if award not in ["mvp", "dpoy"]:
        return {"error": "Award must be mvp or dpoy"}

    db = SessionLocal()

    if award == "dpoy":
        result = db.execute(text("""
            SELECT
                p.id as player_id,
                p.full_name,
                s.label as season,
                f.games_played_pct,
                f.team_win_pct,
                f.team_conf_rank,
                ps.blocks_per_game,
                ps.steals_per_game,
                ps.rebounds_per_game,
                ps.def_rating,
                ps.def_ws
            FROM player_season_features f
            JOIN players p ON p.id = f.player_id
            JOIN seasons s ON s.id = f.season_id
            JOIN player_season_stats ps ON ps.player_id = f.player_id
                AND ps.season_id = f.season_id
            WHERE s.year = :year AND f.award_eligible = TRUE
        """), {"year": season_year})
    else:
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

    df = pd.DataFrame(rows)

    if award == "dpoy":
        df["stocks_per_game"] = df["blocks_per_game"] + df["steals_per_game"]
        df["stocks_rank"] = df["stocks_per_game"].rank(ascending=False, method="min").astype(int)
        df["stocks_rank"] = df["stocks_rank"].clip(upper=20)
        features = DPOY_FEATURES
        model = dpoy_model
        scaler = dpoy_scaler
        prob_col = "dpoy_probability"
    else:
        features = MVP_FEATURES
        model = mvp_model
        scaler = mvp_scaler
        prob_col = "mvp_probability"

    fill_values = {col: 0 for col in features}
    fill_values['def_rating'] = 110
    fill_values['def_ws'] = 0

    X = df[features].fillna(fill_values).values
    X_scaled = scaler.transform(X)
    probs = model.predict(X_scaled).flatten()

    df[prob_col] = probs
    df = df.sort_values(prob_col, ascending=False)

    return df[["player_id", "full_name", "season", prob_col]].head(20).to_dict(orient="records")