import sys
import os

# Add db and models to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'db'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'models'))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import players, leaderboard, predictions

app = FastAPI(title="AwardCast API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(players.router, prefix="/players", tags=["players"])
app.include_router(leaderboard.router, prefix="/leaderboard", tags=["leaderboard"])
app.include_router(predictions.router, prefix="/predictions", tags=["predictions"])

@app.get("/")
def root():
    return {"message": "AwardCast API is running"}