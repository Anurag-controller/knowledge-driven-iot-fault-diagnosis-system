"""
Fault Diagnosis Page — Knowledge-Driven Rule Engine & ML Hybrid Explanations.
Styled with Tactical Neon Lime & Pitch Black Industrial HUD aesthetic.
"""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
import pandas as pd
from database.repository import repo
from ml.predict import predictor

st.set_page_config(page_title="Hybrid Diagnosis | Apex Diagnostics", page_icon="🛡️", layout="wide")

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
        KNOWLEDGE-DRIVEN <span class="hero-highlight">HYBRID DIAGNOSIS</span>
    </h1>
    <p class="hero-subtitle">
        Dual-inference consensus uniting deterministic physics rules with Random Forest statistical machine learning.
    </p>
</div>
""", unsafe_allow_html=True)

# Retrieve latest predictions
preds_df = repo.get_recent_predictions(device_id="motor01", limit=20)

if preds_df.empty:
    st.info("No diagnostic predictions recorded yet. Ingestion pipeline standing by.")
    st.stop()

latest = preds_df.iloc[0]

# Hybrid Verdict Card
sev = latest["hybrid_severity"]
fault = latest["hybrid_fault"]
conf = float(latest.get("ml_confidence", 0.0))
conflict = bool(latest.get("conflict_detected", 0))

sev_color = {
    "NORMAL": "#9ef01a",
    "WARNING": "#facc15",
    "CRITICAL": "#ef4444",
}.get(sev, "#06b6d4")

st.markdown(f"""
<div style='background-color: #0d120e; border-left: 6px solid {sev_color}; border-top: 1px solid #1a261a; border-right: 1px solid #1a261a; border-bottom: 1px solid #1a261a; border-radius: 12px; padding: 22px; margin-bottom: 20px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.6);'>
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <h2 style='margin: 0; color: #ffffff; border: none; padding: 0;'>{fault}</h2>
        <span class='status-pill' style='background-color: {sev_color}22; color: {sev_color}; border: 1px solid {sev_color}; font-size: 0.95rem;'>
            SEVERITY: {sev}
        </span>
    </div>
    <div style='color: #7b8e7b; font-size: 0.85rem; margin-top: 4px;'>
        Evaluated timestamp: <code>{latest['timestamp']}</code>
    </div>
    <p style='color: #b5c7b5; margin-top: 14px; font-size: 1.05rem; line-height: 1.5;'>{latest.get('explanation', '')}</p>
    <div style='background-color: #060907; border: 1px solid #182418; border-radius: 8px; padding: 14px 16px; margin-top: 14px;'>
        <strong style='color: #9ef01a; text-transform: uppercase; font-family: "Oswald", sans-serif; letter-spacing: 0.5px;'>
            🔧 Prescriptive Maintenance Directive:
        </strong>
        <p style='color: #ffffff; margin: 4px 0 0 0;'>{latest.get('recommended_action', '')}</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Diagnostic Comparison: Rules vs ML
col_rule, col_ml = st.columns(2)

with col_rule:
    st.markdown("### 📋 PHYSICS RULE ENGINE")
    st.markdown(f"""
    <div class='metric-container'>
        <div class='metric-label'>SUSPECTED CONDITION</div>
        <div style='font-size: 1.3rem; color: #ffffff; font-weight: 700; font-family: "Oswald", sans-serif;'>{latest['rule_fault']}</div>
        <div style='color: #7d8f7d; margin-top: 6px; font-size: 0.9rem;'>
            Rule Severity: <strong style='color: {sev_color};'>{latest['rule_severity']}</strong>
        </div>
        <div style='margin-top: 8px; font-size: 0.85rem; color: #9ef01a;'>
            ✓ Evaluated against YAML Knowledge Base hypotheses
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_ml:
    st.markdown("### 🤖 RANDOM FOREST INFERENCE")

    ml_fault = latest.get("ml_fault")
    ml_available = (
        ml_fault is not None
        and str(ml_fault).strip().lower()
        not in ("", "none", "nan", "null")
    )

    if not ml_available:
        st.markdown("""
        <div class='metric-container'>
            <div class='metric-label'>PREDICTED CLASS</div>
            <div style='font-size: 1.3rem; color: #859685; font-family: "Oswald", sans-serif;'>NOT EVALUATED</div>
            <div style='color: #7d8f7d; margin-top: 6px; font-size: 0.85rem;'>
                Vibration feature unavailable on physical edge link.
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class='metric-container'>
            <div class='metric-label'>PREDICTED STATISTICAL CLASS</div>
            <div style='font-size: 1.3rem; color: #ffffff; font-weight: 700; font-family: "Oswald", sans-serif;'>{ml_fault}</div>
            <div style='color: #9ef01a; margin-top: 6px; font-size: 1.2rem; font-family: "Oswald", sans-serif;'>
                CONFIDENCE: <strong>{conf*100:.1f}%</strong>
            </div>
            <div style='margin-top: 8px;'>
                <div style='background-color: #151d16; border-radius: 6px; height: 8px; overflow: hidden;'>
                    <div style='background-color: #9ef01a; width: {conf*100}%; height: 100%; box-shadow: 0 0 8px #9ef01a;'></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Diagnostic Audit Trail Table
st.markdown("### 📜 RECENT DIAGNOSTIC AUDIT LOG")
display_cols = ["timestamp", "hybrid_fault", "hybrid_severity", "rule_fault", "ml_fault", "ml_confidence", "conflict_detected"]
st.dataframe(preds_df[display_cols], use_container_width=True)
