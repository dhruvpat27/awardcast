import sys
import os

from fastapi import APIRouter
from connection import SessionLocal
from sqlalchemy import text

router = APIRouter()

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