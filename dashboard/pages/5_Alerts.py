"""
Alerts Page — Active Alarms, Operator Acknowledgment, and Incident Audit Trail.
Styled with Tactical Neon Lime & Pitch Black Industrial HUD aesthetic.
"""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
import pandas as pd
from database.repository import repo

st.set_page_config(page_title="Alarm Management | Apex Alerts", page_icon="🛡️", layout="wide")

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
        INDUSTRIAL ALARM &mdash; <span class="hero-highlight">EVENT QUEUE</span>
    </h1>
    <p class="hero-subtitle">
        Consecutive fault persistence debouncing (N=3), 15s hysteresis cooldown, and operator incident sign-offs.
    </p>
</div>
""", unsafe_allow_html=True)

# Fetch Unacknowledged Alerts
unack_df = repo.get_alerts(device_id="motor01", only_unacknowledged=True, limit=20)

st.markdown(f"### ⚠️ ACTIVE UNACKNOWLEDGED QUEUE ({len(unack_df)})")

if unack_df.empty:
    st.markdown("""
    <div style="background: rgba(158, 240, 26, 0.08); border: 1px solid rgba(158, 240, 26, 0.3); border-radius: 8px; padding: 14px 20px; color: #9ef01a; font-family: 'Oswald', sans-serif; letter-spacing: 0.5px;">
        ✓ ZERO UNACKNOWLEDGED ALARMS. ALL SENSOR STREAMS NOMINAL.
    </div>
    """, unsafe_allow_html=True)
else:
    for idx, row in unack_df.iterrows():
        sev = row["severity"]
        alert_id = row["id"]
        
        sev_color = "#ef4444" if sev == "CRITICAL" else ("#facc15" if sev == "WARNING" else "#06b6d4")

        with st.container():
            st.markdown(f"""
            <div style='background-color: #0d120e; border-left: 5px solid {sev_color}; border-top: 1px solid #1a261a; border-right: 1px solid #1a261a; border-bottom: 1px solid #1a261a; padding: 16px 20px; border-radius: 10px; margin-bottom: 12px;'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <strong style='color: #ffffff; font-size: 1.15rem; font-family: "Oswald", sans-serif; letter-spacing: 0.5px;'>
                        [{sev}] {row['title']}
                    </strong>
                    <span style='color: #7b8e7b; font-size: 0.85rem;'>{row['timestamp']}</span>
                </div>
                <p style='color: #b5c7b5; margin: 8px 0 0 0; font-size: 0.95rem;'>{row['message']}</p>
            </div>
            """, unsafe_allow_html=True)

            ack_col1, ack_col2 = st.columns([1.5, 4])
            with ack_col1:
                if st.button(f"ACKNOWLEDGE #{alert_id}", key=f"ack_btn_{alert_id}", type="primary"):
                    user = st.session_state.get("username", "operator")
                    repo.acknowledge_alert(alert_id, user=user)
                    st.success(f"Alert #{alert_id} acknowledged by {user}.")
                    st.rerun()

st.markdown("<hr style='border-color: #19241a; margin: 24px 0;'>", unsafe_allow_html=True)

# Full Alert Audit History
st.markdown("### 📋 HISTORICAL INCIDENT AUDIT LOG")
all_alerts = repo.get_alerts(device_id="motor01", only_unacknowledged=False, limit=50)

if not all_alerts.empty:
    display_df = all_alerts[[
        "id", "timestamp", "severity", "title", "acknowledged", "acknowledged_by", "acknowledged_at"
    ]]
    st.dataframe(display_df, use_container_width=True)
else:
    st.info("No recorded alarms in audit history.")
