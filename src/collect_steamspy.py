
import requests
import json
import csv
import os
import random
import time

API_URL = "https://steamspy.com/api.php"
FOLDER = "data/raw"
IDS_FILE = "data/raw/game_ids.csv"
RAW_FILE = "data/raw/steamspy_raw.json"

os.makedirs(FOLDER, exist_ok=True)


def get_data(parameters):
    try:
        response = requests.get(API_URL, params=parameters, timeout=30)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError) as error:
        print("API error:", error)
        return None


def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def collect_ids():
    if os.path.exists(IDS_FILE):
        print("game_ids.csv already exists. Keeping the same IDs for your team.")
        return

    pages = [0, 10, 30]          
    amounts = [67, 67, 66]      
    random.seed(42)         
    selected = []    
    downloads = 0

    for i in range(len(pages)):
        page = pages[i]
        filename = f"{FOLDER}/steamspy_page_{page}.json"

        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as file:
                games = json.load(file)
        else:
            if downloads > 0:
                time.sleep(61)  

            print("Downloading catalog page", page)
            games = get_data({"request": "all", "page": page})
            if games is None:
                return
            save_json(filename, games)
            downloads += 1

        if not isinstance(games, dict) or not games:
            print("Invalid/empty catalog page:", page)
            return

        sample = random.sample(list(games.values()), min(amounts[i], len(games)))
        for game in sample:
            if isinstance(game, dict) and game.get("appid") and game.get("name"):
                selected.append([game["appid"], game["name"], page])

    with open(IDS_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["appid", "name", "source_page"])
        writer.writerows(selected)

    print("Saved", len(selected), "game IDs to", IDS_FILE)


def collect_details():
    if not os.path.exists(IDS_FILE):
        print("Run 'ids' first.")
        return

    with open(IDS_FILE, "r", encoding="utf-8") as file:
        ids = [row["appid"] for row in csv.DictReader(file)]

    if os.path.exists(RAW_FILE):
        with open(RAW_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
    else:
        data = {"source": "SteamSpy appdetails", "records": {}}

    for appid in ids:
        if appid in data["records"]:
            continue  

        print("Collecting details for", appid)
        game = get_data({"request": "appdetails", "appid": appid})
        if game is None:
            print("Stopped. Run 'details' again later to resume.")
            break
        if not isinstance(game, dict) or not game.get("appid"):
            print("No valid details for", appid)
            time.sleep(1.2)
            continue

        data["records"][appid] = game
        save_json(RAW_FILE, data)  
        time.sleep(1.2)          

    print("Saved", len(data["records"]), "game details to", RAW_FILE)


choice = input("Type test, ids, or details: ").strip().lower()

if choice == "test":
    game = get_data({"request": "appdetails", "appid": 620})
    if game:
        print("API works! Game:", game.get("name"))
elif choice == "ids":
    collect_ids()
elif choice == "details":
    collect_details()
else:
    print("Please enter: test, ids, or details")
