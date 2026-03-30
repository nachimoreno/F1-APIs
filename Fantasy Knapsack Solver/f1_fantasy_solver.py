import argparse
from src.fetch_results import fetch_and_save_all_races_up_to
from src.knapsack import find_best_lineups
from src.display import display_results

def main():
    parser = argparse.ArgumentParser(description="Find the best F1 fantasy lineups.")
    parser.add_argument("--budget", type=float, default=100.0, help="Budget for the lineup.")
    parser.add_argument("--risk_penalty", type=float, default=0.5, help="Risk penalty for the lineup.")
    parser.add_argument("--top_n", type=int, default=3, help="Number of best lineups to return.")
    parser.add_argument("--exclude_drivers", nargs="*", default=[], help="Driver to exclude from the lineup.")
    parser.add_argument("--exclude_teams", nargs="*", default=[], help="Team to exclude from the lineup.")
    parser.add_argument("--verbosity", type=int, default=0, help="Enable verbose output.")
    args = parser.parse_args()

    print("\nStarting F1 Fantasy Solver...\n")
    print("Loading data...\n")

    fetch_and_save_all_races_up_to(24)
    print("Data loaded successfully!\n")

    print("Finding best lineups...\n")
    driver_info, team_info, best_lineups = find_best_lineups(
        args.exclude_drivers,
        args.exclude_teams,
        args.budget,
        top_n=args.top_n,
        risk_penalty=args.risk_penalty,
        verbosity=args.verbosity
    )
    print("Best lineups found successfully!\n")

    print("Displaying best lineups...\n")
    display_results(
        driver_info,
        team_info,
        best_lineups,
        args.risk_penalty,
        verbose=(args.verbosity == 1)
    )
    print("Done!\n")

if __name__ == "__main__":
    main()