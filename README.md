# 🏀 Steph Shooting Lab — Live NBA Season Tracker

A full-stack data pipeline + dashboard that tracks **Stephen Curry’s 3-point shooting performance** throughout the 2025–26 NBA season.

This project automatically fetches real-time game data from the NBA Stats API, stores it in SQLite, and visualizes key metrics through an interactive Streamlit dashboard.

---
## Live Demo

👉 Steph Shooting Lab (Streamlit App)
https://steph-shooting-lab-bymt.streamlit.app

## Features

 **Automated ETL Pipeline**
- Python ETL script (`etl/pipeline.py`) fetches and cleans game data.
- Saves clean data snapshots and updates `LAST_UPDATED.txt` automatically.

 **Live Streamlit Dashboard**
- Displays Curry’s:
  - Total games, 3PM, FG%, 3P%, FT%, and PPG
  - Recent game logs (sortable)
  - Interactive 3PM-by-game chart
- Auto-refreshes on each `git push` via Streamlit Cloud.

 **SQLite + CSV Data Layer**
- Lightweight persistent database (`data/db.sqlite`)
- CSV backups stored in `/data`

---

## Tech Stack

| Layer | Tools Used |
|-------|-------------|
| **Data Extraction** | `nba_api`, `requests`, `pandas` |
| **Data Storage** | SQLite, CSV |
| **Transformation** | `pandas` |
| **Visualization** | `Streamlit`, `Altair` |
| **Automation** | GitHub Actions CI/CD |

---

## Project Structure

steph-shooting-lab/
├── app/
│ └── Home.py # Streamlit dashboard UI
├── data/
│ ├── season_2025_26_games.csv
│ ├── players.csv
│ ├── db.sqlite
│ └── LAST_UPDATED.txt
├── etl/
│ └── pipeline.py # ETL job: fetch → clean → load → save
├── sql/
│ └── queries.sql # (optional SQL analysis scripts)
├── .github/
│ └── workflows/
│ └── update_data.yml # GitHub Actions automation
├── requirements.txt
└── README.md

---

## How It Works

1. The **GitHub Action** runs `etl/pipeline.py` to fetch Curry’s latest stats.
2. The ETL pipeline cleans and loads new data into `data/db.sqlite` and `season_2025_26_games.csv`.
3. When you `git push`, Streamlit Cloud automatically rebuilds the app.
4. Dashboard updates with the latest stats and charts.

---

## Run Locally

```bash
# 1. Clone the repo
git clone https://github.com/Mykeil-tzul/steph-shooting-lab.git
cd steph-shooting-lab

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate    # Mac/Linux
venv\Scripts\activate       # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run ETL pipeline
python etl/pipeline.py

# 5. Launch the dashboard

🔁 Automation via GitHub Actions

The workflow (.github/workflows/update_data.yml) runs weekly to:

Fetch latest season data

Commit updated CSVs and timestamps

Push new data to the repo (auto-refreshing Streamlit)

You can also run it manually from GitHub → Actions → “Update Steph Curry Data Weekly” → Run workflow.


streamlit run app/Home.py
