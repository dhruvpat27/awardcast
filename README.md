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

---

## Development Phases

- [x] Phase 1 — Data foundation (schema, ETL, API ingestion)
- [ ] Phase 2 — Feature engineering
- [ ] Phase 3 — Baseline ML models
- [ ] Phase 4 — TensorFlow + experiment tracking
- [ ] Phase 5 — FastAPI backend
- [ ] Phase 6 — React dashboard
- [ ] Phase 7 — Docker, deployment, polish



Other Notes:

Activating the Venv:
source venv/bin/activate

Starting PostgreSQL (in case it doesn't run auto):
brew services start postgresql@15