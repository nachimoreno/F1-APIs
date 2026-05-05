import sys
import os

from src.fetch_results import get_driver_and_team_info

try:
    driver_info, team_info = get_driver_and_team_info()
    for d, info in driver_info.items():
        if info["avg_dnf_loss"] != 0:
            print(f"{d}: avg_dnf_loss = {info['avg_dnf_loss']}")
except Exception as e:
    print(f"Error: {e}")
