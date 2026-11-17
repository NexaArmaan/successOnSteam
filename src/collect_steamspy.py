import argparse
import csv
import json
import random
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
IDS_FILE = RAW / "game_ids.csv"
DETAILS_FILE = RAW / "steamspy_raw.json"
API_URL = "https://steamspy.com/api.php"
RAW.mkdir(parents=True, exist_ok=True)


def get_data(params):
    try:
        response = requests.get(API_URL, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError) as error:
        print("API error:", error)
        return None


def save_json(path, data):
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def collect_ids():
    if IDS_FILE.exists():
        print("Keeping the existing 200 game IDs. File:", IDS_FILE)
        return
    random.seed(42)
    selected = []
    downloads = 0
    for page, amount in [(0, 67), (10, 67), (30, 66)]:
        file = RAW / f"steamspy_page_{page}.json"
        if file.exists():
            with file.open(encoding="utf-8") as f:
                games = json.load(f)
        else:
            if downloads:
                time.sleep(61)
            games = get_data({"request": "all", "page": page})
            if not games:
                return
            save_json(file, games)
            downloads += 1
        sample = random.sample(list(games.values()), min(amount, len(games)))
        for game in sample:
            if isinstance(game, dict) and game.get("appid") and game.get("name"):
                selected.append([game["appid"], game["name"], page])
    with IDS_FILE.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["appid", "name", "source_page"])
        writer.writerows(selected)
    print(f"Saved {len(selected)} game IDs to {IDS_FILE}")


def collect_details():
    if not IDS_FILE.exists():
        print("Run with ids first")
        return
    with IDS_FILE.open(encoding="utf-8") as file:
        appids = [row["appid"] for row in csv.DictReader(file)]
    if DETAILS_FILE.exists():
        with DETAILS_FILE.open(encoding="utf-8") as file:
            data = json.load(file)
    else:
        data = {"source": "SteamSpy appdetails", "records": {}}
    for appid in appids:
        if appid in data["records"]:
            continue
        game = get_data({"request": "appdetails", "appid": appid})
        if game is None:
            print("Stopping after API error, rerun to resume")
            break
        if isinstance(game, dict) and game.get("appid"):
            data["records"][appid] = game
            save_json(DETAILS_FILE, data)
        time.sleep(1.2)
    print(f"Saved {len(data['records'])} game details to {DETAILS_FILE}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("task", choices=["test", "ids", "details"], nargs="?")
    args = parser.parse_args()
    task = args.task or input("Type test, ids, or details: ").strip().lower()
    if task == "test":
        result = get_data({"request": "appdetails", "appid": 620})
        print(result.get("name") if result else "API test failed")
    elif task == "ids":
        collect_ids()
    elif task == "details":
        collect_details()
    else:
        print("Choose test, ids, or details")


if __name__ == "__main__":
    main()
