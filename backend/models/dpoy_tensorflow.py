import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'db'))

import pandas as pd
import numpy as np
from connection import SessionLocal
from sqlalchemy import text
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, roc_auc_score
import tensorflow as tf
from tensorflow import keras
import joblib

def load_training_data(db):
    result = db.execute(text("""
        SELECT
            f.player_id,
            f.season_id,
            s.year as season_year,
            p.full_name,
            f.team_win_pct,
            f.team_conf_rank,
            f.games_played_pct,
            ps.def_ws,
            ps.blocks_per_game,
            ps.steals_per_game,
            ps.rebounds_per_game,
            ps.def_rating,
            CASE WHEN v.final_rank <= 5 THEN 1 ELSE 0 END as dpoy_top5
        FROM player_season_features f
        JOIN players p ON p.id = f.player_id
        JOIN seasons s ON s.id = f.season_id
        JOIN player_season_stats ps ON ps.player_id = f.player_id
            AND ps.season_id = f.season_id
        LEFT JOIN award_votes v ON v.player_id = f.player_id
            AND v.season_id = f.season_id
            AND v.award_type = 'DPOY'
        WHERE f.award_eligible = TRUE
    """))

    df = pd.DataFrame(result.fetchall(), columns=result.keys())

    df["stocks_per_game"] = df["blocks_per_game"] + df["steals_per_game"]
    df["stocks_rank"] = df.groupby("season_year")["stocks_per_game"].rank(ascending=False, method="min").astype(int)
    df["stocks_rank"] = df["stocks_rank"].clip(upper=20)

    return df

def build_model(input_dim):
    model = keras.Sequential([
        keras.layers.Input(shape=(input_dim,)),
        keras.layers.Dense(32, activation='relu', kernel_regularizer=keras.regularizers.l2(0.01)),
        keras.layers.Dropout(0.4),
        keras.layers.Dense(16, activation='relu', kernel_regularizer=keras.regularizers.l2(0.01)),
        keras.layers.Dropout(0.3),
        keras.layers.Dense(8, activation='relu'),
        keras.layers.Dense(1, activation='sigmoid')
    ])
    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy', tf.keras.metrics.AUC(name='auc')]
    )
    return model

def train_model(df):
    feature_cols = [
        "blocks_per_game",
        "steals_per_game",
        "rebounds_per_game",
        "def_rating",
        "def_ws",
        "games_played_pct",
        "team_win_pct",
        "team_conf_rank",
        "stocks_per_game",
        "stocks_rank",
    ]

    fill_values = {col: 0 for col in feature_cols}
    fill_values['def_rating'] = 110
    fill_values['def_ws'] = 0

    df = df.dropna(subset=[c for c in feature_cols if c not in ['def_rating', 'def_ws']])

    train_df = df[df["season_year"].astype(int) <= 2022]
    test_df = df[df["season_year"].astype(int) > 2022]

    X_train = train_df[feature_cols].fillna(fill_values).values
    y_train = train_df["dpoy_top5"].values
    X_test = test_df[feature_cols].fillna(fill_values).values
    y_test = test_df["dpoy_top5"].values

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    neg = np.sum(y_train == 0)
    pos = np.sum(y_train == 1)
    class_weight = {0: 1.0, 1: neg / pos}
    print(f"Class weight for DPOY class: {class_weight[1]:.1f}x")

    model = build_model(len(feature_cols))

    model.fit(
        X_train, y_train,
        epochs=30,
        batch_size=64,
        validation_split=0.2,
        class_weight=class_weight,
        verbose=1
    )

    y_prob = model.predict(X_test).flatten()
    y_pred = (y_prob >= 0.5).astype(int)

    print("\n--- DPOY Model Evaluation ---")
    print(classification_report(y_test, y_pred))
    print(f"ROC-AUC Score: {roc_auc_score(y_test, y_prob):.3f}")

    test_df = test_df.copy()
    test_df["dpoy_probability"] = y_prob

    print("\n--- Top 10 DPOY Candidates (2023-2025) ---")
    top = test_df.nlargest(10, "dpoy_probability")[
        ["full_name", "season_year", "dpoy_probability", "dpoy_top5"]
    ]
    print(top.to_string(index=False))

    save_dir = os.path.join(os.path.dirname(__file__), 'saved_models')
    os.makedirs(save_dir, exist_ok=True)
    model.save(os.path.join(save_dir, 'dpoy_model.keras'))
    joblib.dump(scaler, os.path.join(save_dir, 'dpoy_scaler.pkl'))
    print(f"\nModel saved to {save_dir}")

    return model, scaler

if __name__ == "__main__":
    print("Loading training data...")
    db = SessionLocal()
    df = load_training_data(db)
    db.close()
    print(f"Loaded {len(df)} eligible player seasons")
    print(f"DPOY top-5 appearances: {df['dpoy_top5'].sum()}")

    print("\nTraining DPOY model...")
    model, scaler = train_model(df)