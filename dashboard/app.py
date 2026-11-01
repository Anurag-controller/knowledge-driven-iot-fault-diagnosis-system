"""
Streamlit Multi-Page Main Application.
Styled with Tactical Neon Lime & Pitch Black Industrial HUD aesthetic.
"""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
from config.settings import settings
from backend.auth.security import auth_manager

st.set_page_config(
    page_title="Apex Condition Monitoring | IoT Diagnostics",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load custom CSS
css_path = Path(__file__).parent / "styles" / "theme.css"
if css_path.exists():
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Session state initialization
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "username" not in st.session_state:
    st.session_state["username"] = None
if "role" not in st.session_state:
    st.session_state["role"] = None


def render_login_form():
    col1, col2, col3 = st.columns([1, 1.8, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; margin-top: 40px; margin-bottom: 25px;">
            <div style="font-size: 3.5rem; filter: drop-shadow(0 0 16px rgba(158, 240, 26, 0.6));">🛡️</div>
            <div style="font-family: 'Oswald', sans-serif; font-size: 1.1rem; color: #9ef01a; letter-spacing: 3px; font-weight: 700; text-transform: uppercase;">
                DISCIPLINE OVER DOWNTIME
            </div>
            <h1 style="font-size: 2.6rem; margin: 6px 0; color: #ffffff;">OPERATOR ACCESS PORTAL</h1>
            <p style="color: #7d8f7d; font-size: 0.95rem;">Knowledge-Driven IoT Fault Diagnosis System — 12V DC Motor Asset</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
        st.markdown("<h3 style='margin-top: 0; color: #ffffff;'>SECURE OPERATOR LOGIN</h3>", unsafe_allow_html=True)
        username = st.text_input("Username", key="login_username", placeholder="Enter username")
        password = st.text_input("Password", type="password", key="login_password", placeholder="Enter password")
        
        st.write("")
        if st.button("AUTHENTICATE & ENTER", type="primary", use_container_width=True):
            if username and password:
                session = auth_manager.authenticate_user(username, password)
                if session and "error" not in session:
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = session["username"]
                    st.session_state["role"] = session["role"]
                    st.session_state["token"] = session["token"]
                    st.success(f"Verified identity: {session['username'].upper()} ({session['role'].upper()})")
                    st.rerun()
                elif session and "error" in session:
                    st.error(session["error"])
                else:
                    st.error("Access denied. Invalid credentials.")
            else:
                st.warning("Please supply both operator username and credential.")
        
        st.markdown("<hr style='border-color: #19241a; margin: 18px 0;'>", unsafe_allow_html=True)
        st.markdown("""
        <div style="font-size: 0.85rem; color: #728472; line-height: 1.6;">
            <div style="color: #9ef01a; font-weight: 600; text-transform: uppercase; margin-bottom: 4px;">System Credentials:</div>
            • <strong>Admin:</strong> <code>admin</code> / <code>Admin@2026</code><br>
            • <strong>Operator:</strong> <code>operator</code> / <code>Operator@2026</code>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


def main():
    if not st.session_state["authenticated"]:
        render_login_form()
        return

    # Sidebar Header with Spartan Motif
    st.sidebar.markdown("""
    <div class="spartan-badge">
        <div class="spartan-icon">🛡️</div>
        <div>
            <div class="spartan-text">APEX MONITOR</div>
            <div class="spartan-subtext">DISCIPLINE OVER DOWNTIME</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown(f"**OPERATOR:** `{st.session_state['username'].upper()}` (`{st.session_state['role'].upper()}`)")
    
    # Connection badge
    mqtt_cfg = settings.get_effective_mqtt_config()
    broker_label = "HiveMQ Cloud (TLS)" if mqtt_cfg["broker_type"] == "hivemq_cloud" else f"Local Mosquitto ({settings.LOCAL_MQTT_PORT})"
    st.sidebar.caption(f"BROKER: **{broker_label}**")
    st.sidebar.caption(f"MODE: **{settings.OPERATION_MODE.upper()}**")

    if st.sidebar.button("SIGN OUT", use_container_width=True):
        st.session_state["authenticated"] = False
        st.session_state["username"] = None
        st.session_state["role"] = None
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.markdown("#### NAVIGATION")

    # Spartan Motto in Sidebar Footer
    st.sidebar.markdown("""
    <div class="motto-card">
        "The standard you walk past is the standard you accept.<br>Relentless condition-based precision."
    </div>
    """, unsafe_allow_html=True)

    # Hero Banner
    st.markdown("""
    <div class="hero-header">
        <h1 class="hero-title">
            PRECISION TODAY,<br>
            <span class="hero-highlight">RELIABILITY TOMORROW</span>
        </h1>
        <p class="hero-subtitle">
            Continuous condition-based monitoring is the bridge between real-time physics telemetry and zero unplanned industrial downtime.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Quick Navigation Cards matching Spartan Module grid
    st.markdown("### SYSTEM MODULES & APEX MONITORING")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class="metric-container">
            <div class="metric-label">ASSET HEALTH</div>
            <div class="metric-value">98.4<span class="metric-unit">%</span></div>
            <p style="color: #7d8f7d; font-size: 0.85rem; margin-top: 8px;">Station 01 Feed Motor nominal operating envelope.</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="metric-container">
            <div class="metric-label">DIAGNOSTIC CONSENSUS</div>
            <div class="metric-value">100<span class="metric-unit">%</span></div>
            <p style="color: #7d8f7d; font-size: 0.85rem; margin-top: 8px;">Physics rules & ML Random Forest agreement.</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="metric-container">
            <div class="metric-label">UPTIME STREAK</div>
            <div class="metric-value">47<span class="metric-unit">DAYS</span></div>
            <p style="color: #7d8f7d; font-size: 0.85rem; margin-top: 8px;">Continuous telemetry stream without trip.</p>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class="metric-container">
            <div class="metric-label">ACTIVE ALARMS</div>
            <div class="metric-value" style="color: #facc15;">0<span class="metric-unit">UNACK</span></div>
            <p style="color: #7d8f7d; font-size: 0.85rem; margin-top: 8px;">All debounced alarms nominal.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    Use the navigation menu in the left sidebar to access:
    - **1 Overview**: Executive telemetry KPIs, analog tolerance envelopes, and active fault hypotheses.
    - **2 Live Monitoring**: Real-time oscilloscope charts and dynamic scenario fault injection controls.
    - **3 Fault Diagnosis**: Hybrid physics rule reasoning and Random Forest consensus verdicts.
    - **4 Historical Analytics**: Persistent database queries, multi-variable overlays, and CSV export.
    - **5 Alerts**: Industrial debounced alarm queue ($N=3$, 15s cooldown) and operator audit logs.
    - **6 Settings**: MQTT broker telemetry parameters, motor rating thresholds, and hardware modes.
    - **7 Model Performance**: Benchmark holdout metrics and confusion matrix explainability.
    """)


if __name__ == "__main__":
    main()
