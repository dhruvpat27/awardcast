import sys
import os

from fastapi import APIRouter
from connection import SessionLocal
from sqlalchemy import text

router = APIRouter()

@router.get("/snubs/{min_probability}")
def get_snubs(min_probability: float = 0.85):
    db = SessionLocal()

    import joblib
    import tensorflow as tf
    import numpy as np
    import pandas as pd

    BASE = os.path.join(os.path.dirname(__file__), '..', '..', 'models', 'saved_models')
    model = tf.keras.models.load_model(os.path.join(BASE, 'mvp_model.keras'))
    scaler = joblib.load(os.path.join(BASE, 'mvp_scaler.pkl'))

    FEATURE_COLS = [
        "points_per_game", "usage_rate", "ts_pct", "per",
        "team_win_pct", "team_conf_rank", "games_played_pct",
        "ppg_rank", "apg_rank", "rpg_rank",
        "ppg_improvement", "apg_improvement", "rpg_improvement",
    ]

    result = db.execute(text("""
        SELECT
            p.id as player_id,
            p.full_name,
            s.label as season,
            s.year as season_year,
            f.points_per_game, f.usage_rate, f.ts_pct, f.per,
            f.team_win_pct, f.team_conf_rank, f.games_played_pct,
            f.ppg_rank, f.apg_rank, f.rpg_rank,
            f.ppg_improvement, f.apg_improvement, f.rpg_improvement,
            v.final_rank as mvp_rank,
            v.won as mvp_winner,
            aw.player_id as actual_winner_id,
            vw.full_name as actual_winner
        FROM player_season_features f
        JOIN players p ON p.id = f.player_id
        JOIN seasons s ON s.id = f.season_id
        LEFT JOIN award_votes v ON v.player_id = f.player_id
            AND v.season_id = f.season_id
            AND v.award_type = 'MVP'
        LEFT JOIN award_votes aw ON aw.season_id = f.season_id
            AND aw.award_type = 'MVP'
            AND aw.won = TRUE
        LEFT JOIN players vw ON vw.id = aw.player_id
        WHERE f.award_eligible = TRUE
        AND (v.won = FALSE OR v.won IS NULL)
        ORDER BY s.year
    """))

    rows = [dict(row._mapping) for row in result]
    db.close()

    if not rows:
        return []

    df = pd.DataFrame(rows)
    X = df[FEATURE_COLS].fillna(0).values
    X_scaled = scaler.transform(X)
    probs = model.predict(X_scaled).flatten()

    df["mvp_probability"] = probs

    # Snubs = high model probability but didn't win
    snubs = df[df["mvp_probability"] >= min_probability].copy()
    snubs = snubs.sort_values("mvp_probability", ascending=False)

    snubs = snubs.replace({float('nan'): None})

    return snubs[[
        "player_id", "full_name", "season", "mvp_probability",
        "mvp_rank", "actual_winner_id", "actual_winner", "points_per_game",
        "team_win_pct"
    ]].to_dict(orient="records")



@router.get("/player/{player_id}")
def get_player_predictions(player_id: int):
    db = SessionLocal()

    # Load model and scaler
    import joblib
    import tensorflow as tf
    import numpy as np
    import pandas as pd

    BASE = os.path.join(os.path.dirname(__file__), '..', '..', 'models', 'saved_models')
    model = tf.keras.models.load_model(os.path.join(BASE, 'mvp_model.keras'))
    scaler = joblib.load(os.path.join(BASE, 'mvp_scaler.pkl'))

    FEATURE_COLS = [
        "points_per_game", "usage_rate", "ts_pct", "per",
        "team_win_pct", "team_conf_rank", "games_played_pct",
        "ppg_rank", "apg_rank", "rpg_rank",
        "ppg_improvement", "apg_improvement", "rpg_improvement",
    ]

    result = db.execute(text("""
        SELECT
            s.label as season,
            f.points_per_game, f.usage_rate, f.ts_pct, f.per,
            f.team_win_pct, f.team_conf_rank, f.games_played_pct,
            f.ppg_rank, f.apg_rank, f.rpg_rank,
            f.ppg_improvement, f.apg_improvement, f.rpg_improvement,
            v.final_rank as mvp_rank,
            v.won as mvp_winner
        FROM player_season_features f
        JOIN seasons s ON s.id = f.season_id
        LEFT JOIN award_votes v ON v.player_id = f.player_id
            AND v.season_id = f.season_id
            AND v.award_type = 'MVP'
        WHERE f.player_id = :player_id
        AND f.award_eligible = TRUE
        ORDER BY s.year
    """), {"player_id": player_id})

    rows = [dict(row._mapping) for row in result]
    db.close()

    if not rows:
        return []

    df = pd.DataFrame(rows)
    X = df[FEATURE_COLS].fillna(0).values
    X_scaled = scaler.transform(X)
    probs = model.predict(X_scaled).flatten()

    for i, row in enumerate(rows):
        row["mvp_probability"] = float(probs[i])


    return rows

@router.get("/{player_id}/{season_year}")
def get_player_prediction(player_id: int, season_year: int):
    db = SessionLocal()
    result = db.execute(text("""
        SELECT
            p.full_name,
            s.label as season,
            f.points_per_game, f.usage_rate, f.ts_pct, f.per,
            f.team_win_pct, f.team_conf_rank,
            f.games_played, f.award_eligible,
            v.final_rank as mvp_rank,
            v.won as mvp_winner
        FROM player_season_features f
        JOIN players p ON p.id = f.player_id
        JOIN seasons s ON s.id = f.season_id
        LEFT JOIN award_votes v ON v.player_id = f.player_id
            AND v.season_id = f.season_id
            AND v.award_type = 'MVP'
        WHERE f.player_id = :player_id AND s.year = :year
    """), {"player_id": player_id, "year": season_year})

    row = result.fetchone()
    db.close()

    if not row:
        return {"error": "Player/season not found"}

    return dict(row._mapping)

