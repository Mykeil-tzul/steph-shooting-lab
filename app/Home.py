import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import os
from datetime import datetime

# ============================================================
# 📦 CONFIG
# ============================================================

st.set_page_config(page_title="Steph Shooting Lab", page_icon="🏀", layout="wide")

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
DB_PATH = os.path.join(DATA_DIR, "db.sqlite")
SEED_PATH = os.path.join(DATA_DIR, "seed_alltime_3pm.csv")
LAST_UPDATED_PATH = os.path.join(DATA_DIR, "LAST_UPDATED.txt")

# Connect to SQLite
engine = create_engine(f"sqlite:///{DB_PATH}")

# ============================================================
# 🧠 LOAD DATA
# ============================================================

# ============================================================
# 🧠 LOAD DATA (Fixed for SQLAlchemy 2.x)
# ============================================================

with engine.connect() as conn:
    season = pd.read_sql(
        text("""
            SELECT 
                COUNT(*) AS games,
                SUM(FG3M) AS threes_made,
                SUM(FG3A) AS threes_att,
                CASE WHEN SUM(FG3A)=0 THEN 0.0 ELSE 1.0*SUM(FG3M)/SUM(FG3A) END AS three_pct,
                SUM(FGM) AS fgm,
                SUM(FGA) AS fga,
                CASE WHEN SUM(FGA)=0 THEN 0.0 ELSE 1.0*SUM(FGM)/SUM(FGA) END AS fg_pct,
                SUM(FTM) AS ftm,
                SUM(FTA) AS fta,
                CASE WHEN SUM(FTA)=0 THEN 0.0 ELSE 1.0*SUM(FTM)/SUM(FTA) END AS ft_pct,
                ROUND(AVG(PTS),1) AS ppg
            FROM games_2025_26
        """),
        conn
    )

    games = pd.read_sql(
        text("""
            SELECT GAME_DATE, MATCHUP, WL, FG3M, FG3A, PTS
            FROM games_2025_26
            ORDER BY GAME_DATE DESC
        """),
        conn
    )

# 3. Load seed (career 3PM prior to this season)
seed = pd.read_csv(SEED_PATH)
seed_value = int(seed.iloc[0]["seed_career_3pm"])

# 4. Last updated timestamp
if os.path.exists(LAST_UPDATED_PATH):
    with open(LAST_UPDATED_PATH, "r") as f:
        last_updated = f.read().strip()
else:
    last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ============================================================
# 🎯 KPIs
# ============================================================

total_3pm = seed_value + int(season.loc[0, "threes_made"] or 0)
three_pct = round(season.loc[0, "three_pct"] * 100, 1)
fg_pct = round(season.loc[0, "fg_pct"] * 100, 1)
ppg = season.loc[0, "ppg"]

# ============================================================
# 🖼️ LAYOUT
# ============================================================

st.title("🏀 Steph Shooting Lab — Live Season Tracker")
st.caption(f"Last updated: {last_updated}")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Games", int(season.loc[0, "games"]))
col2.metric("3PM", int(season.loc[0, "threes_made"]))
col3.metric("3P%", f"{three_pct}%")
col4.metric("PPG", f"{ppg}")

col5, col6, col7 = st.columns(3)
col5.metric("Career 3PM", f"{total_3pm:,}")
col6.metric("FG%", f"{fg_pct}%")
col7.metric("FT%", f"{round(season.loc[0, 'ft_pct'] * 100, 1)}%")

# ============================================================
# 📊 GAME LOG TABLE
# ============================================================

st.subheader("📅 Recent Games")
st.dataframe(games, use_container_width=True)

# ============================================================
# 🧩 VISUALIZATIONS
# ============================================================

import altair as alt

st.subheader("📈 3PM by Game")
chart = (
    alt.Chart(games)
    .mark_bar(color="#FDB927")
    .encode(
        x=alt.X("GAME_DATE:T", title="Game Date"),
        y=alt.Y("FG3M:Q", title="3PM"),
        tooltip=["MATCHUP", "FG3M", "FG3A", "PTS", "WL"]
    )
)
st.altair_chart(chart, use_container_width=True)

# ============================================================
# 🏁 FOOTER
# ============================================================

st.markdown("---")
st.markdown("**Built with ❤️ by Mykeil Tzul** — Data, Basketball & AI 📊🏀")
