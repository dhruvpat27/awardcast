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
            f.per,
            f.team_win_pct,
            f.team_conf_rank,
            f.games_played_pct,
            f.ppg_rank,
            f.apg_rank,
            f.rpg_rank,
            f.ppg_improvement,
            f.apg_improvement,
            f.rpg_improvement,
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

def build_model(input_dim):
    model = keras.Sequential([
        keras.layers.Input(shape=(input_dim,)),
        keras.layers.Dense(64, activation='relu'),
        keras.layers.Dropout(0.3),
        keras.layers.Dense(32, activation='relu'),
        keras.layers.Dropout(0.2),
        keras.layers.Dense(16, activation='relu'),
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
        "points_per_game", "usage_rate", "ts_pct", "per",
        "team_win_pct", "team_conf_rank",
        "games_played_pct",
        "ppg_rank", "apg_rank", "rpg_rank",
        "ppg_improvement", "apg_improvement", "rpg_improvement",
    ]

    df = df.dropna(subset=feature_cols)

    train_df = df[df["season_year"].astype(int) <= 2022]
    test_df = df[df["season_year"].astype(int) > 2022]

    X_train = train_df[feature_cols].values
    y_train = train_df["mvp_top5"].values
    X_test = test_df[feature_cols].values
    y_test = test_df["mvp_top5"].values

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    # Handle class imbalance — very few MVP candidates vs everyone else
    neg = np.sum(y_train == 0)
    pos = np.sum(y_train == 1)
    class_weight = {0: 1.0, 1: neg / pos}
    print(f"Class weight for MVP class: {class_weight[1]:.1f}x")

    model = build_model(len(feature_cols))
    model.summary()

    history = model.fit(
        X_train, y_train,
        epochs=50,
        batch_size=32,
        validation_split=0.2,
        class_weight=class_weight,
        verbose=1
    )

    # Evaluate
    y_prob = model.predict(X_test).flatten()
    y_pred = (y_prob >= 0.5).astype(int)

    print("\n--- TensorFlow Model Evaluation ---")
    print(classification_report(y_test, y_pred))
    print(f"ROC-AUC Score: {roc_auc_score(y_test, y_prob):.3f}")

    # Show top predictions
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

    print("\nTraining TensorFlow model...")
    model, scaler = train_model(df)