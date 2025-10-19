import os
import pandas as pd
from nba_api.stats.endpoints import playergamelog
from datetime import datetime
from sqlalchemy import create_engine

# ======================================================
# CONFIG
# ======================================================

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "db.sqlite")
CSV_PATH = os.path.join(DATA_DIR, "season_2025_26_games.csv")
LAST_UPDATED_PATH = os.path.join(DATA_DIR, "LAST_UPDATED.txt")
PLAYERS_PATH = os.path.join(DATA_DIR, "players.csv")
SEED_PATH = os.path.join(DATA_DIR, "seed_alltime_3pm.csv")

PLAYER_ID = 201939  # Steph Curry
SEASON = "2024-25"
TABLE = "games_2025_26"

# ======================================================
# FUNCTIONS
# ======================================================

def fetch_player_game_logs(player_id: int, season: str) -> pd.DataFrame:
    """Fetch all game logs for the given player & season."""
    print(f"📡 Fetching game logs for player {player_id} ({season})...")
    gamelog = playergamelog.PlayerGameLog(player_id=player_id, season=season)
    df = gamelog.get_data_frames()[0]
    print(f"✅ Retrieved {len(df)} games.")
    return df


def normalize_cols(df: pd.DataFrame) -> pd.DataFrame:
    """Keep and rename key columns."""
    keep = ["GAME_DATE", "MATCHUP", "WL", "FGM", "FGA", "FG3M", "FG3A", "FTM", "FTA", "PTS"]
    df = df[keep].copy()
    df.columns = [c.lower() for c in df.columns]
    df["game_date"] = pd.to_datetime(df["game_date"])
    return df


def save_sqlite(df: pd.DataFrame, table: str):
    """Save cleaned data to SQLite."""
    engine = create_engine(f"sqlite:///{DB_PATH}")
    df.to_sql(table, engine, if_exists="replace", index=False)
    print(f"💾 Saved {len(df)} records to {table} in SQLite.")


def save_csv_snapshot(df: pd.DataFrame):
    """Save a CSV snapshot of the season."""
    df.to_csv(CSV_PATH, index=False)
    print(f"📂 Snapshot saved to {CSV_PATH}")


def update_last_updated():
    """Update timestamp text file."""
    with open(LAST_UPDATED_PATH, "w") as f:
        f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("🕒 Updated timestamp.")


# ======================================================
# MAIN
# ======================================================

def main():
    print(f"\n🚀 Starting ETL for Steph Curry ({SEASON})\n")

    # Fetch data
    raw = fetch_player_game_logs(PLAYER_ID, SEASON)
    if raw.empty:
        print("⚠️ No games found. Skipping save.")
        return

    clean = normalize_cols(raw)
    save_sqlite(clean, TABLE)
    save_csv_snapshot(clean)
    update_last_updated()

    print(f"\n✅ Pipeline complete — {len(clean)} games processed.\n")


if __name__ == "__main__":
    main()
