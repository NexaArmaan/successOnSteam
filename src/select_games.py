import argparse
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--per-tier", type=int, default=10,
                        help="Max number from each SteamSpy page (0, 10, 30)")
    parser.add_argument("--min-reviews", type=int, default=300,
                        help="Exclude games with fewer total Steam reviews")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    if args.per_tier < 1 or args.min_reviews < 0:
        parser.error("--per-tier must be positive and --min-reviews nonnegative")

    ids = pd.read_csv(RAW / "game_ids.csv")
    summaries = pd.read_csv(RAW / "steam_reviews_summary.csv")
    store = pd.read_csv(RAW / "games_data.csv")[["appid", "type", "genres"]]
    games = ids.merge(summaries[["appid", "total_reviews"]], on="appid")
    games = games.merge(store, on="appid")
    games = games[(games["type"] == "game") & (games["total_reviews"] >= args.min_reviews)]
    choices = {}
    for tier, group in games.groupby("source_page"):
        choices[tier] = group.sample(n=min(len(group), args.per_tier), random_state=args.seed)
        choices[tier] = choices[tier].reset_index(drop=True)

    # Interleave tiers so a five-game pilot isn't only the biggest titles.
    rows = []
    for index in range(max((len(group) for group in choices.values()), default=0)):
        for tier in sorted(choices):
            if index < len(choices[tier]):
                rows.append(choices[tier].iloc[index])
    if not rows:
        raise ValueError("No eligible games. Lower --min-reviews")
    selected = pd.DataFrame(rows)[["appid", "name", "source_page", "total_reviews", "genres"]]
    selected["appid"] = selected["appid"].astype(int)
    path = RAW / "selected_game_ids.csv"
    selected.to_csv(path, index=False)
    print(f"Selected {len(selected)} games, saved to {path}")
    print("Selection by original SteamSpy tier:")
    print(selected["source_page"].value_counts().sort_index().to_string())
    print("Selection is a convenience sample, NOT a random sample of Steam players.")


if __name__ == "__main__":
    main()
