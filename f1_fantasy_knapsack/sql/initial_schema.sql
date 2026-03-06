PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS teams (
  team_id     INTEGER PRIMARY KEY,
  canonical   TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS team_aliases (
  alias_id INTEGER PRIMARY KEY,
  team_id  INTEGER NOT NULL,
  alias    TEXT NOT NULL,
  UNIQUE(team_id, alias),
  UNIQUE(alias),
  FOREIGN KEY(team_id) REFERENCES teams(team_id)
);

CREATE TABLE IF NOT EXISTS seasons (
  year        INTEGER PRIMARY KEY,
  num_rounds  INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS events (
  year         INTEGER NOT NULL,
  round_number INTEGER NOT NULL,
  PRIMARY KEY (year, round_number),
  FOREIGN KEY(year) REFERENCES seasons(year)
);

CREATE TABLE IF NOT EXISTS session_points_history (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  year         INTEGER NOT NULL,
  round_number INTEGER NOT NULL,
  team_id      INTEGER NOT NULL,
  points       REAL NOT NULL,
  recorded_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  UNIQUE(year, round_number, team_id),
  FOREIGN KEY(year, round_number) REFERENCES events(year, round_number),
  FOREIGN KEY(team_id) REFERENCES teams(team_id)
);

CREATE INDEX IF NOT EXISTS idx_sph_lookup
ON session_points_history(year, round_number, team_id, recorded_at);