
import csv
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

API_URL = (
    "https://api.steampowered.com/"
    "IUserReviewsService/GetAppReviews/v1/"
)

BASE_DIR = Path(__file__).resolve().parent
APP_IDS_FILE = BASE_DIR / "app_ids.txt"
OUTPUT_FILE = BASE_DIR / "data" / "steam_reviews_summary.csv"


def collect_reviews(app_id):
    input_data = {
        "appid": int(app_id),
        "filter": 1,
        "languages": ["all"],
        "review_type": 0,
        "purchase_type": 1,
        "num_per_page": 20,
    }

    response = requests.get(
        API_URL,
        params={"input_json": json.dumps(input_data)},
        timeout=30,
    )
    response.raise_for_status()

    result = response.json().get("response", {})
    summary = result.get("query_summary")

    if not summary or "total_positive" not in summary:
        raise ValueError(
            "Steam did not return review summary data. "
            f"Response: {response.text[:500]}"
        )

    positive = int(summary["total_positive"])
    negative = int(summary["total_negative"])
    total = int(summary["total_reviews"])

    denominator = positive + negative
    percentage = (
        round(positive / denominator * 100, 2)
        if denominator else None
    )

    return {
        "appid": app_id,
        "review_score": summary.get("review_score", ""),
        "review_score_desc": summary.get("review_score_desc", ""),
        "total_positive": positive,
        "total_negative": negative,
        "total_reviews": total,
        "positive_percentage": percentage,
        "collected_at": datetime.now(timezone.utc).isoformat(),
    }


def main():
    with APP_IDS_FILE.open("r", encoding="utf-8") as file:
        app_ids = [
            line.strip()
            for line in file
            if line.strip() and not line.strip().startswith("#")
        ]

    if not app_ids:
        print("No App IDs found in app_ids.txt")
        return

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    columns = [
        "appid",
        "review_score",
        "review_score_desc",
        "total_positive",
        "total_negative",
        "total_reviews",
        "positive_percentage",
        "collected_at",
    ]

    rows = []

    for app_id in app_ids:
        try:
            print(f"Collecting App ID {app_id}...")
            row = collect_reviews(app_id)
            rows.append(row)

            print(
                f"  Rating: {row['review_score_desc']}\n"
                f"  Positive: {row['total_positive']:,}\n"
                f"  Negative: {row['total_negative']:,}\n"
                f"  Total: {row['total_reviews']:,}"
            )

        except (requests.RequestException, ValueError, KeyError) as error:
            print(f"  Could not collect App ID {app_id}: {error}")

        time.sleep(1)

    with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nSaved {len(rows)} game summaries to:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()
