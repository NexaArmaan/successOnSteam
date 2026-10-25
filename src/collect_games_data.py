import json
import os
from pprint import pprint
from pathlib import Path

import pandas as pd
import time
import requests

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GAME_IDS_FILE = PROJECT_ROOT / "data" / "raw" / "game_ids.csv"
GAMES_DATA_FILE = PROJECT_ROOT / "data" / "raw" / "games_data.csv"

API_KEY = os.getenv("API_KEY")

steam_url = "https://steampowered.com/api/appdetails"

with open(GAME_IDS_FILE) as f:
    game_ids = pd.read_csv(f)['appid'].to_list()



rows = []
id_count = 0

# App Id, genres, categories, price, release data, description
for appid in game_ids:
    while True:
        r = requests.get(
            "https://store.steampowered.com/api/appdetails",
            params={"appids": appid, "cc": "us", "l": "english"},
            timeout=15,
        )

        if r.status_code in (403, 429):  # throttled: wait and retry the same ID
            print("  rate limited, waiting 60 s")
            time.sleep(60)
            continue
        r.raise_for_status()
        break

    entry = r.json().get(str(appid), {}) # .get() in case of bad request
    if not entry.get('success'):
        continue
    data = entry["data"]
    rows.append({
        'appid': data['steam_appid'],
        'genres': "; ".join(g['description'] for g in data.get('genres', [])), 
        'categories': "; ".join(c['description'] for c in data.get('categories', [])),
        'price': data.get('price_overview', {}).get('final', 0),
        'release_date': data['release_date']['date'],
        'description': data['short_description'],
    })

    print(f"current item: ( {id_count} / {len(game_ids)} )")
    id_count += 1

    time.sleep(1.6) # to stay under rate limit

df = pd.DataFrame(rows)

df.to_csv(GAMES_DATA_FILE)

print(rows)