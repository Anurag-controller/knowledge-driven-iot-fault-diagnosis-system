"""
Overview Page — Executive Asset Health, KPIs, and Connectivity.
Styled with Tactical Neon Lime & Pitch Black Industrial HUD aesthetic.
"""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
import pandas as pd
from datetime import datetime, timezone
from config.settings import settings
from database.repository import repo
from dashboard.components.charts import create_gauge

st.set_page_config(page_title="Executive Overview | Apex Diagnostics", page_icon="🛡️", layout="wide")

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
        EXECUTIVE ASSET OVERVIEW &mdash; <span class="hero-highlight">MOTOR 01</span>
    </h1>
    <p class="hero-subtitle">
        Condition-monitoring telemetry and physics envelope verification for 12V Brushed DC Feed Motor (Cell 1, Station 01).
    </p>
</div>
""", unsafe_allow_html=True)

# Fetch latest telemetry and diagnosis from SQLite
readings_df = repo.get_recent_readings(device_id="motor01", limit=1)
diag_df = repo.get_recent_predictions(device_id="motor01", limit=1)
alerts_df = repo.get_alerts(device_id="motor01", only_unacknowledged=True, limit=5)

latest_reading = readings_df.iloc[-1].to_dict() if not readings_df.empty else None
latest_diag = diag_df.iloc[0].to_dict() if not diag_df.empty else None

# Status Header Bar
status_col1, status_col2, status_col3 = st.columns([2, 1, 1])

with status_col1:
    if latest_reading:
        ts = latest_reading["timestamp"]
        st.markdown(f"**LAST TELEMETRY EVENT:** `{ts}`")
    else:
        st.info("No telemetry received yet. Ingestion pipeline standing by.")

with status_col2:
    mqtt_cfg = settings.get_effective_mqtt_config()
    broker_name = "HiveMQ Cloud" if mqtt_cfg["broker_type"] == "hivemq_cloud" else f"Local Broker ({settings.LOCAL_MQTT_PORT})"
    st.markdown(f"**BROKER:** `{broker_name}`")

with status_col3:
    mode_badge = "🟢 SIMULATION" if settings.OPERATION_MODE == "simulation" else "🔵 REAL HARDWARE"
    st.markdown(f"**MODE:** {mode_badge}")

st.markdown("<hr style='border-color: #19241a; margin: 16px 0;'>", unsafe_allow_html=True)

# KPI Metric Cards
temp_val = latest_reading["temperature_c"] if latest_reading else 0.0
vibe_val = latest_reading["vibration_rms_g"] if latest_reading else 0.0
curr_val = latest_reading["current_a"] if latest_reading else 0.0
rpm_val = latest_reading["rpm"] if latest_reading else 0.0

m_col1, m_col2, m_col3, m_col4 = st.columns(4)

with m_col1:
    st.markdown(f"""
    <div class='metric-container'>
        <div class='metric-label'>MOTOR TEMPERATURE</div>
        <div class='metric-value'>{temp_val:.1f}<span class='metric-unit'>°C</span></div>
    </div>
    """, unsafe_allow_html=True)

with m_col2:
    st.markdown(f"""
    <div class='metric-container'>
        <div class='metric-label'>VIBRATION RMS</div>
        <div class='metric-value'>{"N/A" if vibe_val is None else format(vibe_val, ".3f")}<span class='metric-unit'>g</span></div>
    </div>
    """, unsafe_allow_html=True)

with m_col3:
    st.markdown(f"""
    <div class='metric-container'>
        <div class='metric-label'>ARMATURE CURRENT</div>
        <div class='metric-value'>{curr_val:.3f}<span class='metric-unit'>A</span></div>
    </div>
    """, unsafe_allow_html=True)

with m_col4:
    st.markdown(f"""
    <div class='metric-container'>
        <div class='metric-label'>ROTATIONAL SPEED</div>
        <div class='metric-value'>{rpm_val:.0f}<span class='metric-unit'>RPM</span></div>
    </div>
    """, unsafe_allow_html=True)

# Active Diagnostic Hypothesis Banner
st.markdown("### 🛡️ ACTIVE DIAGNOSTIC STATUS")
if latest_diag:
    sev = latest_diag["hybrid_severity"]
    fault = latest_diag["hybrid_fault"]
    explanation = latest_diag.get("explanation", "")
    rec = latest_diag.get("recommended_action", "")

    badge_class = {
        "NORMAL": "status-normal",
        "WARNING": "status-warning",
        "CRITICAL": "status-critical",
    }.get(sev, "status-unknown")

    st.markdown(f"""
    <div class='diagnosis-box'>
        <h3 style='margin: 0; display: flex; align-items: center; gap: 12px;'>
            <span class='status-pill {badge_class}'>{sev}</span>
            <span style='color: #ffffff;'>{fault}</span>
        </h3>
        <p style='color: #a4b8a4; margin-top: 10px; font-size: 0.95rem;'>{explanation}</p>
        <p style='color: #9ef01a; font-weight: 600; font-size: 0.95rem; margin-bottom: 0;'>
            🔧 <strong>Recommended Action:</strong> {rec}
        </p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.info("Awaiting diagnostic inference results...")

# Gauges Section
st.markdown("### 📊 OPERATIONAL ENVELOPES")
g_col1, g_col2, g_col3, g_col4 = st.columns(4)

with g_col1:
    st.plotly_chart(create_gauge(temp_val, 0, 100, "Temperature", "°C", 60.0, 75.0), use_container_width=True)
with g_col2:
    st.plotly_chart(create_gauge(vibe_val, 0, 1.0, "Vibration", "g", 0.40, 0.70), use_container_width=True)
with g_col3:
    st.plotly_chart(create_gauge(curr_val, 0, 2.5, "Current", "A", 1.10, 1.70), use_container_width=True)
with g_col4:
    st.plotly_chart(create_gauge(rpm_val, 0, 3000, "Speed", "RPM", 1400, 200), use_container_width=True)

# Quick Unacknowledged Alerts
st.markdown("### 🚨 ACTIVE UNACKNOWLEDGED ALARMS")
if not alerts_df.empty:
    for _, alert in alerts_df.iterrows():
        st.warning(f"**[{alert['severity']}] {alert['title']}** — {alert['message']} ({alert['timestamp']})")
else:
    st.markdown("""
    <div style="background: rgba(158, 240, 26, 0.08); border: 1px solid rgba(158, 240, 26, 0.3); border-radius: 8px; padding: 12px 18px; color: #9ef01a;">
        ✓ Zero unacknowledged alarms. Asset is operating within healthy design envelopes.
    </div>
    """, unsafe_allow_html=True)
