"""
Plotly chart helpers for cattle health data visualization.
Theme-aware: uses centralized palette for all colors.
"""

import math
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.theme import get_palette, CHART

SERIES = CHART


def _layout(palette: dict) -> dict:
    """Build a theme-aware Plotly layout dict."""
    return dict(
        plot_bgcolor=palette["chart_bg"],
        paper_bgcolor=palette["chart_paper"],
        font=dict(color=palette["chart_text"], size=12),
        xaxis=dict(gridcolor=palette["chart_grid"], showgrid=True),
        yaxis=dict(gridcolor=palette["chart_grid"], showgrid=True),
        margin=dict(l=50, r=20, t=40, b=40),
        legend=dict(bgcolor=palette["chart_legend_bg"],
                    bordercolor=palette["chart_legend_border"], borderwidth=1),
        hovermode="x unified",
    )


def _extract_sensor_data(readings: list) -> dict:
    """Extract time series arrays from sensor readings."""
    timestamps, temps, bpms, signals = [], [], [], []
    ax_list, ay_list, az_list = [], [], []
    gx_list, gy_list, gz_list = [], [], []
    activities = []

    for r in readings:
        timestamps.append(r.get("timestamp_iso", ""))
        temps.append(r.get("temperature", 0))

        heart = r.get("heart", {})
        bpms.append(heart.get("bpm", 0))
        signals.append(heart.get("signal", 0))

        accel = r.get("accel", {})
        ax, ay, az = accel.get("ax", 0), accel.get("ay", 0), accel.get("az", 0)
        ax_list.append(ax)
        ay_list.append(ay)
        az_list.append(az)
        activities.append(math.sqrt(ax**2 + ay**2 + az**2))

        gyro = r.get("gyro", {})
        gx_list.append(gyro.get("gx", 0))
        gy_list.append(gyro.get("gy", 0))
        gz_list.append(gyro.get("gz", 0))

    return {
        "timestamps": timestamps,
        "temperature": temps,
        "bpm": bpms,
        "signal": signals,
        "ax": ax_list, "ay": ay_list, "az": az_list,
        "gx": gx_list, "gy": gy_list, "gz": gz_list,
        "activity": activities,
    }


def build_overview_chart(readings: list) -> go.Figure:
    """Multi-panel chart with Temperature, Heart Rate, and Activity."""
    p = get_palette()
    data = _extract_sensor_data(readings)
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.06,
        subplot_titles=("🌡️ Temperature (°C)", "❤️ Heart Rate (BPM)", "Activity Level"),
    )

    fig.add_trace(go.Scatter(
        x=data["timestamps"], y=data["temperature"],
        mode="lines", name="Temperature",
        line=dict(color=SERIES["temperature"], width=1.5),
    ), row=1, col=1)

    fig.add_hline(y=39.5, line_dash="dash", line_color=SERIES["temperature"], opacity=0.5,
                  row=1, col=1, annotation_text="High (39.5°C)")
    fig.add_hline(y=35.0, line_dash="dash", line_color=SERIES["activity"], opacity=0.5,
                  row=1, col=1, annotation_text="Low (35°C)")

    fig.add_trace(go.Scatter(
        x=data["timestamps"], y=data["bpm"],
        mode="lines", name="BPM",
        line=dict(color=SERIES["bpm"], width=1.5),
    ), row=2, col=1)

    if any(b > 0 for b in data["bpm"]):
        fig.add_hline(y=100, line_dash="dash", line_color=SERIES["temperature"], opacity=0.5,
                      row=2, col=1, annotation_text="High (100)")
        fig.add_hline(y=30, line_dash="dash", line_color=SERIES["activity"], opacity=0.5,
                      row=2, col=1, annotation_text="Low (30)")

    fig.add_trace(go.Scatter(
        x=data["timestamps"], y=data["activity"],
        mode="lines", name="Activity",
        line=dict(color=SERIES["activity"], width=1.5),
        fill="tozeroy", fillcolor="rgba(33,139,255,0.08)",
    ), row=3, col=1)

    fig.add_hline(y=500, line_dash="dash", line_color=SERIES["signal"], opacity=0.5,
                  row=3, col=1, annotation_text="Low (500)")

    base = _layout(p)
    fig.update_layout(
        height=700,
        showlegend=True,
        **{k: v for k, v in base.items() if k not in ("xaxis", "yaxis")},
    )
    for i in range(1, 4):
        fig.update_xaxes(gridcolor=p["chart_grid"], showgrid=True, row=i, col=1)
        fig.update_yaxes(gridcolor=p["chart_grid"], showgrid=True, row=i, col=1)

    return fig


def build_acceleration_chart(readings: list) -> go.Figure:
    """Acceleration XYZ chart."""
    p = get_palette()
    data = _extract_sensor_data(readings)
    fig = go.Figure()

    for axis, color, label in [
        ("ax", SERIES["accel_x"], "X-axis"),
        ("ay", SERIES["accel_y"], "Y-axis"),
        ("az", SERIES["accel_z"], "Z-axis"),
    ]:
        fig.add_trace(go.Scatter(
            x=data["timestamps"], y=data[axis],
            mode="lines", name=label,
            line=dict(color=color, width=1.5),
        ))

    fig.update_layout(title="📐 Acceleration (ax, ay, az)", height=350, **_layout(p))
    return fig


def build_gyroscope_chart(readings: list) -> go.Figure:
    """Gyroscope XYZ chart."""
    p = get_palette()
    data = _extract_sensor_data(readings)
    fig = go.Figure()

    for axis, color, label in [
        ("gx", SERIES["gyro_x"], "X-axis"),
        ("gy", SERIES["gyro_y"], "Y-axis"),
        ("gz", SERIES["gyro_z"], "Z-axis"),
    ]:
        fig.add_trace(go.Scatter(
            x=data["timestamps"], y=data[axis],
            mode="lines", name=label,
            line=dict(color=color, width=1.5),
        ))

    fig.update_layout(title="🔄 Gyroscope (gx, gy, gz)", height=350, **_layout(p))
    return fig


def build_heart_signal_chart(readings: list) -> go.Figure:
    """Heart signal and peak detection chart."""
    p = get_palette()
    data = _extract_sensor_data(readings)
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=data["timestamps"], y=data["signal"],
        mode="lines", name="Signal",
        line=dict(color=SERIES["signal"], width=1),
    ))

    fig.update_layout(title="💓 Heart Signal", height=300, **_layout(p))
    return fig


def build_gauge(value: float, title: str, min_val: float, max_val: float,
                thresholds: dict = None) -> go.Figure:
    """Build a theme-aware gauge indicator for a single metric."""
    p = get_palette()
    steps = []
    if thresholds:
        low = thresholds.get("low", min_val)
        high = thresholds.get("high", max_val)
        steps = [
            dict(range=[min_val, low], color=p["gauge_low"]),
            dict(range=[low, high], color=p["gauge_normal"]),
            dict(range=[high, max_val], color=p["gauge_high"]),
        ]

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title=dict(text=title, font=dict(size=14, color=p["chart_text"])),
        gauge=dict(
            axis=dict(range=[min_val, max_val], tickcolor=p["chart_text"]),
            bar=dict(color=p["gauge_bar"]),
            bgcolor=p["gauge_bg"],
            steps=steps,
        ),
        number=dict(font=dict(color=p["chart_text"])),
    ))

    fig.update_layout(
        height=200,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor=p["chart_paper"],
        font=dict(color=p["chart_text"]),
    )
    return fig
