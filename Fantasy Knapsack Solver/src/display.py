from .knapsack import total_points, average_points, standard_deviation, risk_adjusted_points
import time

def display_results(driver_info, team_info, best_lineups, risk_penalty, verbose=False):
    if verbose:
        print("DEBUG: display_results() called with:")
        print(f"  Best lineups: {best_lineups}")

    for lineup_index, lineup in enumerate(best_lineups, start=1):
        print("\n================================================================")
        print(f"Lineup #{lineup_index}:\n")
        print("Drivers:")
        for driver in lineup["drivers"]:
            driver_total_points = total_points(driver_info[driver]["points"])
            driver_average_points = average_points(driver_info[driver]["points"])
            driver_standard_deviation = standard_deviation(driver_info[driver]["points"])
            driver_risk_adjusted_score = risk_adjusted_points(
                driver_info[driver]["points"],
                risk_penalty
            )
            print(
                f"  - {driver} "
                f"(cost={driver_info[driver]['cost']}, "
                f"total_points={driver_total_points}, "
                f"avg_points={driver_average_points:.2f}, "
                f"std_dev={driver_standard_deviation:.2f}, "
                f"risk_adjusted={driver_risk_adjusted_score:.2f})"
            )

        print("\nTeams:")
        for team in lineup["teams"]:
            team_total_points = total_points(team_info[team]["points"])
            team_average_points = average_points(team_info[team]["points"])
            team_standard_deviation = standard_deviation(team_info[team]["points"])
            team_risk_adjusted_score = risk_adjusted_points(
                team_info[team]["points"],
                risk_penalty
            )
            print(
                f"  - {team} "
                f"(cost={team_info[team]['cost']}, "
                f"points={team_total_points}, "
                f"avg_points={team_average_points:.2f}, "
                f"std_dev={team_standard_deviation:.2f}, "
                f"risk_adjusted={team_risk_adjusted_score:.2f})"
            )

        print(f"\nSuggested 2x driver: {lineup['two_x_driver']}")
        print(f"Expected 2x bonus: {lineup['two_x_bonus']}")
        print(f"Historical total points: {lineup['historical_total_points']}")
        print(f"Lineup risk-adjusted score: {lineup['lineup_risk_adjusted_score']}")
        print(f"Projected total score: {lineup['projected_total_score']}")
        print(f"Total cost: {lineup['total_cost']}")
        print("================================================================\n")
        time.sleep(0.4)
