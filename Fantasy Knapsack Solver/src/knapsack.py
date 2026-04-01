from itertools import combinations
from math import sqrt
from pathlib import Path

from .fetch_results import get_driver_and_team_info

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def total_points(points_by_session, verbose=False):
    if verbose:
        print(f"DEBUG: total_points() called with {points_by_session}...")
    return sum(points_by_session)


def average_points(points_by_session, verbose=False):
    if verbose:
        print(f"DEBUG: average_points() called with {points_by_session}...")
    return sum(points_by_session) / len(points_by_session)


def standard_deviation(points_by_session, verbose=False):
    if verbose:
        print(f"DEBUG: standard_deviation() called with {points_by_session}...")
    mean_points = average_points(points_by_session, verbose=verbose)
    variance = sum((point - mean_points) ** 2 for point in points_by_session) / len(
        points_by_session
    )
    return sqrt(variance)


def risk_adjusted_points(points_by_session, risk_penalty, verbose=False):
    if verbose:
        print(f"DEBUG: risk_adjusted_points() called with {points_by_session}...")
    return average_points(
        points_by_session, verbose=verbose
    ) - risk_penalty * standard_deviation(points_by_session, verbose=verbose)


def best_2x_driver(selected_drivers, driver_info, risk_penalty, verbose=False):
    if verbose:
        print(
            f"DEBUG: best_2x_driver() called with:\n"
            f"Selected drivers: {selected_drivers}\n"
            f"Driver info: {driver_info}\n"
            f"Risk penalty: {risk_penalty}\n"
        )
    return max(
        selected_drivers,
        key=lambda driver_name: risk_adjusted_points(
            driver_info[driver_name]["points"], risk_penalty, verbose=verbose
        ),
    )


def _build_valid_lineups(
    excluded_drivers=None,
    excluded_teams=None,
    budget=100.0,
    risk_penalty=0.5,
    verbosity=0,
):
    driver_info, team_info = get_driver_and_team_info()

    if excluded_drivers:
        for excluded_driver in excluded_drivers:
            if excluded_driver in driver_info:
                del driver_info[excluded_driver]
            else:
                print(
                    f"exclude_drivers: Driver {excluded_driver} passed "
                    "into arguments but was not found in driver info."
                )
                print("Possible driver names include:")
                for driver_name in driver_info.keys():
                    print(f"  {driver_name}")
                print("\nExiting...")
                exit(1)

    if excluded_teams:
        for excluded_team in excluded_teams:
            if excluded_team in team_info:
                del team_info[excluded_team]
            else:
                print(
                    f"exclude_teams: Team {excluded_team} passed "
                    "into arguments but was not found in team info."
                )
                print("Possible team names include:")
                for team_name in team_info.keys():
                    print(f"  {team_name}")
                print("\nExiting...")
                exit(1)

    driver_info = dict(
        sorted(
            driver_info.items(),
            key=lambda x: total_points(x[1]["points"]),
            reverse=True,
        )
    )
    team_info = dict(
        sorted(
            team_info.items(),
            key=lambda x: total_points(x[1]["points"]),
            reverse=True,
        )
    )

    if verbosity > 0:
        print("DEBUG: _build_valid_lineups() produced:")
        print(f"  Driver info: {driver_info}")
        print(f"  Team info: {team_info}")

    valid_lineups = []

    driver_names = list(driver_info.keys())
    team_names = list(team_info.keys())

    for selected_drivers in combinations(driver_names, 5):
        driver_cost = sum(driver_info[driver]["cost"] for driver in selected_drivers)

        if driver_cost > budget:
            continue

        driver_total_points = sum(
            total_points(driver_info[driver]["points"], verbose=(verbosity > 1))
            for driver in selected_drivers
        )

        driver_risk_adjusted_score = sum(
            risk_adjusted_points(
                driver_info[driver]["points"], risk_penalty, verbose=(verbosity > 1)
            )
            for driver in selected_drivers
        )

        driver_average_points = sum(
            average_points(driver_info[driver]["points"], verbose=(verbosity > 1))
            for driver in selected_drivers
        )

        selected_2x_driver = best_2x_driver(selected_drivers, driver_info, risk_penalty)
        two_x_bonus = risk_adjusted_points(
            driver_info[selected_2x_driver]["points"],
            risk_penalty,
            verbose=(verbosity > 1),
        )

        two_x_bonus_clean = average_points(
            driver_info[selected_2x_driver]["points"], verbose=(verbosity > 1)
        )

        remaining_budget = budget - driver_cost

        for selected_teams in combinations(team_names, 2):
            team_cost = sum(team_info[team]["cost"] for team in selected_teams)

            if team_cost > remaining_budget:
                continue

            team_total_points = sum(
                total_points(team_info[team]["points"], verbose=(verbosity > 1))
                for team in selected_teams
            )

            team_risk_adjusted_score = sum(
                risk_adjusted_points(
                    team_info[team]["points"], risk_penalty, verbose=(verbosity > 1)
                )
                for team in selected_teams
            )

            team_average_points = sum(
                average_points(team_info[team]["points"], verbose=(verbosity > 1))
                for team in selected_teams
            )

            historical_total_points = driver_total_points + team_total_points
            lineup_risk_adjusted_score = (
                driver_risk_adjusted_score + team_risk_adjusted_score + two_x_bonus
            )
            projected_total_score = (
                driver_average_points + team_average_points + two_x_bonus_clean
            )
            total_cost = driver_cost + team_cost

            valid_lineups.append(
                {
                    "drivers": selected_drivers,
                    "teams": selected_teams,
                    "two_x_driver": selected_2x_driver,
                    "two_x_bonus": round(two_x_bonus, 2),
                    "historical_total_points": historical_total_points,
                    "lineup_risk_adjusted_score": round(lineup_risk_adjusted_score, 2),
                    "projected_total_score": round(projected_total_score, 2),
                    "total_cost": round(total_cost, 1),
                }
            )

    valid_lineups.sort(
        key=lambda lineup: (
            lineup["projected_total_score"],
            lineup["lineup_risk_adjusted_score"],
            lineup["historical_total_points"],
        ),
        reverse=True,
    )

    return driver_info, team_info, valid_lineups


def find_best_lineups(
    excluded_drivers=None,
    excluded_teams=None,
    budget=100.0,
    top_n=3,
    risk_penalty=0.5,
    verbosity=0,
):
    driver_info, team_info, valid_lineups = _build_valid_lineups(
        excluded_drivers=excluded_drivers,
        excluded_teams=excluded_teams,
        budget=budget,
        risk_penalty=risk_penalty,
        verbosity=verbosity,
    )
    return driver_info, team_info, valid_lineups[:top_n]


def _overlap_dnf_penalty(reference_lineup, candidate_lineup, driver_info, team_info):
    penalty = 0.0

    repeated_drivers = set(reference_lineup["drivers"]) & set(
        candidate_lineup["drivers"]
    )
    repeated_teams = set(reference_lineup["teams"]) & set(candidate_lineup["teams"])

    for driver_name in repeated_drivers:
        # avg_dnf_loss is stored as a negative number in fetch_results.py
        penalty += abs(driver_info[driver_name]["avg_dnf_loss"])

    for team_name in repeated_teams:
        # team avg_dnf_loss is also accumulated as a negative number
        penalty += abs(team_info[team_name]["avg_dnf_loss"])

    return penalty


def _build_second_lineup(reference_lineup, all_valid_lineups, driver_info, team_info):
    rescored_lineups = []

    for candidate_lineup in all_valid_lineups:
        overlap_penalty = _overlap_dnf_penalty(
            reference_lineup=reference_lineup,
            candidate_lineup=candidate_lineup,
            driver_info=driver_info,
            team_info=team_info,
        )

        adjusted_projected_total_score = (
            candidate_lineup["projected_total_score"] - overlap_penalty
        )

        rescored_lineups.append(
            {
                **candidate_lineup,
                "overlap_dnf_penalty": round(overlap_penalty, 2),
                "adjusted_projected_total_score": round(
                    adjusted_projected_total_score, 2
                ),
            }
        )

    rescored_lineups.sort(
        key=lambda lineup: (
            lineup["adjusted_projected_total_score"],
            lineup["lineup_risk_adjusted_score"],
            lineup["historical_total_points"],
        ),
        reverse=True,
    )

    return rescored_lineups[0]


def find_best_two_team_lineups(
    excluded_drivers=None,
    excluded_teams=None,
    budget=100.0,
    top_n=3,
    risk_penalty=0.5,
    verbosity=0,
):
    driver_info, team_info, first_lineups = find_best_lineups(
        excluded_drivers=excluded_drivers,
        excluded_teams=excluded_teams,
        budget=budget,
        top_n=top_n,
        risk_penalty=risk_penalty,
        verbosity=verbosity,
    )

    _, _, all_valid_lineups = _build_valid_lineups(
        excluded_drivers=excluded_drivers,
        excluded_teams=excluded_teams,
        budget=budget,
        risk_penalty=risk_penalty,
        verbosity=verbosity,
    )

    second_lineups = []

    for first_lineup in first_lineups:
        second_lineup = _build_second_lineup(
            reference_lineup=first_lineup,
            all_valid_lineups=all_valid_lineups,
            driver_info=driver_info,
            team_info=team_info,
        )
        second_lineups.append(second_lineup)

    return driver_info, team_info, first_lineups, second_lineups
