# successOnSteam

**What makes a game successful on Steam?** This project collects data on Steam games from four APIs, cleans and merges it, and builds one dataset for studying how design choices relate to player satisfaction and popularity. The design choices covered are genre, price, camera perspective, art style, narrative, and multiplayer.

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
| Steam Reviews | `api.steampowered.com/IUserReviewsService/GetAppReviews/v1/` | Review counts, % positive, Steam rating label | `collect_reviews.py` | `data/steam_reviews_summary.csv` |

### Sample

200 games, sampled with a fixed seed (`random.seed(42)`). Roughly a third come from each of three pages of the SteamSpy catalog, which is sorted by owners:

- page 0: the most-owned games on Steam
- page 10: mid-tier games
- page 30: smaller games

Sampling across tiers gives a mix of hits and small releases. It is **not** a random sample of all of Steam, so results describe these tiers, not Steam as a whole. `sample_page` in the final data records which tier each game came from.

## Why this data needed work

The four sources don't line up out of the box. The cleaning notebook handles:

| Problem | Example | Fix |
|---|---|---|
| Numbers stored as text | SteamSpy price `"499"` (cents, as a string) | Converted to `4.99` dollars |
| Ranges instead of numbers | Owners `"50,000 .. 100,000"` | Split into `owners_low`, `owners_high`, plus a geometric midpoint `owners_mid` |
| Several values in one cell | Genres `"Action; Indie; Free To Play"` | One yes/no column per genre and per gameplay feature |
| Untranslated labels from Steam | `#category_contrast_controls` | Mapped to readable names; `VR Supported` merged with `VR Support` |
| `$0` doesn't always mean free | Delisted games such as *Sniper Elite V2* and *FIFA 23* return no price | Flagged with `price_missing`; SteamSpy's price used where it has one (`price_source`) |
| Rating label replaced by a count | `"3 user reviews"` instead of `"Positive"` for games with few reviews | `rating_label` left blank, `low_review_count` flag added |
| % positive is unreliable for tiny samples | 1 of 1 review = 100% | Added `review_score_wilson` (Wilson lower bound) |
| Dates as text | `"Oct 27, 2016"`, one missing | Parsed to dates, plus `release_year` / `release_month` |
| Names differ between sources | `Battlefield 1` vs `Battlefield™ 1` | SteamSpy's name kept; differences reported |
| Dead fields | SteamSpy `score_rank` and `userscore` are empty for every game | Dropped |
| Duplicate file | The reviews CSV is in the repo root and in `data/` | Notebook reads `data/` and checks the two copies match |

All raw files are left untouched; every fix happens in the notebook.

## How to reproduce

```bash
pip install -r requirements.txt
pip install matplotlib            # used for the charts in the notebook

# 1. Sample game IDs (skips if data/raw/game_ids.csv already exists)
python src/collect_steamspy.py    # type: ids

# 2. SteamSpy tags for perspective / art style / narrative (~1 request per second, resumable)
python src/collect_steamspy.py    # type: details

# 3. Steam Store details
python src/collect_games_data.py

# 4. Review summaries
python collect_reviews.py

# 5. Merge and clean → data/processed/steam_games_clean.csv and .json
jupyter notebook notebooks/clean_and_merge.ipynb   # Run All
```

Steps 1, 3 and 4 have already been run and their output is committed. **Step 2 still needs to be run**: until `data/raw/steamspy_raw.json` exists, the notebook runs fine but the perspective, art-style and narrative columns are empty.

## Output

`data/processed/steam_games_clean.csv` (same content in `steam_games_clean.json`): one row per game, 200 rows, 94 columns.

### Data dictionary

**Identity**

| Column | Description |
|---|---|
| `appid` | Steam app ID (join key across all sources) |
| `name`, `developer`, `publisher` | From SteamSpy |
| `release_date`, `release_year`, `release_month` | Parsed from the Store API |
| `short_description` | Store page blurb (free text) |
| `sample_page`, `catalog_page` | SteamSpy catalog page the game was sampled from (0 = most owned) |

**Price**

| Column | Description |
|---|---|
| `initial_price`, `final_price` | USD; `final_price` includes any sale at collection time |
| `on_sale` | `final_price < initial_price` |
| `is_free_to_play` | Store genre includes "Free To Play" |
| `price_missing` | Store returned no price for a game that isn't free (usually delisted) |
| `price_source` | `store`, `steamspy` (fallback), or `missing` |

**Success measures**

| Column | Description |
|---|---|
| `total_reviews`, `total_positive`, `total_negative` | Steam review counts (Steam purchases only) |
| `positive_percentage` | positive ÷ (positive + negative) × 100 |
| `review_score_wilson` | Lower bound of the 95% Wilson interval on % positive; penalises tiny review counts |
| `log_total_reviews` | log10 of review count, a popularity measure |
| `rating_label` | Steam's label (Overwhelmingly Negative … Overwhelmingly Positive), ordered; blank when too few reviews |
| `review_score_code` | Steam's numeric code for the label |
| `low_review_count` | Fewer than 10 reviews |
| `owners_range`, `owners_low`, `owners_high`, `owners_mid` | SteamSpy owner estimate (broad ranges, secondary measure) |
| `peak_ccu_yesterday` | SteamSpy peak concurrent players on the day of collection |

**Design: genres and gameplay** (Store API)

| Column | Description |
|---|---|
| `genres`, `n_genres` | Cleaned genre list and count |
| `genre_*` | 1/0 for each of the 14 genres in the sample |
| `categories`, `n_categories` | Cleaned Steam feature list and count |
| `single_player`, `multiplayer`, `online_pvp`, `co_op`, `mmo` | Play modes |
| `steam_achievements`, `steam_workshop`, `controller_full`, `controller_partial`, `in_app_purchases`, `vr` | Other features |

**Design: perspective, art style, narrative** (SteamSpy tags; empty until step 2 is run)

| Column | Description |
|---|---|
| `perspective` | Most-voted of First-Person, Third Person, Top-Down, Isometric, Side Scroller, 2.5D |
| `art_style` | Most-voted of Pixel Graphics, Realistic, Anime, Cartoony, Stylized, Hand-drawn, … |
| `narrative` | Most-voted of Story Rich, Choices Matter, Multiple Endings, Narration, … |
| `dimension` | 2D or 3D |
| `story_rich` | Game has the "Story Rich" tag |
| `tag_*` | Each design tag's share of the game's total tag votes (0–1) |
| `n_tags`, `top_tags` | Number of tags and the ten most-voted |

**Metadata**

| Column | Description |
|---|---|
| `reviews_collected_at` | When review data was pulled (UTC) |

## Repository layout

```
collect_reviews.py            Reviews API collector
app_ids.txt                   App IDs read by collect_reviews.py (same IDs as game_ids.csv)
src/collect_steamspy.py       SteamSpy catalog + tag collector
src/collect_games_data.py     Store API collector
data/raw/                     Raw API output (never edited)
data/steam_reviews_summary.csv
data/processed/               Cleaned, merged dataset
notebooks/clean_and_merge.ipynb
```

## Limitations

- The sample covers three popularity tiers of SteamSpy's catalog and spans release years 2006–2026, so it isn't a set of same-month new releases.
- SteamSpy owner counts are broad estimates; review counts are the more reliable popularity measure.
- Review numbers are a snapshot from October 2026 and change over time.
- The data shows associations, not causes.

## Use of AI tools

AI assistance (Anthropic's Claude) was used in a limited way during this project, mainly for help with setup, merging team branches, and drafting and reviewing parts of the cleaning notebook and this README. All data comes from the public APIs listed above, and the team reviewed the code and results.
