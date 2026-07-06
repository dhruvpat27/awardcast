# AwardCast

AwardCast is an NBA analytics and machine learning experience for exploring MVP and DPOY voting trends, surfacing historical snubs, and comparing players across seasons using model-based probability estimates.

It combines a FastAPI backend, a React frontend, and TensorFlow-based award prediction models to make the data feel interactive and easy to explore.

## Live links

- Frontend: https://awardcast-xbq4-2305ptreg-dhruvprojs.vercel.app/
- Backend API: https://awardcast-production.up.railway.app/
- API docs: https://awardcast-production.up.railway.app/docs

## What the app does

AwardCast is designed for users who want to move beyond surface-level box score browsing and explore how advanced analytics and machine learning interpret NBA award races. The experience combines historical player data, contextual team performance, and award-voting outcomes to surface the players the model believes were most deserving of MVP or DPOY recognition.

Users can:

- Explore MVP and DPOY leaderboards across multiple seasons with model-driven probability estimates rather than relying on conventional narratives alone.
- Dive into individual player profiles to inspect career trajectories, seasonal performance trends, and how the model evaluated each season over time.
- Compare two players side by side in a head-to-head analysis that highlights how the prediction engine would frame their relative award chances.
- Investigate historical snubs and identify cases where the model strongly favored a player who was not ultimately recognized by voters.
- Gain a more analytical perspective on award history by pairing statistical evidence with outcome-based context.

## Key features

- Interactive award leaderboards for MVP and DPOY, with season-based filtering so users can compare how the model ranks players across different years.
- Player detail pages that combine historical career stats with season-by-season MVP probability estimates, making it easier to understand how a player's profile evolved over time.
- A head-to-head comparison experience that lets users compare two players from different seasons and see how the model would likely assess them against each other.
- Historical snub analysis that surfaces players who had strong model confidence but were not selected as actual award winners, helping highlight potential voter bias or overlooked performances.
- A machine learning-driven prediction workflow that uses player stats, team performance, and historical voting data to estimate the likelihood that a player would win an award.
- A polished, data-first user experience built around NBA award conversations, with clear visualizations and easy navigation between leaderboard, player, and comparison views.

## Tech stack

- Frontend: React, React Router, Recharts, Axios
- Backend: FastAPI, SQLAlchemy, PostgreSQL
- ML: TensorFlow, scikit-learn, pandas, numpy, joblib
- Deployment: Vercel (frontend), Railway (backend)

## Project structure

- backend/api: FastAPI routes and app entrypoint
- backend/db: database connection and session setup
- backend/ingestion: data ingestion scripts
- backend/models: model training code and saved model artifacts
- frontend/awardcast-ui: React app

## Model performance

### MVP model
- ROC-AUC: about 0.991
- Trained on historical player-season features and award voting data
- Uses features such as points per game, usage rate, true shooting percentage, player impact estimate, team win percentage, conference rank, games played, and year-over-year improvement

### DPOY model
- ROC-AUC: about 0.905
- Trained on defensive metrics including blocks, steals, rebounds, defensive rating, stocks, team strength, and games played

## Local development

### Prerequisites
- Python 3.10+ or 3.12
- Node.js 18+
- PostgreSQL database

### 1. Clone the repo

```bash
git clone https://github.com/dhruvpat27/awardcast.git
cd awardcast
```

### 2. Create and activate a Python virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Set environment variables

Create a `.env` file in the repo root with either:

```env
DATABASE_URL=postgresql://USER:PASSWORD@HOST:PORT/DBNAME
```

or the individual DB variables:

```env
DB_HOST=...
DB_PORT=5432
DB_NAME=...
DB_USER=...
DB_PASSWORD=...
```

### 5. Run the backend

```bash
python3 -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8000
```

The API will be available at:
- http://127.0.0.1:8000
- http://127.0.0.1:8000/docs

### 6. Run the frontend

```bash
cd frontend/awardcast-ui
npm install
npm start
```

The frontend will be available at:
- http://localhost:3000

## Database schema

The app uses a PostgreSQL schema centered around these tables:

- seasons
- teams
- players
- team_season_stats
- player_season_stats
- award_votes

## Data ingestion

The ingestion scripts live in `backend/ingestion/` and can be run to rebuild the database from NBA data sources.

Example:

```bash
cd backend/ingestion
python3 ingest_teams_seasons.py
```

## Deployment setup

### Backend on Railway

- Build uses the Dockerfile in `backend/Dockerfile`
- Start command:

```bash
python3 -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8000
```

Required environment variables:
- `DATABASE_URL` or the DB variable set

### Frontend on Vercel

- Import the repo into Vercel
- Set the root directory to `frontend/awardcast-ui`
- Build command: `npm run build`
- Output directory: `build`
- Add the backend URL as the API target if you want to make it configurable

## Roadmap ideas

- Add future-season prediction workflows
- Let users input a hypothetical player season and see predicted award chances
- Add richer player comparison visuals
- Improve model explainability and confidence intervals

## Notes

AwardCast is a personal analytics project built to explore how data and machine learning can illuminate historical NBA award voting behavior. It is designed to be useful, interactive, and easy to extend.