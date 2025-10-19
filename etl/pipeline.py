import os, time
import pandas as pd
from datetime import datetime
from dateutil import parser as dtp
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
from sqlalchemy import create_engine

# ============================================================
# CONFIGURATION
# ============================================================
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
DB_PATH = os.path.join(DATA_DIR, "db.sqlite")
CSV_PATH = os.path.join(DATA_DIR, "season_2025_26_games.csv")
LAST_UPDATED_PATH = os.path.join(DATA_DIR, "LAST_UPDATED.txt")

PLAYER_NAME = "Stephen Curry"
SEASON = "2024-25"   # NBA API format (e.g., 2024-25)
TABLE = "games_2025_26"

# ============================================================
# 1. GET PLAYER ID
# ============================================================
def get_player_id(name: str) -> int:
    plist = players.get_players()
    pid = [p["id"] for p in plist if p["full_name"] == name]
    if not pid:
        raise ValueError(f"Player {name} not found.")
    return pid[0]

# ============================================================
# 2. FETCH GAME LOG DATA
# ============================================================
def fetch_gamelog(player_id: int, season: str) -> pd.DataFrame:
    """
    Calls the NBA Stats API for the player's game logs for a given season.
    Retries up to 4 times if network or rate-limit issues occur.
    """
    err = None
    for i in range(4):
        try:
            gl = playergamelog.PlayerGameLog(player_id=player_id, season=season, timeout=60)
            df = gl.get_data_frames()[0]
            print(f"✅ Successfully fetched {len(df)} games for {PLAYER_NAME}")
            return df
        except Exception as e:
            err = e
            print(f"Retry {i+1} failed: {e}")
            time.sleep(3 * (i + 1))
    raise err

# ============================================================
# 3. CLEAN / NORMALIZE COLUMNS
# ============================================================
def normalize_cols(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans and standardizes the NBA API output columns.
    Auto-handles any naming mismatches between seasons.
    """
    # Standardize column names to uppercase
    df.columns = [c.upper() for c in df.columns]

    expected = [
        "GAME_ID","GAME_DATE","MATCHUP","WL","MIN",
        "FGM","FGA","FG3M","FG3A","FTM","FTA","PTS","PLUS_MINUS"
    ]

    # Fill in any missing expected columns with blanks
    missing = [c for c in expected if c not in df.columns]
    if missing:
        print(f"⚠️ Warning: Missing columns {missing} — filling with default values.")
        for c in missing:
            df[c] = None

    # Keep only expected columns
    df = df[expected].copy()

    # Convert and add derived fields
    df["GAME_DATE"] = pd.to_datetime(df["GAME_DATE"])
    df["SEASON"] = SEASON

    df["FG_PCT"] = (df["FGM"] / df["FGA"]).fillna(0).replace([float("inf")], 0)
    df["FG3_PCT"] = (df["FG3M"] / df["FG3A"]).fillna(0).replace([float("inf")], 0)
    df["FT_PCT"] = (df["FTM"] / df["FTA"]).fillna(0).replace([float("inf")], 0)

    return df.sort_values("GAME_DATE")

# ============================================================
# 4. LOAD TO SQLITE DATABASE
# ============================================================
def load_sqlite(df: pd.DataFrame):
    """
    Stores the cleaned game log data in a local SQLite database.
    Deduplicates rows by GAME_ID each run.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    eng = create_engine(f"sqlite:///{DB_PATH}")

    try:
        existing = pd.read_sql_table(TABLE, eng)
    except Exception:
        existing = pd.DataFrame(columns=df.columns)

    all_df = pd.concat([existing, df], ignore_index=True)
    all_df = all_df.drop_duplicates(subset=["GAME_ID"], keep="last")
    all_df.to_sql(TABLE, eng, if_exists="replace", index=False)

# ============================================================
# 5. SAVE SNAPSHOT CSV
# ============================================================
def save_csv_snapshot():
    eng = create_engine(f"sqlite:///{DB_PATH}")
    snap = pd.read_sql(f"SELECT * FROM {TABLE} ORDER BY GAME_DATE", eng)
    snap.to_csv(CSV_PATH, index=False)
    print(f"💾 Saved snapshot to {CSV_PATH}")

# ============================================================
# 6. UPDATE LAST UPDATED TIMESTAMP
# ============================================================
def update_last_updated():
    with open(LAST_UPDATED_PATH, "w") as f:
        f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# ============================================================
# 7. MAIN EXECUTION PIPELINE
# ============================================================
def main():
    print(f"🚀 Starting ETL for {PLAYER_NAME} ({SEASON})")
    pid = get_player_id(PLAYER_NAME)
    raw = fetch_gamelog(pid, SEASON)
    clean = normalize_cols(raw)
    load_sqlite(clean)
    save_csv_snapshot()
    update_last_updated()
    print(f"✅ Pipeline complete — {len(clean)} games processed.")

# ============================================================
# RUN SCRIPT
# ============================================================
if __name__ == "__main__":
    main()