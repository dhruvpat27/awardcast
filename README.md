## AwardCast
**Functionality**
AwardCast is an NBA analytics and machine learning platform built to analyze MVP voting trends, predict award outcomes, and investigate whether certain players were statistically “snubbed” of MVP awards. The project uses historical NBA player statistics, advanced metrics, team performance, and award voting data to allow users to see what machine learning models determine the “statistical MVP” should have been. 

Want to eventually extend it to an app that can forecast future MVP's or allow you to input a player's stats into a year they did not play in and see if they would win MVP or not.

## Current Functionality
Able to display with Machine Learning, every year's suggest MVP based on previous trends, and provides a bar graph of the top leaders. This works for 2004 - 2025. Also allows you to compare players that were in the running from MVP between years, for instance, allowing you to compare SGA's 2025 MVP year to Jokic in 2024. Also displays all potential MVP snubs throughout the 20 years with ranging model confidence rates. 

## Model Performance

### MVP Model (TensorFlow Neural Network)
- **ROC-AUC: 0.996**
- Trained on 21 seasons (2004-05 through 2024-25) of player season stats, advanced metrics, and historical voting data
- Features: points per game, usage rate, true shooting %, team win percentage, conference rank, games played, league rankings, year-over-year improvement, PIE
- Test set: 2022-23 through 2024-25 seasons
- Top 10 predicted candidates across test seasons were all confirmed top-5 MVP vote receivers
- Known limitation: model reflects statistical merit, not voter narrative — explains historically snubbed players like James Harden (2018-19, 36.1 PPG) and Luka Dončić (2023-24, 33.9 PPG)

### DPOY Model (TensorFlow Neural Network)
- **ROC-AUC: 0.935**
- Same architecture as MVP model, trained on DPOY-specific features
- Features: blocks per game, steals per game, rebounds per game, defensive rating, games played percentage, team win percentage, conference rank, stocks (blocks + steals) per game, stocks rank
- Test set: 2022-23 through 2024-25 seasons
- Lower accuracy than MVP reflects the fundamental difficulty of quantifying defensive impact through box score stats alone — metrics like steals and blocks don't capture defensive IQ, positioning, or deterrence effect
- Known limitation: model overrates guards with high steal rates (e.g. SGA) since traditional stats can't distinguish defensive specialists from offensive stars with good steal numbers

## Phase Notes
### VENV + Database Set Up
#### Database Schema

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
- [x] Phase 6a — Player page with career trajectory and MVP probability chart
- [x] Phase 6b — Historical snubs page revealing MVP voter bias
- [x] Phase 6c — Compare page with radar chart, stat cards, and head-to-head MVP predictor
- [ ] Phase 7 — Docker, deployment, polish

Other Notes:

Activating the Venv:
source venv/bin/activate

Starting PostgreSQL (in case it doesn't run auto):
brew services start postgresql@15