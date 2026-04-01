import json
import os
from pathlib import Path

import requests

LOCAL_ROOT = Path(__file__).parent.parent
DATA_DIR = LOCAL_ROOT / "data"


class RaceFetchForbiddenError(Exception):
    pass


def fetch_and_save_race(race_number):
    os.makedirs(DATA_DIR, exist_ok=True)

    output_path = DATA_DIR / f"drivers_{race_number}_en.json"
    if output_path.exists():
        print(f"  Race {race_number}: File already exists, skipping.")
        return

    url = f"https://fantasy.formula1.com/feeds/drivers/{race_number}_en.json"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

    except requests.exceptions.HTTPError as error:
        if error.response is not None and error.response.status_code == 403:
            raise RaceFetchForbiddenError(f"Race {race_number}: got 403") from error
        print(f"  Race {race_number}: HTTP error fetching data: {error}")
        return

    except requests.exceptions.RequestException as error:
        print(f"  Race {race_number}: Error fetching data: {error}")
        return

    data = response.json()

    with output_path.open("w", encoding="utf-8") as output_file:
        json.dump(data, output_file, ensure_ascii=False, indent=2)

    print(f"  Race {race_number}: Saved JSON to {output_path.resolve()}")


def fetch_and_save_all_races_up_to(race_number):
    print(f"Fetching and saving all races up to race number {race_number}\n")
    for race_num in range(1, race_number + 1):
        try:
            fetch_and_save_race(race_num)
        except RaceFetchForbiddenError:
            print(f"  Race {race_num}: Forbidden, stopping fetching.")
            break
    print("\nDone!\n")


def get_driver_and_team_info(verbose=False):
    if verbose:
        print("Getting driver and team info...")

    driver_info = {}
    team_info = {}

    # Set up driver info dictionary with driver names as keys
    # and cost and points as values
    with open(DATA_DIR / "drivers_1_en.json", encoding="utf-8") as file:
        if verbose:
            print("Building dictionaries...")

        data = json.load(file)

        for player in data["Data"]["Value"]:
            if player["PositionName"] == "DRIVER":
                driver_name = player["FUllName"]
                driver_info[driver_name] = {
                    "points": [],
                    "dnq": [],
                    "dnf_sprint": [],
                    "dnf_race": [],
                    "cost": 0,
                    "team": "",
                }

            if player["PositionName"] == "CONSTRUCTOR":
                driver_team = player["FUllName"]
                team_info[driver_team] = {
                    "points": [],
                    "cost": 0,
                    "avg_dnf_loss": 0,
                }

    # Add value, points, dnfs, and dnqs to driver info dictionary
    num_fetched_races = len(list(DATA_DIR.glob("drivers_*.json")))
    count_race = 0
    for file_path in DATA_DIR.glob("drivers_*.json"):
        if verbose:
            print(f"Processing {file_path}...")

        with open(file_path, encoding="utf-8") as file:
            data = json.load(file)
            count_race += 1

            for player in data["Data"]["Value"]:
                if player["PositionName"] == "DRIVER":
                    driver_name = player["FUllName"]
                    driver_info[driver_name]["team"] = player["TeamName"]
                    # Last fetched race is placeholder, therefore get results
                    # only from previous races
                    if count_race != num_fetched_races:
                        driver_info[driver_name]["points"].append(
                            float(player["GamedayPoints"])
                        )
                        # DNF logic
                        for session in player["SessionWisePoints"]:
                            session_points_diff = (
                                session["points"] - session["nonegative_points"]
                            )
                            if (
                                session["sessiontype"] == "Qualifying"
                                and session_points_diff <= -5
                            ):
                                driver_info[driver_name]["dnq"].append(-5)
                            else:
                                driver_info[driver_name]["dnq"].append(0)
                            if (
                                session["sessiontype"] == "Sprint Qualifying"
                                and session_points_diff <= -10
                            ):
                                driver_info[driver_name]["dnf_sprint"].append(-10)
                            else:
                                driver_info[driver_name]["dnf_sprint"].append(0)
                            if (
                                session["sessiontype"] == "Race"
                                and session_points_diff <= -20
                            ):
                                driver_info[driver_name]["dnf_race"].append(-20)
                            else:
                                driver_info[driver_name]["dnf_race"].append(0)

                    # Except cost, which we always want the latest
                    driver_info[driver_name]["cost"] = float(player["Value"])

                if player["PositionName"] == "CONSTRUCTOR":
                    driver_team = player["FUllName"]
                    # Last fetched race is placeholder, therefore get results
                    # only from previous races
                    if count_race != num_fetched_races:
                        team_info[driver_team]["points"].append(
                            float(player["GamedayPoints"])
                        )
                    # Except cost, which we always want the latest
                    team_info[driver_team]["cost"] = float(player["Value"])

    # Calculate average points loss to DNFs for each driver and team
    for driver_name in driver_info:
        driver_info[driver_name]["avg_dnf_loss"] = (
            sum(driver_info[driver_name]["dnq"])
            + sum(driver_info[driver_name]["dnf_sprint"])
            + sum(driver_info[driver_name]["dnf_race"])
        ) / len(driver_info[driver_name]["points"])
        driver_team = driver_info[driver_name]["team"]
        team_info[driver_team]["avg_dnf_loss"] += driver_info[driver_name][
            "avg_dnf_loss"
        ]

    return driver_info, team_info
