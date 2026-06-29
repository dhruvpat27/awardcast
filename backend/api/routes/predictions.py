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

@router.get("/dpoy-snubs/{min_probability}")
def get_dpoy_snubs(min_probability: float = 0.85):
    db = SessionLocal()

    import joblib
    import tensorflow as tf
    import numpy as np
    import pandas as pd

    BASE = os.path.join(os.path.dirname(__file__), '..', '..', 'models', 'saved_models')
    model = tf.keras.models.load_model(os.path.join(BASE, 'dpoy_model.keras'))
    scaler = joblib.load(os.path.join(BASE, 'dpoy_scaler.pkl'))

    FEATURE_COLS = [
        "blocks_per_game", "steals_per_game", "rebounds_per_game",
        "def_rating", "def_ws", "games_played_pct", "team_win_pct",
        "team_conf_rank", "stocks_per_game", "stocks_rank",
    ]

    result = db.execute(text("""
        SELECT
            p.id as player_id,
            p.full_name,
            s.label as season,
            s.year as season_year,
            f.games_played_pct,
            f.team_win_pct,
            f.team_conf_rank,
            ps.blocks_per_game,
            ps.steals_per_game,
            ps.rebounds_per_game,
            ps.def_rating,
            ps.def_ws,
            v.final_rank as dpoy_rank,
            v.won as dpoy_winner,
            aw.player_id as actual_winner_id,
            vw.full_name as actual_winner
        FROM player_season_features f
        JOIN players p ON p.id = f.player_id
        JOIN seasons s ON s.id = f.season_id
        JOIN player_season_stats ps ON ps.player_id = f.player_id
            AND ps.season_id = f.season_id
        LEFT JOIN award_votes v ON v.player_id = f.player_id
            AND v.season_id = f.season_id
            AND v.award_type = 'DPOY'
        LEFT JOIN award_votes aw ON aw.season_id = f.season_id
            AND aw.award_type = 'DPOY'
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
    df["stocks_per_game"] = df["blocks_per_game"] + df["steals_per_game"]
    df["stocks_rank"] = df.groupby("season_year")["stocks_per_game"].rank(ascending=False, method="min").astype(int)
    df["stocks_rank"] = df["stocks_rank"].clip(upper=20)

    fill_values = {col: 0 for col in FEATURE_COLS}
    fill_values['def_rating'] = 110
    fill_values['def_ws'] = 0

    X = df[FEATURE_COLS].fillna(fill_values).values
    X_scaled = scaler.transform(X)
    probs = model.predict(X_scaled).flatten()

    df["dpoy_probability"] = probs
    df = df.replace({float('nan'): None})

    snubs = df[df["dpoy_probability"] >= min_probability].copy()
    snubs = snubs.sort_values("dpoy_probability", ascending=False)

    return snubs[[
        "player_id", "full_name", "season", "dpoy_probability",
        "dpoy_rank", "actual_winner_id", "actual_winner",
        "blocks_per_game", "steals_per_game", "def_rating"
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


@router.get("/head-to-head/{player1_id}/{season1}/{player2_id}/{season2}")
def head_to_head(player1_id: int, season1: int, player2_id: int, season2: int):
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

    def get_features(player_id, season_year):
        result = db.execute(text("""
            SELECT
                p.full_name,
                s.label as season,
                f.points_per_game, f.usage_rate, f.ts_pct, f.per,
                f.team_win_pct, f.team_conf_rank, f.games_played_pct,
                f.ppg_rank, f.apg_rank, f.rpg_rank,
                f.ppg_improvement, f.apg_improvement, f.rpg_improvement
            FROM player_season_features f
            JOIN players p ON p.id = f.player_id
            JOIN seasons s ON s.id = f.season_id
            WHERE f.player_id = :player_id AND s.year = :year
        """), {"player_id": player_id, "year": season_year})
        row = result.fetchone()
        return dict(row._mapping) if row else None

    p1 = get_features(player1_id, season1)
    p2 = get_features(player2_id, season2)
    db.close()

    if not p1 or not p2:
        return {"error": "One or both players not found"}

    df = pd.DataFrame([p1, p2])
    X = df[FEATURE_COLS].fillna(0).values
    X_scaled = scaler.transform(X)
    probs = model.predict(X_scaled).flatten()

    p1_prob = float(probs[0])
    p2_prob = float(probs[1])

    # Use softmax-style normalization to amplify differences
    import numpy as np
    raw = np.array([p1_prob, p2_prob])
    # Amplify the gap by raising to a power before normalizing
    amplified = raw ** 50
    total = amplified[0] + amplified[1]

    p1_pct = float(round((amplified[0] / total) * 100, 1))
    p2_pct = float(round((amplified[1] / total) * 100, 1))
    winner = p1["full_name"] if p1_prob > p2_prob else p2["full_name"]

    return {
        "player1": {"name": p1["full_name"], "season": p1["season"], "probability": p1_prob, "share": p1_pct},
        "player2": {"name": p2["full_name"], "season": p2["season"], "probability": p2_prob, "share": p2_pct},
        "winner": winner
    }


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

