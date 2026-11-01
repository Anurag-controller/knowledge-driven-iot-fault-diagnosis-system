"""
Live Monitoring Page — Real-Time Telemetry Streaming & Scenario Controls.
Styled with Tactical Neon Lime & Pitch Black Industrial HUD aesthetic.
"""

import sys
import time
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
import pandas as pd
from config.settings import settings
from database.repository import repo
from simulation.scenarios import MotorScenario
from ingestion.mqtt_client import ManagedMQTTClient
from dashboard.components.charts import create_live_telemetry_chart

st.set_page_config(page_title="Live Telemetry | Apex Monitoring", page_icon="🛡️", layout="wide")

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
        LIVE TELEMETRY STREAM &mdash; <span class="hero-highlight">MOTOR 01</span>
    </h1>
    <p class="hero-subtitle">
        Sub-second high-frequency multi-sensor oscilloscope stream with dynamic fault injection.
    </p>
</div>
""", unsafe_allow_html=True)

# Scenario Injection Toolbar
with st.expander("🎮 SIMULATION SCENARIO & FAULT INJECTION CONTROLS", expanded=True):
    ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([2, 1, 1])

    with ctrl_col1:
        selected_scenario = st.selectbox(
            "Select Scenario to Inject into Simulation:",
            options=[s.value for s in MotorScenario],
            format_func=lambda x: f"{x.replace('_', ' ').title()}",
            key="selected_scenario_box",
        )

    with ctrl_col2:
        st.write("")
        st.write("")
        if st.button("INJECT SCENARIO", type="primary", use_container_width=True):
            cfg = settings.get_effective_mqtt_config()
            cmd_client = ManagedMQTTClient(f"dash_cmd_{int(time.time())}", cfg)
            if cmd_client.connect(timeout=2):
                cmd_payload = {"command": "set_scenario", "scenario": selected_scenario}
                cmd_client.publish(settings.get_commands_topic("motor01"), cmd_payload)
                cmd_client.disconnect()
                st.success(f"Dispatched scenario command: '{selected_scenario.upper()}'")
            else:
                st.error("Could not reach MQTT broker to send scenario command.")

    with ctrl_col3:
        st.write("")
        st.write("")
        auto_refresh = st.checkbox("Auto-Refresh (1s)", value=True)

# Fetch latest 60 readings from SQLite
readings_df = repo.get_recent_readings(device_id="motor01", limit=60)

if readings_df.empty:
    st.info("No live telemetry points stored yet. Ingestion service standing by.")
else:
    latest = readings_df.iloc[-1]
    
    # Check freshness (offline indicator)
    try:
        last_dt = pd.to_datetime(latest["timestamp"])
        now_dt = pd.Timestamp.now(tz="UTC")
        age_seconds = (now_dt - last_dt).total_seconds()
        is_stale = age_seconds > 10.0
    except Exception:
        is_stale = False

    if is_stale:
        st.markdown(f"""
        <div style="background: rgba(239, 68, 68, 0.15); border: 1px solid #ef4444; border-radius: 8px; padding: 10px 16px; color: #ef4444; margin-bottom: 14px;">
            ⚠️ <strong>Telemetry Link Stale / Node Offline</strong> (No reading received for {age_seconds:.0f}s)
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background: rgba(158, 240, 26, 0.1); border: 1px solid #9ef01a; border-radius: 8px; padding: 10px 16px; color: #9ef01a; margin-bottom: 14px; font-family: 'Oswald', sans-serif; letter-spacing: 0.5px;">
            🟢 <strong>TELEMETRY STREAM ACTIVE</strong> (Latency: &lt;1s | Event ID: <code>{latest.get('event_id', '')[:12]}...</code>)
        </div>
        """, unsafe_allow_html=True)

    # Render synchronized 4-row live time-series chart
    fig = create_live_telemetry_chart(readings_df)
    st.plotly_chart(fig, use_container_width=True)

    # Telemetry Data Table
    with st.expander("VIEW RAW TELEMETRY LOG (LAST 15 FRAMES)"):
        st.dataframe(
            readings_df.tail(15)[["timestamp", "temperature_c", "vibration_rms_g", "current_a", "rpm", "sensor_status", "event_id"]],
            use_container_width=True,
        )

# Auto-refresh loop
if auto_refresh:
    time.sleep(1.0)
    st.rerun()
