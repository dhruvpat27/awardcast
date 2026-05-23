-- Seasons
CREATE TABLE IF NOT EXISTS seasons (
    id SERIAL PRIMARY KEY,
    year INTEGER NOT NULL UNIQUE,  -- e.g. 2024 means 2023-24 season
    label VARCHAR(10) NOT NULL     -- e.g. '2023-24'
);

-- Teams
CREATE TABLE IF NOT EXISTS teams (
    id SERIAL PRIMARY KEY,
    nba_team_id INTEGER UNIQUE,
    name VARCHAR(100) NOT NULL,
    abbreviation VARCHAR(10) NOT NULL,
    city VARCHAR(100)
);

-- Players
CREATE TABLE IF NOT EXISTS players (
    id SERIAL PRIMARY KEY,
    nba_player_id INTEGER UNIQUE,
    full_name VARCHAR(100) NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    position VARCHAR(10),
    is_active BOOLEAN DEFAULT TRUE
);

-- Team season stats
CREATE TABLE IF NOT EXISTS team_season_stats (
    id SERIAL PRIMARY KEY,
    team_id INTEGER REFERENCES teams(id),
    season_id INTEGER REFERENCES seasons(id),
    wins INTEGER,
    losses INTEGER,
    win_pct NUMERIC(5,3),
    conf_rank INTEGER,
    UNIQUE(team_id, season_id)
);

-- Player season stats
CREATE TABLE IF NOT EXISTS player_season_stats (
    id SERIAL PRIMARY KEY,
    player_id INTEGER REFERENCES players(id),
    team_id INTEGER REFERENCES teams(id),
    season_id INTEGER REFERENCES seasons(id),
    games_played INTEGER,
    points_per_game NUMERIC(5,2),
    assists_per_game NUMERIC(5,2),
    rebounds_per_game NUMERIC(5,2),
    steals_per_game NUMERIC(5,2),
    blocks_per_game NUMERIC(5,2),
    fg_pct NUMERIC(5,3),
    fg3_pct NUMERIC(5,3),
    ft_pct NUMERIC(5,3),
    true_shooting_pct NUMERIC(5,3),
    usage_rate NUMERIC(5,2),
    per NUMERIC(6,2),
    win_shares NUMERIC(6,2),
    bpm NUMERIC(5,2),
    vorp NUMERIC(5,2),
    UNIQUE(player_id, season_id)
);

-- Award votes
CREATE TABLE IF NOT EXISTS award_votes (
    id SERIAL PRIMARY KEY,
    player_id INTEGER REFERENCES players(id),
    season_id INTEGER REFERENCES seasons(id),
    award_type VARCHAR(20) NOT NULL,  -- 'MVP', 'MIP', 'DPOY', 'ALL_NBA'
    first_place_votes INTEGER DEFAULT 0,
    total_points INTEGER DEFAULT 0,
    final_rank INTEGER,
    won BOOLEAN DEFAULT FALSE,
    UNIQUE(player_id, season_id, award_type)
);

-- Engineered features for ML models
CREATE TABLE IF NOT EXISTS player_season_features (
    id SERIAL PRIMARY KEY,
    player_id INTEGER REFERENCES players(id),
    season_id INTEGER REFERENCES seasons(id),

    -- Scoring & usage
    points_per_game NUMERIC(5,2),
    usage_rate NUMERIC(5,2),
    ts_pct NUMERIC(5,3),

    -- Team success
    team_win_pct NUMERIC(5,3),
    team_conf_rank INTEGER,

    -- Availability
    games_played INTEGER,
    games_played_pct NUMERIC(5,3),
    award_eligible BOOLEAN DEFAULT FALSE,

    -- League rankings (how dominant were they that season)
    ppg_rank INTEGER,
    apg_rank INTEGER,
    rpg_rank INTEGER,

    -- Year over year improvement
    ppg_improvement NUMERIC(5,2),
    apg_improvement NUMERIC(5,2),
    rpg_improvement NUMERIC(5,2),

    -- Efficiency
    per NUMERIC(6,2),
    win_shares NUMERIC(6,2),
    bpm NUMERIC(5,2),
    vorp NUMERIC(5,2),

    UNIQUE(player_id, season_id)
);