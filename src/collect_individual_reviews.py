import argparse
import csv
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
SELECTED_IDS = RAW / "selected_game_ids.csv"
REVIEW_DIR = RAW / "reviews" / "by_app"
OUTPUT = RAW / "individual_reviews.csv"
PROGRESS = RAW / "reviews" / "collection_progress.json"
API_URL = "https://api.steampowered.com/IUserReviewsService/GetAppReviews/v1/"

COLUMNS = [
    "appid", "recommendationid", "playtime_at_review_min",
    "playtime_forever_min", "voted_up", "review_text", "language",
    "timestamp_created", "timestamp_updated", "written_during_early_access",
    "steam_purchase", "received_for_free", "refunded", "collected_at"
]


def request_page(appid, cursor, count, language="english"):
    """Request one page, retrying a limited number of times on rate limiting."""
    inputs = {
        "appid": int(appid),
        "filter": 1,              # Recent reviews; 0 (Helpful) isn't a chronological sample
        "languages": [language],  # English for comparable text analysis
        "review_type": 0,        # Both positive and negative reviews
        "purchase_type": 1,      # All purchase types
        "num_per_page": min(count, 100),
        "cursor": cursor,
    }
    for attempt in range(4):
        response = requests.get(
            API_URL,
            params={"input_json": json.dumps(inputs)},
            timeout=30,
        )
        if response.status_code == 429:
            wait = 30 * (attempt + 1)
            print(f"    Rate limited; retrying in {wait} seconds")
            time.sleep(wait)
            continue
        response.raise_for_status()
        data = response.json()
        if not isinstance(data.get("response"), dict):
            raise ValueError(f"Unexpected response for {appid}: {str(data)[:250]}")
        return data["response"]
    raise RuntimeError("Steam still returned HTTP 429 after four attempts")


def extract_review(appid, review):
    """Keep API fields raw; data cleaning is handled by another teammate."""
    author = review.get("author") or {}
    return {
        "appid": int(appid),
        "recommendationid": review.get("recommendationid"),
        "playtime_at_review_min": author.get("playtime_at_review"),
        "playtime_forever_min": author.get("playtime_forever"),
        "voted_up": review.get("voted_up"),
        "review_text": review.get("review", ""),
        "language": review.get("language"),
        "timestamp_created": review.get("timestamp_created"),
        "timestamp_updated": review.get("timestamp_updated"),
        "written_during_early_access": review.get("written_during_early_access"),
        "steam_purchase": review.get("steam_purchase"),
        "received_for_free": review.get("received_for_free"),
        "refunded": review.get("refunded"),
        "collected_at": datetime.now(timezone.utc).isoformat(),
    }


def collect_game(appid, max_reviews, pause_seconds):
    """Read up to max_reviews recent reviews for one game."""
    collected = []
    seen_ids = set()
    cursor = "*"
    while len(collected) < max_reviews:
        batch = request_page(appid, cursor, max_reviews - len(collected))
        items = batch.get("reviews") or []
        if not items:
            break

        for review in items:
            review_id = str(review.get("recommendationid", ""))
            if not review_id or review_id in seen_ids:
                continue
            seen_ids.add(review_id)
            collected.append(extract_review(appid, review))
            if len(collected) >= max_reviews:
                break

        next_cursor = batch.get("cursor")
        if not next_cursor or next_cursor == cursor:
            break
        cursor = next_cursor
        if len(collected) < max_reviews:
            time.sleep(pause_seconds)
    return collected


def save_rows(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def combine_saved_files():
    """Regenerate combined CSV from successful per-app files (no duplicates)."""
    paths = sorted(REVIEW_DIR.glob("*.csv"))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with OUTPUT.open("w", newline="", encoding="utf-8-sig") as destination:
        writer = csv.DictWriter(destination, fieldnames=COLUMNS)
        writer.writeheader()
        for path in paths:
            with path.open("r", newline="", encoding="utf-8-sig") as source:
                for row in csv.DictReader(source):
                    writer.writerow(row)
                    count += 1
    return count


def main():
    parser = argparse.ArgumentParser(description="Download individual Steam reviews")
    parser.add_argument("--limit-games", type=int, default=None,
                        help="Pilot only: number of games from selected_game_ids.csv")
    parser.add_argument("--reviews-per-game", type=int, default=300,
                        help="Maximum reviews per game (default: 300)")
    parser.add_argument("--pause", type=float, default=1.5,
                        help="Seconds between API pages/games (default: 1.5)")
    args = parser.parse_args()
    if args.reviews_per_game <= 0 or args.limit_games == 0 or args.pause < 0:
        parser.error("Review count and game limit must be positive, pause nonnegative")
    if not SELECTED_IDS.exists():
        parser.error("Missing data/raw/selected_game_ids.csv. Run select_games.py first")

    selected = pd.read_csv(SELECTED_IDS)
    if selected.empty or "appid" not in selected:
        parser.error("Selected game file must contain an appid column and at least one game")
    if args.limit_games is not None:
        if args.limit_games < 0:
            parser.error("--limit-games must be positive")
        selected = selected.head(args.limit_games)

    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    PROGRESS.parent.mkdir(parents=True, exist_ok=True)
    if PROGRESS.exists():
        with PROGRESS.open(encoding="utf-8") as f:
            progress = json.load(f)
    else:
        progress = {"language": "english", "filter": "recent", "apps": {}}
    if progress.get("language") != "english" or progress.get("filter") != "recent":
        parser.error("Progress file is for another sampling configuration")

    try:
        for appid in selected["appid"].dropna().astype(int).unique():
            appid = int(appid)
            out_path = REVIEW_DIR / f"{appid}.csv"
            prior = progress["apps"].get(str(appid), {})
            if out_path.exists() and prior.get("requested_reviews", 0) >= args.reviews_per_game:
                print(f"Skipping {appid}: already collected for this target")
                continue
            try:
                print(f"Collecting {appid} (up to {args.reviews_per_game} reviews)...")
                rows = collect_game(appid, args.reviews_per_game, args.pause)
                save_rows(out_path, rows)
                progress["apps"][str(appid)] = {
                    "requested_reviews": args.reviews_per_game,
                    "collected_reviews": len(rows),
                    "finished_at": datetime.now(timezone.utc).isoformat(),
                }
                with PROGRESS.open("w", encoding="utf-8") as f:
                    json.dump(progress, f, indent=2)
                print(f"  Saved {len(rows)} reviews")
            except (requests.RequestException, ValueError, RuntimeError) as error:
                print(f"  Failed {appid}: {error}; continuing with the next game")
            time.sleep(args.pause)
    except KeyboardInterrupt:
        print("\nInterrupted: saving combined data collected so far")
    finally:
        combined = combine_saved_files()
        print(f"Saved {combined} total review rows to {OUTPUT}")


if __name__ == "__main__":
    main()
