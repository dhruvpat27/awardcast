import sys
import os

from fastapi import APIRouter
from connection import SessionLocal
from sqlalchemy import text

router = APIRouter()

@router.get("/")
def get_players():
    db = SessionLocal()
    result = db.execute(text("""
        SELECT id, full_name, position, is_active
        FROM players
        ORDER BY full_name
    """))
    players = [dict(row._mapping) for row in result]
    db.close()
    return players

@router.get("/{player_id}")
def get_player(player_id: int):
    db = SessionLocal()
    result = db.execute(text("""
        SELECT p.id, p.full_name, p.position,
               s.label as season,
               ps.points_per_game, ps.assists_per_game, ps.rebounds_per_game,
               ps.games_played
        FROM players p
        JOIN player_season_stats ps ON ps.player_id = p.id
        JOIN seasons s ON s.id = ps.season_id
        WHERE p.id = :player_id
        ORDER BY s.year DESC
    """), {"player_id": player_id})
    rows = [dict(row._mapping) for row in result]
    db.close()
    return rows