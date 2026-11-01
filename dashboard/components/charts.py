"""
Plotly Chart Components for Tactical Industrial Monitoring.
Dark HUD aesthetic styled after athletic/tactical Spartan dashboard:
Deep pitch black, electric neon lime lines (#9ef01a), and glowing indicators.
"""

from typing import List, Optional
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

CHART_LAYOUT_DEFAULTS = dict(
    template="plotly_dark",
    paper_bgcolor="#070907",
    plot_bgcolor="#0c110d",
    margin=dict(l=40, r=30, t=40, b=40),
    font=dict(color="#f0f6fc", family="'Oswald', 'Inter', sans-serif"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)


def create_live_telemetry_chart(df: pd.DataFrame) -> go.Figure:
    """Creates a 4-row synchronized time-series subplot for Temp, Vibration, Current, RPM in Neon Lime HUD."""
    if df.empty:
        fig = go.Figure()
        fig.update_layout(**CHART_LAYOUT_DEFAULTS, title="No Telemetry Data Available")
        return fig

    # Ensure timestamp conversion
    timestamps = pd.to_datetime(
        df["timestamp"],
        format="ISO8601",
        utc=True,
        errors="coerce",
    )

    fig = make_subplots(
        rows=4,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.07,
        subplot_titles=(
            "TEMPERATURE (°C)",
            "VIBRATION RMS (g)",
            "MOTOR CURRENT (A)",
            "SPEED (RPM)",
        ),
    )

    # Tactical color palette
    # Primary: Electric Neon Lime (#9ef01a)
    # Secondary: Tactical Amber (#facc15) for current, Cyan (#06b6d4) for RPM, Coral Red for Temp spikes
    colors = {
        "temp": "#ff5252",
        "vibe": "#9ef01a",
        "current": "#facc15",
        "rpm": "#06b6d4",
    }

    # 1. Temperature
    fig.add_trace(
        go.Scatter(
            x=timestamps,
            y=df["temperature_c"],
            mode="lines+markers",
            name="Temperature",
            line=dict(color=colors["temp"], width=2.5),
            marker=dict(size=4, color="#ffffff", line=dict(color=colors["temp"], width=1.5)),
            fill="tozeroy",
            fillcolor="rgba(255, 82, 82, 0.06)",
        ),
        row=1,
        col=1,
    )

    # 2. Vibration (Hero Neon Lime Trace)
    fig.add_trace(
        go.Scatter(
            x=timestamps,
            y=df["vibration_rms_g"],
            mode="lines+markers",
            name="Vibration",
            line=dict(color=colors["vibe"], width=2.5),
            marker=dict(size=4, color="#ffffff", line=dict(color=colors["vibe"], width=1.5)),
            fill="tozeroy",
            fillcolor="rgba(158, 240, 26, 0.08)",
        ),
        row=2,
        col=1,
    )

    # 3. Current
    fig.add_trace(
        go.Scatter(
            x=timestamps,
            y=df["current_a"],
            mode="lines+markers",
            name="Current",
            line=dict(color=colors["current"], width=2.5),
            marker=dict(size=4, color="#ffffff", line=dict(color=colors["current"], width=1.5)),
            fill="tozeroy",
            fillcolor="rgba(250, 204, 21, 0.06)",
        ),
        row=3,
        col=1,
    )

    # 4. RPM
    fig.add_trace(
        go.Scatter(
            x=timestamps,
            y=df["rpm"],
            mode="lines+markers",
            name="RPM",
            line=dict(color=colors["rpm"], width=2.5),
            marker=dict(size=4, color="#ffffff", line=dict(color=colors["rpm"], width=1.5)),
            fill="tozeroy",
            fillcolor="rgba(6, 182, 212, 0.06)",
        ),
        row=4,
        col=1,
    )

    # Update grid styling
    fig.update_xaxes(gridcolor="#151d16", zerolinecolor="#19241a")
    fig.update_yaxes(gridcolor="#151d16", zerolinecolor="#19241a")

    layout_config = {
        **CHART_LAYOUT_DEFAULTS,
        "height": 680,
        "showlegend": False,
    }
    fig.update_layout(**layout_config)
    return fig


def create_gauge(
    value: float,
    min_val: float,
    max_val: float,
    title: str,
    unit: str,
    warning_thresh: float,
    crit_thresh: float,
) -> go.Figure:
    """Builds a circular gauge indicator styled with neon lime HUD tracks."""
    if warning_thresh < crit_thresh:
        steps = [
            {"range": [min_val, warning_thresh], "color": "rgba(158, 240, 26, 0.22)"},
            {"range": [warning_thresh, crit_thresh], "color": "rgba(250, 204, 21, 0.28)"},
            {"range": [crit_thresh, max_val], "color": "rgba(239, 68, 68, 0.38)"},
        ]
    else:
        steps = [
            {"range": [min_val, crit_thresh], "color": "rgba(239, 68, 68, 0.38)"},
            {"range": [crit_thresh, warning_thresh], "color": "rgba(250, 204, 21, 0.28)"},
            {"range": [warning_thresh, max_val], "color": "rgba(158, 240, 26, 0.22)"},
        ]

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            title={"text": f"{title.upper()} ({unit})", "font": {"size": 14, "color": "#859685", "family": "'Oswald', sans-serif"}},
            number={"suffix": f" {unit}", "font": {"size": 22, "color": "#9ef01a", "family": "'Oswald', sans-serif"}},
            gauge={
                "axis": {"range": [min_val, max_val], "tickcolor": "#526352"},
                "bar": {"color": "#9ef01a"},
                "bgcolor": "#0c110d",
                "borderwidth": 1,
                "bordercolor": "#19241a",
                "steps": steps,
            },
        )
    )

    gauge_layout = {
        **CHART_LAYOUT_DEFAULTS,
        "height": 190,
        "margin": dict(l=20, r=20, t=32, b=10),
    }
    fig.update_layout(**gauge_layout)
    return fig


def create_confusion_matrix_heatmap(labels: List[str], matrix: List[List[int]]) -> go.Figure:
    """Renders confusion matrix heatmap in dark lime green HUD palette."""
    custom_greens = [
        [0.0, "#070a07"],
        [0.3, "#0f1c10"],
        [0.7, "#3b6e11"],
        [1.0, "#9ef01a"],
    ]

    fig = go.Figure(
        data=go.Heatmap(
            z=matrix,
            x=labels,
            y=labels,
            colorscale=custom_greens,
            showscale=True,
            text=matrix,
            texttemplate="%{text}",
            textfont={"size": 13, "color": "#ffffff", "family": "'Oswald', sans-serif"},
        )
    )
    heatmap_layout = {
        **CHART_LAYOUT_DEFAULTS,
        "title": "CONFUSION MATRIX (HOLDOUT EVALUATION SET)",
        "xaxis_title": "Predicted Label",
        "yaxis_title": "Ground-Truth Label",
        "height": 460,
    }
    fig.update_layout(**heatmap_layout)
    return fig
