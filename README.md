# F1 Fantasy Solver

A solver that builds optimal [F1 Fantasy](https://fantasy.formula1.com) lineups from
real, historical scoring data. It pulls per-race driver and constructor results
straight from Formula 1's public fantasy feeds, models each pick by its
risk-adjusted scoring, and searches every valid combination to find the best
team(s) under your budget. Available as both a CLI and a Streamlit web app.

## How it works

A fantasy lineup is **5 drivers + 2 constructors** under a fixed budget, with one
driver chosen as a 2x point multiplier. Finding the best one is a constrained
knapsack problem, which the solver brute-forces over all combinations.

The pipeline has three stages:

1. **Fetch** ([src/fetch_results.py](Fantasy%20Knapsack%20Solver/src/fetch_results.py))
   downloads each race's JSON feed from
   `fantasy.formula1.com/feeds/drivers/{race}_en.json` into `data/`. Existing
   files are skipped, and empty/corrupt files are purged. The most recent fetched
   race is treated as a placeholder (upcoming round), so only completed races
   contribute scoring history; costs always use the latest values.

2. **Model** (same file) aggregates per-driver and per-constructor point history,
   current cost, and an **average DNF loss** — how many points each pick
   typically bleeds to DNQ/DNF events across qualifying, sprint, and race
   sessions.

3. **Solve** ([src/knapsack.py](Fantasy%20Knapsack%20Solver/src/knapsack.py))
   scores every budget-valid lineup and ranks them. Each pick is scored by its
   **risk-adjusted points**:

   ```
   risk_adjusted = average_points − (risk_penalty × std_dev)
   ```

   A higher `risk_penalty` punishes volatile, boom-or-bust picks. The solver also
   selects the best 2x driver per lineup and adds the bonus.

### Two-team mode

`find_best_two_team_lineups` returns lineup **pairs** for managers running two
entries. The first team is the top lineup outright; the second is re-scored to
penalize overlap with the first (you don't want both teams wiped out by the same
DNF), subtracting the shared picks' average DNF loss before re-ranking.

## Setup

Requires Python 3.11+.

```bash
cd "Fantasy Knapsack Solver"
pip install -r requirements.txt   # streamlit, pandas, altair
pip install requests              # used by the fetcher
```

All commands below are run from inside the `Fantasy Knapsack Solver` directory
(the `src` imports are relative to it). Race data is fetched automatically on
first run and cached in `data/` (git-ignored).

## Usage

### Web app (recommended)

```bash
streamlit run app.py
```

Set budget, risk penalty, number of lineup pairs, and any driver/constructor
exclusions in the sidebar, then click **Run Solver**. Results show the best
lineup pairs plus sortable driver and constructor model tables with charts.

### Command line

```bash
python fantasy_solver_cli.py [options]
```

| Flag | Default | Description |
|------|---------|-------------|
| `--budget` | `100.0` | Total budget for the lineup. |
| `--risk_penalty` | `0.5` | 0–1; higher penalizes volatile picks more. |
| `--top_n` | `3` | Number of best lineups to return. |
| `--exclude_drivers` | `[]` | Driver name(s) to exclude. |
| `--exclude_teams` | `[]` | Constructor name(s) to exclude. |
| `--verbosity` | `0` | `0` none, `1` basic, `2` detailed. |

Example:

```bash
python fantasy_solver_cli.py --budget 102.5 --risk_penalty 0.3 --top_n 5 \
  --exclude_drivers "Max Verstappen"
```

Exact names matter — if an excluded name isn't found, the solver prints the valid
options and exits.

## Project layout

```
Fantasy Knapsack Solver/
├── app.py                  # Streamlit web UI
├── fantasy_solver_cli.py   # CLI entry point
├── requirements.txt
├── src/
│   ├── fetch_results.py    # download + aggregate race feeds
│   ├── knapsack.py         # lineup scoring and search
│   └── console_display.py  # CLI result formatting
├── data/                   # fetched race JSON (git-ignored)
└── scratch/debug_dnf.py    # DNF statistics debugging script
```

## Notes

- The fetcher walks races 1–24; a `403` from the feed stops fetching (data not
  yet published for that round).
- Costs reflect the latest fetched round; scoring history excludes the latest
  (placeholder) round.
- This project is unofficial and not affiliated with Formula 1.
