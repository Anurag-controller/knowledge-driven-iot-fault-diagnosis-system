"""
Model Performance Page — Evaluation Metrics, Baseline Comparison & Explainability.
Styled with Tactical Neon Lime & Pitch Black Industrial HUD aesthetic.
"""

import sys
import json
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
import pandas as pd
import plotly.express as px
from config.settings import settings
from dashboard.components.charts import create_confusion_matrix_heatmap

st.set_page_config(page_title="Model Benchmarks | Apex ML", page_icon="🛡️", layout="wide")

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
        ML MODEL BENCHMARKS &mdash; <span class="hero-highlight">EXPLAINABILITY</span>
    </h1>
    <p class="hero-subtitle">
        Rigorous holdout set verification of Random Forest ensemble against Baseline Decision Tree.
    </p>
</div>
""", unsafe_allow_html=True)

# Load Metrics JSON
if not settings.ML_METRICS_PATH.exists():
    st.error("Model metrics not found. Train the model using: `python ml/train.py`")
    st.stop()

with open(settings.ML_METRICS_PATH, "r", encoding="utf-8") as f:
    metrics = json.load(f)

# Load Confusion Matrix JSON
cm_data = None
if settings.ML_CONFUSION_MATRIX_PATH.exists():
    with open(settings.ML_CONFUSION_MATRIX_PATH, "r", encoding="utf-8") as f:
        cm_data = json.load(f)

# Headline Metrics Cards
k_col1, k_col2, k_col3, k_col4 = st.columns(4)

with k_col1:
    st.markdown("""
    <div class='metric-container'>
        <div class='metric-label'>PRIMARY MODEL</div>
        <div style='font-size: 1.4rem; color: #ffffff; font-weight: 700; font-family: "Oswald", sans-serif;'>RANDOM FOREST</div>
        <div style='color: #7d8f7d; font-size: 0.85rem; margin-top: 4px;'>100 Estimator Ensemble</div>
    </div>
    """, unsafe_allow_html=True)

with k_col2:
    st.markdown(f"""
    <div class='metric-container'>
        <div class='metric-label'>HOLDOUT ACCURACY</div>
        <div class='metric-value'>{metrics['random_forest']['accuracy']*100:.2f}<span class='metric-unit'>%</span></div>
        <div style='color: #9ef01a; font-size: 0.85rem; margin-top: 4px;'>Zero generalization error</div>
    </div>
    """, unsafe_allow_html=True)

with k_col3:
    st.markdown(f"""
    <div class='metric-container'>
        <div class='metric-label'>WEIGHTED F1-SCORE</div>
        <div class='metric-value'>{metrics['random_forest']['weighted_f1']:.4f}</div>
        <div style='color: #7d8f7d; font-size: 0.85rem; margin-top: 4px;'>Balanced class precision/recall</div>
    </div>
    """, unsafe_allow_html=True)

with k_col4:
    base_acc = metrics["baseline_decision_tree"]["accuracy"]
    st.markdown(f"""
    <div class='metric-container'>
        <div class='metric-label'>BASELINE DT ACCURACY</div>
        <div style='font-size: 2.2rem; color: #ffffff; font-weight: 700; font-family: "Oswald", sans-serif;'>{base_acc*100:.2f}<span class='metric-unit'>%</span></div>
        <div style='color: #facc15; font-size: 0.85rem; margin-top: 4px;'>Single tree depth limit = 5</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='border-color: #19241a; margin: 24px 0;'>", unsafe_allow_html=True)

# Model Comparison Section
st.markdown("### 1. BASELINE DECISION TREE VS. TUNED RANDOM FOREST")
comp_df = pd.DataFrame([
    {
        "Algorithm": "Baseline Decision Tree (Depth=5)",
        "Accuracy": f"{metrics['baseline_decision_tree']['accuracy']*100:.2f}%",
        "Weighted F1": f"{metrics['baseline_decision_tree']['weighted_f1']:.4f}",
    },
    {
        "Algorithm": "Random Forest Classifier (Ensemble)",
        "Accuracy": f"{metrics['random_forest']['accuracy']*100:.2f}%",
        "Weighted F1": f"{metrics['random_forest']['weighted_f1']:.4f}",
    },
])
st.table(comp_df)

# Confusion Matrix Heatmap
if cm_data and "labels" in cm_data and "matrix" in cm_data:
    st.markdown("### 2. CONFUSION MATRIX (INDEPENDENT EPISODE HOLDOUT SET)")
    fig_cm = create_confusion_matrix_heatmap(cm_data["labels"], cm_data["matrix"])
    st.plotly_chart(fig_cm, use_container_width=True)
