# Beyond Playtime: Does Playing More Mean Enjoying More?

### A Data Science Analysis of Player Engagement and Satisfaction on Steam

**CSC 366 – Principles of Data Science | Fall 2026**  
**Farmingdale State College**

**Group 4:** Armaan Arora, Shil Patel, D'Angelo Prepetit, Timothy Bas

---

## Project Overview

Does spending more time playing a video game necessarily mean that a player enjoys it more?

Video games are designed to keep players engaged, and playtime is often used as a measure of a game's success. However, spending hundreds of hours playing a game does not always mean that a player is satisfied with their experience. Some players invest significant amounts of time in games but ultimately leave negative reviews.

Our project explores this relationship using real Steam game data. By combining individual player reviews, gameplay hours, game genres, and other characteristics, we aim to understand whether higher engagement is associated with greater player satisfaction.

We are particularly interested in the **playtime–satisfaction paradox:** why do some players spend hundreds or thousands of hours playing games they do not recommend?

Rather than examining what makes a game commercially successful, our research focuses on player behavior, engagement, and recommendations across different types of games.

## Research Question

**How does the amount of time players spend playing Steam games relate to their likelihood of recommending them, and how does this relationship differ across genres and gameplay styles? Additionally, what patterns can be identified among players who spend significant amounts of time playing games but leave negative reviews?**

Our research investigates four main questions:

1. Are players with more gameplay hours more likely to leave positive reviews?
2. Does the relationship between playtime and recommendations differ across game genres and gameplay styles?
3. How common are negative reviews among players with 100 or more hours of gameplay?
4. Can playtime and game characteristics help predict whether a player will recommend a game?

**Note:** Steam recommendations are used as a measurable indicator of player satisfaction. They do not directly measure a player's emotional happiness.

---

## Data Sources

Our project collects data directly from public APIs rather than using a prebuilt dataset.

| Source | Data Collected | Purpose |
|---|---|---|
| SteamSpy API | Estimated owners, game tags, popularity statistics, developer and publisher information | Game characteristics and background information |
| Steam Store API | Genres, categories, release dates, prices, descriptions | Game metadata and gameplay classifications |
| Steam User Reviews API | Individual reviews, playtime at review, recommendation status, review dates and text | Main player engagement and satisfaction analysis |

**API References:**

- SteamSpy API: https://steamspy.com/api.php
- Steam Store: https://store.steampowered.com/api/appdetails
- Steam User Reviews: https://partner.steamgames.com/doc/webapi/IUserReviewsService

The individual review collector uses the public Steam Reviews API and does not require a Steam API key.

## Dataset and Collection Methodology

Our original dataset consists of **200 Steam games**, sampled from three different SteamSpy catalog pages representing different popularity levels.

- **Page 0:** Higher-ownership games
- **Page 10:** Mid-tier games
- **Page 30:** Lower-ownership games

The original sampling process uses a fixed random seed (`42`) to make game selection reproducible.

For our updated research, we selected **28 games** from this existing dataset based on review availability, with a target of collecting up to 300 individual reviews per game.

The review collector supports pagination, request retries, and per-game progress saving.

### Current Dataset Summary

*Initial collection — November 2026*

| Metric | Value |
|---|---:|
| Original game catalog | 200 games |
| Games selected for review analysis | 28 |
| Individual reviews collected | 6,999 |
| Positive recommendations | 5,483 |
| Negative recommendations | 1,516 |
| Reviews with 100+ hours played | 916 |
| Positive reviews with 100+ hours | 783 |
| Negative reviews with 100+ hours | 133 |
| Negative reviews with 500+ hours | 33 |
| Duplicate individual reviews | 0 |
| Missing playtime values | 1 |

### Preliminary Observation

Among the 916 sampled reviews from players with at least 100 hours of gameplay:

- **85.48%** were positive recommendations.
- **14.52%** were negative recommendations.

This provides a starting point for investigating the relationship between gameplay engagement and player satisfaction.

However, further analysis is required to determine how these percentages compare with players who have fewer hours and whether results differ across genres or individual games.

These were early observations. See [Key Findings](#key-findings) below for the final results.

---

## Project Structure

```text
successOnSteam/
│
├── README.md
├── requirements.txt
├── .gitignore
│
├── src/
│   ├── collect_steamspy.py
│   ├── collect_games_data.py
│   ├── collect_reviews.py
│   ├── select_games.py
│   └── collect_individual_reviews.py
│
├── data/
│   ├── raw/
│   │   ├── game_ids.csv
│   │   ├── selected_game_ids.csv
│   │   ├── games_data.csv
│   │   ├── steamspy_raw.json
│   │   ├── steamspy_page_*.json
│   │   ├── steam_reviews_summary.csv
│   │   ├── individual_reviews.csv
│   │   └── reviews/
│   │       └── by_app/
│   │
│   ├── individual_reviews_cleaned.csv
│   │
│   └── cleaned/
│       ├── games_data.csv
│       ├── steamspy.json
│       ├── steam_reviews_summary.csv
│       └── reviews_with_games.csv   (created by running 03_eda_statistics.ipynb)
│
├── notebooks/
│   ├── raw_data.ipynb
│   ├── 01_game_cleaning.ipynb
│   ├── 02_review_cleaning.ipynb
│   ├── 03_eda_statistics.ipynb
│   └── 04_machine_learning.ipynb
│
├── tests/
│   ├── test_review_collector.py
│   └── test_review.py
│
├── figures/
│
└── docs/
    └── Beyond_Playtime_Report_final.pdf
```

*Note: Notebooks 01–03 are complete. The machine learning notebook and figures are still in progress. `steamspy.json` in `data/cleaned/` is saved as CSV text despite its `.json` extension.*

### Folder Descriptions

- **`src/`** — Python scripts used to collect game data and individual player reviews from APIs.
- **`data/raw/`** — Original collected datasets, preserved without cleaning or modification.
- **`data/cleaned/`** — Processed datasets generated during data cleaning and merging.
- **`notebooks/`** — Jupyter notebooks for cleaning, exploratory analysis, statistics, and machine learning.
- **`tests/`** — Scripts for checking collector functionality and validating collected data.
- **`figures/`** — Visualizations generated from our analysis.
- **`docs/`** — Project documentation and assignment reports.

---

## Technologies and Libraries

**Programming Language:** Python

**Data Collection:**
- `requests` — API requests
- `json` and `csv` — Data storage and processing

**Data Processing:**
- `pandas` — Data cleaning, merging, and manipulation
- `numpy` — Numerical operations

**Exploratory Data Analysis and Statistics:**
- `matplotlib` — Data visualization
- `seaborn` — Statistical visualizations
- `scipy` — Statistical testing

**Machine Learning (Planned):**
- `scikit-learn` — Classification models and evaluation

**Development Tools:**
- VS Code
- Jupyter Notebook
- Git and GitHub

---

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/NexaArmaan/successOnSteam.git
cd successOnSteam
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Select Games for Review Collection

```bash
python src/select_games.py --per-tier 10 --min-reviews 300
```

This creates `data/raw/selected_game_ids.csv` using the existing Steam game catalog and review summaries.

### 5. Collect Individual Steam Reviews

To test the collector using a small sample:

```bash
python src/collect_individual_reviews.py --limit-games 2 --reviews-per-game 10
```

To collect up to 300 reviews per selected game:

```bash
python src/collect_individual_reviews.py --reviews-per-game 300
```

The results are saved in:

```text
data/raw/individual_reviews.csv
```

The collector also saves individual game results to support restarting interrupted collection sessions.

### 6. Run Collector Tests

```bash
python -m unittest discover -s tests -p "test_review_collector.py" -v
```

### 7. Open the Analysis Notebooks

```bash
jupyter notebook
```

Navigate to the `notebooks/` folder to view data cleaning, EDA, and later machine learning work.

---

## Data Cleaning and Preprocessing

Our data comes from multiple APIs, so cleaning and standardization are necessary before analysis.

The cleaning workflow includes:

1. Identifying and handling missing or incomplete values.
2. Checking for duplicate game and review records.
3. Converting playtime from minutes into hours.
4. Converting Unix timestamps into readable dates.
5. Standardizing positive and negative recommendation values.
6. Cleaning game genres, prices, categories, and other metadata.
7. Identifying extreme playtime values and deciding how to handle them.
8. Creating playtime groups for statistical comparisons.
9. Merging game-level and individual-review datasets using Steam App IDs.
10. Validating the final processed dataset.

### Planned Playtime Categories

| Category | Hours Played |
|---|---|
| Very short | 0–2 hours |
| Short | 2–10 hours |
| Moderate | 10–50 hours |
| Long | 50–100 hours |
| Very long | 100+ hours |

These categories will help us compare positive and negative recommendation percentages at different engagement levels.

We will preserve legitimate high-playtime observations rather than automatically treating them as errors.

All original data remains available in `data/raw/` for reproducibility.

---

## Exploratory Data Analysis and Statistical Analysis

The combined analysis is in `notebooks/03_eda_statistics.ipynb`, and the full write-up is in `docs/Beyond_Playtime_Report_final.pdf`.

### What We Did

1. Merged the cleaned reviews with the cleaned game data on `appid` and checked that no rows were lost, doubled, or left unmatched (6,998 reviews across 28 games).
2. Added game features: primary genre (from SteamSpy user tags), multiplayer vs single-player only, story-rich, and free-to-play.
3. Compared positive recommendation rates across the five playtime groups, overall and by genre and gameplay style.
4. Ran statistical tests: chi-square with Cramér's V, Mann–Whitney U, a within-game Wilcoxon test, and Fisher exact tests.
5. Sorted the 133 negative reviews from players with 100+ hours into complaint themes, and compared them with negative reviews from players under 100 hours.

### Key Findings

| Playtime group | Reviews | Positive rate |
|---|---:|---:|
| 0–2 hours | 1,317 | 63.3% |
| 2–10 hours | 2,267 | 76.8% |
| 10–50 hours | 1,959 | 85.1% |
| 50–100 hours | 539 | 84.8% |
| 100+ hours | 916 | 85.5% |

- **More playtime goes with more positive reviews, but only up to about 10 hours.** After that, the positive rate stays around 85%. The chi-square test is significant (p < 0.001) with a small-to-moderate effect (Cramér's V = 0.20). The pattern also holds within individual games: the longer-playing half of reviewers was more positive in 23 of 26 games.
- **Genres and gameplay styles.** Multiplayer and single-player games follow almost the same pattern. Story-rich games show the strongest effect: only 34% of their reviews from players with under 2 hours are positive. Roguelikes are liked at every playtime level.
- **Long-time negative reviewers.** 14.5% of 100+ hour reviews are negative (vs 22.7% under 100 hours). Compared with shorter-playtime critics, they complain much more about updates or mods breaking the game (22% vs 6%), the game getting worse over time (25% vs 14%), and the developer or paid content (41% vs 22%). They are also more than twice as likely to say they used to love the game.

### Planned Visualizations

- Histogram of gameplay hours
- Boxplots comparing positive and negative review playtime
- Positive recommendation percentage by playtime category
- Genre-specific playtime and recommendation comparisons
- Breakdown of long-time negative reviews by game
- Additional plots based on findings during EDA

Our objective is to create a clear visual story showing whether time invested in a game is necessarily associated with a positive player experience.

---

## Machine Learning (Planned)

Following data cleaning and exploratory analysis, we plan to investigate whether review recommendations can be predicted using gameplay hours and game characteristics.

### Prediction Target

`voted_up`

- `1` — Positive recommendation
- `0` — Negative recommendation

### Potential Features

- Playtime at review
- Log-transformed playtime
- Genre
- Gameplay categories
- Multiplayer or single-player characteristics
- Game release year
- Price category

### Planned Models

- Logistic Regression
- Decision Tree
- Random Forest (optional)

We plan to compare a baseline model using playtime alone with another model incorporating additional game characteristics.

Model performance will be evaluated using measures such as precision, recall, F1-score, balanced accuracy, and ROC-AUC.

To reduce data leakage, we intend to evaluate model generalization using game-level train/test separation.

---

## Team Responsibilities

| Member | Primary Responsibilities |
|---|---|
| Armaan Arora | API collection, individual review dataset, repository setup, integration support, and later ML |
| Shil Patel | Combined dataset, EDA, statistical testing, long-time negative review analysis, and project report |
| D'Angelo Prepetit | Individual review cleaning and initial review analysis |
| Timothy Bas | Game data cleaning (Steam Store, SteamSpy, review summary) and game-level statistics |

The remaining cleaning, visualization, statistics, documentation, and reporting tasks are divided among the team members, with shared review and integration before submission.

---

## Research Goal

Ultimately, our project aims to explore an important distinction in gaming: **engagement and satisfaction are not necessarily the same thing.**

By analyzing gameplay hours, player recommendations, and differences between game types, we hope to better understand what playtime actually tells us about player experience.

Our findings may help game recommendation systems, gaming researchers, and players interpret gameplay statistics more meaningfully, rather than assuming that more hours always mean greater enjoyment.

---

## Academic Purpose

This project is developed for **CSC 366 – Principles of Data Science at Farmingdale State College**, Fall 2026.

Data is collected from publicly available Steam and SteamSpy APIs for educational research and analysis.

---

## AI Usage

AI assistance (Anthropic's Claude) was used in a limited way during this project, mainly for help with setup, merging team branches, and drafting and reviewing parts of the notebook and this README.