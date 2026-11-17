import argparse
import time
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parent.parent
GAME_IDS_FILE = ROOT / "data" / "raw" / "game_ids.csv"
OUTPUT = ROOT / "data" / "raw" / "games_data.csv"
URL = "https://store.steampowered.com/api/appdetails"


def get_game(appid):
    for attempt in range(4):
        response = requests.get(URL, params={"appids": appid, "cc": "us", "l": "english"}, timeout=20)
        if response.status_code in (403, 429):
            wait = 30 * (attempt + 1)
            print(f"  Waiting {wait} seconds due to rate limit")
            time.sleep(wait)
            continue
        response.raise_for_status()
        entry = response.json().get(str(appid), {})
        if not entry.get("success"):
            return None
        data = entry["data"]
        pricing = data.get("price_overview")
        # Missing price is unknown, NOT proof a game is free.
        is_free = data.get("is_free", False)
        initial = pricing.get("initial") / 100 if pricing and pricing.get("initial") is not None else (0 if is_free else None)
        final = pricing.get("final") / 100 if pricing and pricing.get("final") is not None else (0 if is_free else None)
        return {
            "appid": data.get("steam_appid", appid),
            "type": data.get("type"), "name": data.get("name"),
            "genres": "; ".join(g.get("description", "") for g in data.get("genres", [])),
            "categories": "; ".join(c.get("description", "") for c in data.get("categories", [])),
            "initial_price": initial,
            "final_price": final,
            "is_free": is_free,
            "release_date": (data.get("release_date") or {}).get("date"),
            "description": data.get("short_description"),
        }
    raise RuntimeError("Store API rate limit did not clear")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true", help="Update the existing snapshot")
    args = parser.parse_args()
    if OUTPUT.exists() and not args.refresh:
        print(f"Keeping existing file {OUTPUT}. Use --refresh to collect again.")
        return
    ids = pd.read_csv(GAME_IDS_FILE)["appid"].tolist()
    # If refresh, keep existing rows if an individual request fails.
    previous = {}
    if OUTPUT.exists():
        previous = {int(row["appid"]): row for row in pd.read_csv(OUTPUT).to_dict("records")}
    rows = []
    for index, appid in enumerate(ids, start=1):
        try:
            row = get_game(int(appid))
        except (requests.RequestException, RuntimeError, ValueError) as error:
            print(f"Request failed for {appid}: {error}")
            row = None
        row = row or previous.get(int(appid))
        if row is not None:
            rows.append(row)
        print(f"{index}/{len(ids)}: {appid}")
        time.sleep(1.2)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUTPUT, index=False)
    print(f"Saved {len(rows)} rows to {OUTPUT}")


if __name__ == "__main__":
    main()
