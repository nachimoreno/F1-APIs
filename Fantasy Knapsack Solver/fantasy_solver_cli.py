import argparse

from src.console_display import display_results
from src.fetch_results import fetch_and_save_all_races_up_to
from src.knapsack import find_best_lineups


def main():
    parser = argparse.ArgumentParser(description="Find the best F1 fantasy lineups.")
    parser.add_argument(
        "--budget",
        type=float,
        default=100.0,
        help="Budget available for the lineup.",
    )
    parser.add_argument(
        "--risk_penalty",
        type=float,
        default=0.5,
        help="Risk penalty for the lineup. Value between 0 and 1. "
        "Higher values penalize riskier drivers more.",
    )
    parser.add_argument(
        "--top_n",
        type=int,
        default=3,
        help="Number of best lineups to return.",
    )
    parser.add_argument(
        "--exclude_drivers",
        nargs="*",
        default=[],
        help="Driver(s) to exclude from the lineup.",
    )
    parser.add_argument(
        "--exclude_teams",
        nargs="*",
        default=[],
        help="Team(s) to exclude from the lineup.",
    )
    parser.add_argument(
        "--verbosity",
        type=int,
        default=0,
        help="Enable verbose output. "
        "0 = No output, 1 = Basic output, 2 = Detailed output.",
    )
    args = parser.parse_args()

    print("\nStarting F1 Fantasy Solver...\n")
    print("Loading data from fantasy.formula1.com ...\n")

    fetch_and_save_all_races_up_to(24)
    print("Data loaded successfully!\n")

    print("Finding best lineups...\n")
    driver_info, team_info, best_lineups = find_best_lineups(
        args.exclude_drivers,
        args.exclude_teams,
        args.budget,
        top_n=args.top_n,
        risk_penalty=args.risk_penalty,
        verbosity=args.verbosity,
    )
    print("Best lineups found successfully!\n")

    print("Displaying best lineups...\n")
    display_results(
        driver_info,
        team_info,
        best_lineups,
        args.risk_penalty,
        verbose=(args.verbosity == 1),
    )
    print("Done!\n")


if __name__ == "__main__":
    main()
