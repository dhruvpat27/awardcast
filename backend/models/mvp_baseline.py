import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'db'))

import pandas as pd
import numpy as np
from connection import SessionLocal
from sqlalchemy import text
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, roc_auc_score

def load_training_data(db):
    result = db.execute(text("""
        SELECT
            f.player_id,
            f.season_id,
            s.year as season_year,
            p.full_name,
            f.points_per_game,
            f.usage_rate,
            f.ts_pct,
            f.team_win_pct,
            f.team_conf_rank,
            f.games_played,
            f.games_played_pct,
            f.ppg_rank,
            f.apg_rank,
            f.rpg_rank,
            f.ppg_improvement,
            f.apg_improvement,
            f.rpg_improvement,
            f.per,
            f.win_shares,
            f.bpm,
            f.vorp,
            CASE WHEN v.final_rank <= 5 THEN 1 ELSE 0 END as mvp_top5
        FROM player_season_features f
        JOIN players p ON p.id = f.player_id
        JOIN seasons s ON s.id = f.season_id
        LEFT JOIN award_votes v ON v.player_id = f.player_id 
            AND v.season_id = f.season_id 
            AND v.award_type = 'MVP'
        WHERE f.award_eligible = TRUE
    """))
    return pd.DataFrame(result.fetchall(), columns=result.keys())

def train_baseline_model(df):
    feature_cols = [
    "points_per_game",
    "team_win_pct", "team_conf_rank",
    "games_played_pct",
    "ppg_rank", "apg_rank", "rpg_rank",
    "ppg_improvement", "apg_improvement", "rpg_improvement",
  ]

    # Drop rows with any missing features
    print(df[feature_cols].isnull().sum())
    df = df.dropna(subset=feature_cols)

    # Split by season — train on older seasons, test on recent ones
    # This is important: never test on data the model trained on
    print(df["season_year"].dtype)
    print(df["season_year"].unique())
    train_df = df[df["season_year"].astype(int) <= 2022]
    test_df = df[df["season_year"].astype(int) > 2022]

    X_train = train_df[feature_cols]
    y_train = train_df["mvp_top5"]
    X_test = test_df[feature_cols]
    y_test = test_df["mvp_top5"]

    # Normalize features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Train logistic regression
    model = LogisticRegression(max_iter=1000, class_weight="balanced")
    model.fit(X_train_scaled, y_train)

    # Evaluate
    y_pred = model.predict(X_test_scaled)
    y_prob = model.predict_proba(X_test_scaled)[:, 1]

    print("\n--- Baseline Model Evaluation ---")
    print(classification_report(y_test, y_pred))
    print(f"ROC-AUC Score: {roc_auc_score(y_test, y_prob):.3f}")

    # Show predicted MVP probabilities for test seasons
    test_df = test_df.copy()
    test_df["mvp_probability"] = y_prob

    print("\n--- Top 10 MVP Candidates (2023-2025) ---")
    top = test_df.nlargest(10, "mvp_probability")[
        ["full_name", "season_year", "mvp_probability", "mvp_top5"]
    ]
    print(top.to_string(index=False))

    return model, scaler

if __name__ == "__main__":
    print("Loading training data...")
    db = SessionLocal()
    df = load_training_data(db)
    db.close()
    print(f"Loaded {len(df)} eligible player seasons")
    print(f"MVP top-5 appearances: {df['mvp_top5'].sum()}")

    print("\nTraining baseline model...")
    model, scaler = train_baseline_model(df)