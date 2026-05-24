Phase Notes
VENV + Database Set Up:
## Database Schema

Six tables make up the foundation of the data warehouse:

- **seasons** — each NBA season, stored by year and label (e.g. 2023-24)
- **teams** — all NBA teams with their NBA.com ID and abbreviation
- **players** — all players with their NBA.com ID, name, position, active status
- **team_season_stats** — wins, losses, win percentage, conference rank per season
- **player_season_stats** — full per-game and advanced stats for each player per season
- **award_votes** — historical MVP/MIP/DPOY voting results used as ML training labels

---

## Why a Virtual Environment

A venv isolates this project's Python dependencies from everything else on your machine.
Without it, installing packages globally can cause version conflicts across projects.
The `requirements.txt` file captures the exact versions used so anyone cloning this repo
can recreate the environment exactly with `pip install -r requirements.txt`.

## Data Ingestion

Data is pulled using `nba_api`, a free Python package that hits NBA.com endpoints directly.
No API key required. Scripts live in `backend/ingestion/`.

### What's been ingested so far
- **30 NBA teams** — pulled from nba_api static data, stored with NBA.com team IDs
- **20 seasons** — 2004-05 through 2024-25, stored with year and label
- **2225 players** - the stats of all 2225 players who played during this time period

### Development Phase Notes
- First model was slightly inaccurate, picked Luka for 2024, because it overweighs scoring rate (ppg). More advanced stats like BPM and other factors will be added next
- Added advanced stats to PostgreSQL table, now can pull info. like utility rate, true shooting pct, and much more. These now affect the mvp predictions, Jokic is properly represented for 2024 and 2025.
- Created first Tensorflow model for MVP. Only one inaccuracy so far, Luka is back as 2024 MVP favorite, barely over Jokic. This might be statistically accurate (a lot of people that year say Luka was robbed of the award)
- Made FastAPI backend which stores and provides easy access to the Tensorflow model's output.


### To re-run ingestion
```bash
cd backend/ingestion
python3 ingest_teams_seasons.py


## Development Phases

- [x] Phase 1a — Project setup (venv, dependencies, PostgreSQL)
- [x] Phase 1b — Database schema (6 tables)
- [x] Phase 1c — DB connection via SQLAlchemy
- [x] Phase 1d — Teams and seasons ingested
- [x] Phase 1e — Player and team season stats ingestion
- [x] Phase 2 — Feature engineering
- [x] Phase 3a — Historical MVP voting data scraped from Basketball Reference (21 seasons)
- [x] Phase 3b - Baseline ML models
- [x] Phase 4 — TensorFlow neural network MVP model (ROC-AUC: 0.996)
- [x] Phase 5 — FastAPI backend (players, leaderboard, predictions endpoints)
- [ ] Phase 6 — React dashboard
- [ ] Phase 7 — Docker, deployment, polish

Other Notes:

Activating the Venv:
source venv/bin/activate

Starting PostgreSQL (in case it doesn't run auto):
brew services start postgresql@15