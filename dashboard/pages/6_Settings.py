"""
Settings & Administration Page.
Styled with Tactical Neon Lime & Pitch Black Industrial HUD aesthetic.
"""

import sys
import yaml
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
from config.settings import settings
from database.connection import db_manager

st.set_page_config(page_title="Settings & System Specs | Apex Admin", page_icon="🛡️", layout="wide")

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
        SYSTEM CONFIGURATION &mdash; <span class="hero-highlight">ASSET SPECS</span>
    </h1>
    <p class="hero-subtitle">
        Operational regimes, MQTT broker routing, hardware calibrations, and engineering tolerances.
    </p>
</div>
""", unsafe_allow_html=True)

# Operational Mode
st.markdown("### 1. OPERATIONAL REGIME")
mode_col1, mode_col2 = st.columns(2)
with mode_col1:
    st.markdown(f"""
    <div class='metric-container'>
        <div class='metric-label'>ACTIVE OPERATION MODE</div>
        <div class='metric-value'>{settings.OPERATION_MODE.upper()}</div>
        <p style="color: #7b8e7b; font-size: 0.85rem; margin-top: 8px;">
            • <strong>Simulation Mode</strong>: Dynamic 7-scenario physics generator.<br>
            • <strong>Real Hardware Mode</strong>: 12V DC motor + ESP32 edge telemetry.
        </p>
    </div>
    """, unsafe_allow_html=True)

with mode_col2:
    st.markdown("""
    <div class='metric-container'>
        <div class='metric-label'>PIPELINE SYMMETRY</div>
        <p style="color: #b5c7b5; font-size: 0.95rem; margin-top: 6px;">
            Mode toggle is controlled via <code>.env</code> (<code>OPERATION_MODE=simulation</code> or <code>OPERATION_MODE=hardware</code>). Both modes stream to the exact same ingestion validation, SQLite deduplication, and AI consensus engine.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='border-color: #19241a; margin: 20px 0;'>", unsafe_allow_html=True)

# MQTT Broker Configuration
st.markdown("### 2. MQTT BROKER & TRANSPORT")
mqtt_cfg = settings.get_effective_mqtt_config()

b_col1, b_col2, b_col3 = st.columns(3)
with b_col1:
    st.markdown(f"""
    <div class='metric-container'>
        <div class='metric-label'>BROKER TYPE</div>
        <div style='font-size: 1.5rem; color: #ffffff; font-weight: 700; font-family: "Oswald", sans-serif;'>
            {mqtt_cfg['broker_type'].replace('_', ' ').upper()}
        </div>
    </div>
    """, unsafe_allow_html=True)
with b_col2:
    st.markdown(f"""
    <div class='metric-container'>
        <div class='metric-label'>HOST ADDRESS</div>
        <div style='font-size: 1.5rem; color: #9ef01a; font-weight: 700; font-family: "Oswald", sans-serif;'>
            {mqtt_cfg['host']}
        </div>
    </div>
    """, unsafe_allow_html=True)
with b_col3:
    st.markdown(f"""
    <div class='metric-container'>
        <div class='metric-label'>PORT & SECURITY</div>
        <div style='font-size: 1.5rem; color: #ffffff; font-weight: 700; font-family: "Oswald", sans-serif;'>
            {mqtt_cfg['port']} (TLS: {mqtt_cfg['use_tls']})
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='border-color: #19241a; margin: 20px 0;'>", unsafe_allow_html=True)

# Device Specifications
st.markdown("### 3. REGISTERED ASSET SPECIFICATIONS (MOTOR 01)")
if settings.DEVICES_FILE.exists():
    with open(settings.DEVICES_FILE, "r") as f:
        dev_data = yaml.safe_load(f) or {}
    st.json(dev_data)

st.markdown("<hr style='border-color: #19241a; margin: 20px 0;'>", unsafe_allow_html=True)

# Thresholds Configuration
st.markdown("### 4. OPERATIONAL THRESHOLDS SPECIFICATION")
if settings.THRESHOLDS_FILE.exists():
    with open(settings.THRESHOLDS_FILE, "r") as f:
        thresh_data = yaml.safe_load(f) or {}
    st.json(thresh_data)
