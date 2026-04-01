import json
from pathlib import Path
import requests
import os

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
    for race_number in range(1, race_number + 1):
        try:
            fetch_and_save_race(race_number)
        except RaceFetchForbiddenError:
            print(f"  Race {race_number}: Forbidden, stopping fetching.")
            break
    print("\nDone!\n")