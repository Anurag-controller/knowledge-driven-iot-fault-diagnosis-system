"""
Historical Analytics Page — Persistent Database Queries & Data Export.
Styled with Tactical Neon Lime & Pitch Black Industrial HUD aesthetic.
"""

import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
import pandas as pd
from database.repository import repo
from dashboard.components.charts import create_live_telemetry_chart

st.set_page_config(page_title="Historical Analytics | Apex Database", page_icon="🛡️", layout="wide")

# Inject Theme CSS
css_path = Path(__file__).resolve().parent.parent / "styles" / "theme.css"
if css_path.exists():
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

if not st.session_state.get("authenticated", False):
    st.warning("Please sign in from the main portal.")
    st.stop()

# Header Banner
st.markdown("""
<div class="hero-header" style="padding: 22px 28px;">
    <h1 class="hero-title" style="font-size: 2.2rem;">
        HISTORICAL TELEMETRY &mdash; <span class="hero-highlight">DATABASE ARCHIVE</span>
    </h1>
    <p class="hero-subtitle">
        Query indexed SQLite records in WAL mode, multi-variable trend overlays, and analytical data export.
    </p>
</div>
""", unsafe_allow_html=True)

# Filter Controls
f_col1, f_col2, f_col3 = st.columns([1, 1, 1])

now = datetime.now(timezone.utc)
default_start = (now - timedelta(hours=2)).date()
default_end = now.date()

with f_col1:
    start_date = st.date_input("Start Date", default_start)
with f_col2:
    end_date = st.date_input("End Date", default_end)
with f_col3:
    max_records = st.selectbox("Max Records Limit", options=[100, 500, 1000, 5000], index=1)

start_iso = f"{start_date.isoformat()}T00:00:00Z"
end_iso = f"{end_date.isoformat()}T23:59:59Z"

# Fetch filtered readings from SQLite
df = repo.get_readings_by_time_range("motor01", start_iso, end_iso, limit=max_records)

if df.empty:
    st.warning(f"No records found between {start_iso} and {end_iso}. Expanding to most recent records...")
    df = repo.get_recent_readings("motor01", limit=max_records)

if not df.empty:
    st.markdown(f"### 📈 TELEMETRY OVERLAYS ({len(df)} RECORDS LOADED)")

    # Time-series Chart
    fig = create_live_telemetry_chart(df)
    st.plotly_chart(fig, use_container_width=True)

    # Statistical Aggregations
    st.markdown("### 📊 STATISTICAL SUMMARY")
    stats_df = df[["temperature_c", "vibration_rms_g", "current_a", "rpm"]].describe().T
    stats_df = stats_df.rename(columns={
        "mean": "Mean", "std": "Std Dev", "min": "Min", "max": "Max"
    })
    st.dataframe(stats_df[["Mean", "Std Dev", "Min", "Max"]], use_container_width=True)

    # CSV Export Button
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 EXPORT HISTORICAL DATASET (CSV)",
        data=csv_bytes,
        file_name=f"motor01_telemetry_{start_date}_{end_date}.csv",
        mime="text/csv",
        type="primary",
    )
