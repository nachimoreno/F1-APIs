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
                    "cost": 0,
                }

            if player["PositionName"] == "CONSTRUCTOR":
                driver_team = player["FUllName"]
                team_info[driver_team] = {
                    "points": [],
                    "cost": 0,
                }

    # Add points to driver info dictionary
    for file_path in DATA_DIR.glob("drivers_*.json"):
        if verbose:
            print(f"Processing {file_path}...")

        with open(file_path, encoding="utf-8") as file:
            data = json.load(file)

            for player in data["Data"]["Value"]:
                if player["PositionName"] == "DRIVER":
                    driver_name = player["FUllName"]
                    driver_info[driver_name]["points"].append(
                        float(player["GamedayPoints"])
                    )
                    driver_info[driver_name]["cost"] = float(player["Value"])

                if player["PositionName"] == "CONSTRUCTOR":
                    driver_team = player["FUllName"]
                    team_info[driver_team]["points"].append(
                        float(player["GamedayPoints"])
                    )
                    team_info[driver_team]["cost"] = float(player["Value"])

    return driver_info, team_info
