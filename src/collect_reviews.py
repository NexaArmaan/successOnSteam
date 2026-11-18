
import argparse
import csv
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parent.parent
IDS = ROOT / "data" / "raw" / "game_ids.csv"
OUTPUT = ROOT / "data" / "raw" / "steam_reviews_summary.csv"
API_URL = "https://api.steampowered.com/IUserReviewsService/GetAppReviews/v1/"


def get_summary(appid):
    parameters = {
        "appid": int(appid),
        "filter": 1,
        "languages": ["all"],
        "review_type": 0,
        "purchase_type": 1,
        "num_per_page": 1
    }

    response = requests.get(
        API_URL,
        params={"input_json": json.dumps(parameters)},
        timeout=30
    )
    response.raise_for_status()

    summary = response.json().get("response", {}).get("query_summary", {})

    if "total_positive" not in summary:
        raise ValueError("Missing review summary")

    positives = int(summary["total_positive"])
    negatives = int(summary["total_negative"])
    total = positives + negatives

    return {
        "appid": appid,
        "review_score": summary.get("review_score"),
        "review_score_desc": summary.get("review_score_desc"),
        "total_positive": positives,
        "total_negative": negatives,
        "total_reviews": int(summary.get("total_reviews", total)),
        "positive_percentage": round(100 * positives / total, 2) if total else None,
        "collected_at": datetime.now(timezone.utc).isoformat()
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()

    if OUTPUT.exists() and not args.refresh:
        print(f"Keeping existing snapshot {OUTPUT}. Use --refresh to recollect.")
        return

    appids = pd.read_csv(IDS)["appid"].astype(int).tolist()

    # Preserve existing summaries if a future refresh fails.
    previous = (
        {
            int(row["appid"]): row
            for row in pd.read_csv(OUTPUT).to_dict("records")
        }
        if OUTPUT.exists()
        else {}
    )

    rows = []

    for i, appid in enumerate(appids, start=1):
        try:
            row = get_summary(appid)
        except (requests.RequestException, ValueError) as error:
            print(f"Could not collect {appid}: {error}")
            row = previous.get(appid)

        if row:
            rows.append(row)

        print(f"{i}/{len(appids)}: {appid}")
        time.sleep(1.2)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT.open("w", newline="", encoding="utf-8") as file:
        cols = [
            "appid",
            "review_score",
            "review_score_desc",
            "total_positive",
            "total_negative",
            "total_reviews",
            "positive_percentage",
            "collected_at"
        ]

        writer = csv.DictWriter(file, fieldnames=cols)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved {len(rows)} summaries to {OUTPUT}")


if __name__ == "__main__":
    main()
