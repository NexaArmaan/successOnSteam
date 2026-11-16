# successOnSteam

**What makes a game successful on Steam?** This project collects raw data on Steam games from four APIs for studying how design choices relate to player satisfaction and popularity. The design choices covered are genre, price, camera perspective, art style, narrative, and multiplayer.

*Group 4: Armaan Arora, Shil Patel, D'Angelo Prepetit, Timothy Bas*

## Research question

Which characteristics of games on Steam (genre, price, camera perspective, visual style, narrative elements, and gameplay features) are associated with higher player satisfaction and popularity?

## Data sources

All data comes from public REST APIs; nothing was downloaded as a ready-made dataset.

| Source | Endpoint | What we use it for | Script | Raw output |
|---|---|---|---|---|
| SteamSpy catalog | `steamspy.com/api.php?request=all&page=N` | Game list to sample from, owner-count ranges, developer/publisher | `src/collect_steamspy.py` → `ids` | `data/raw/steamspy_page_{0,10,30}.json`, `data/raw/game_ids.csv` |
| SteamSpy details | `steamspy.com/api.php?request=appdetails&appid=N` | Community tags with vote counts: perspective, art style, narrative | `src/collect_steamspy.py` → `details` | `data/raw/steamspy_raw.json` |
| Steam Store | `store.steampowered.com/api/appdetails?appids=N` | Genres, gameplay categories, price, release date, description | `src/collect_games_data.py` | `data/raw/games_data.csv` |
| Steam Reviews | `api.steampowered.com/IUserReviewsService/GetAppReviews/v1/` | Review counts, % positive, Steam rating label | `src/collect_reviews.py` | `data/steam_reviews_summary.csv` |

### Sample

200 games, sampled with a fixed seed (`random.seed(42)`). Roughly a third come from each of three pages of the SteamSpy catalog, which is sorted by owners:

- page 0: the most-owned games on Steam
- page 10: mid-tier games
- page 30: smaller games

Sampling across tiers gives a mix of hits and small releases. It is **not** a random sample of all of Steam, so results describe these tiers, not Steam as a whole. `source_page` in `data/raw/game_ids.csv` records which tier each game came from.

## Why this data is messy

The four sources don't line up out of the box. Problems in the raw data include:

| Problem | Example |
|---|---|
| Numbers stored as text | SteamSpy price `"499"` (cents, as a string) |
| Ranges instead of numbers | Owners `"50,000 .. 100,000"` |
| Several values in one cell | Genres `"Action; Indie; Free To Play"` |
| Untranslated labels from Steam | `#category_contrast_controls`; `VR Supported` and `VR Support` both used |
| `$0` doesn't always mean free | Delisted games such as *Sniper Elite V2* and *FIFA 23* return no price |
| Rating label replaced by a count | `"3 user reviews"` instead of `"Positive"` for games with few reviews |
| % positive is unreliable for tiny samples | 1 of 1 review = 100% |
| Dates as text | `"Oct 27, 2016"`, one missing |
| Names differ between sources | `Battlefield 1` vs `Battlefield™ 1` |
| Dead fields | SteamSpy `score_rank` and `userscore` are empty for every game |
| Tags are free-form community labels | Hundreds of user-voted tags per game, with no fixed perspective or art-style field |
| Duplicate file | The reviews CSV is in the repo root and in `data/` |

All raw files are left exactly as the APIs returned them. `notebooks/raw_data.ipynb` loads them and shows these problems.

## How to reproduce

```bash
pip install -r requirements.txt

# 1. Sample game IDs (skips if data/raw/game_ids.csv already exists)
python src/collect_steamspy.py    # type: ids

# 2. SteamSpy tags for perspective / art style / narrative (~1 request per second, resumable)
python src/collect_steamspy.py    # type: details

# 3. Steam Store details
python src/collect_games_data.py

# 4. Review summaries
python src/collect_reviews.py

# 5. Load the raw data and view its problems
jupyter notebook notebooks/raw_data.ipynb   # Run All
```

All four collection steps have already been run and their output is committed.

## Raw data files

| File | Source | Contents |
|---|---|---|
| `data/raw/game_ids.csv` | SteamSpy catalog | The 200 sampled games: `appid`, `name`, `source_page` |
| `data/raw/steamspy_page_{0,10,30}.json` | SteamSpy catalog | Full catalog pages: owners range, price, developer, publisher |
| `data/raw/steamspy_raw.json` | SteamSpy details | Per-game details including community tags with vote counts |
| `data/raw/games_data.csv` | Steam Store | Genres, categories, price, release date, description |
| `data/steam_reviews_summary.csv` | Steam Reviews | Review counts, % positive, Steam rating label |

## Repository layout

```
src/collect_reviews.py        Reviews API collector
app_ids.txt                   App IDs read by collect_reviews.py (same IDs as game_ids.csv)
src/collect_steamspy.py       SteamSpy catalog + tag collector
src/collect_games_data.py     Store API collector
data/raw/                     Raw API output (never edited)
data/steam_reviews_summary.csv
notebooks/raw_data.ipynb
```

## Limitations

- The sample covers three popularity tiers of SteamSpy's catalog and spans release years 2006–2026, so it isn't a set of same-month new releases.
- SteamSpy owner counts are broad estimates; review counts are the more reliable popularity measure.
- Review numbers are a snapshot from October 2026 and change over time.
- The data shows associations, not causes.

## Use of AI tools

AI assistance (Anthropic's Claude) was used in a limited way during this project, mainly for help with setup, merging team branches, and drafting and reviewing parts of the notebook and this README. All data comes from the public APIs listed above, and the team reviewed the code and results.
