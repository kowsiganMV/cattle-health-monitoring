"""
Centralized theme palette — enterprise-grade light/dark color system.
Inspired by Google Material Design + Zoho + GitHub dark.
All views import `get_palette()` to get theme-aware colors.
"""

import streamlit as st

# ── Semantic status colors (same in both themes) ──
STATUS = {
    "success": "#1A7F37",
    "success_light": "#2DA44E",
    "warning": "#BF8700",
    "warning_light": "#D4A72C",
    "danger": "#CF222E",
    "danger_light": "#E5534B",
    "info": "#0969DA",
    "info_light": "#218BFF",
}

# ── Chart series colors (same in both themes) ──
CHART = {
    "temperature": "#E5534B",
    "bpm": "#2DA44E",
    "activity": "#218BFF",
    "accel_x": "#E5534B",
    "accel_y": "#2DA44E",
    "accel_z": "#218BFF",
    "gyro_x": "#D4A72C",
    "gyro_y": "#A371F7",
    "gyro_z": "#3FB950",
    "signal": "#D4A72C",
}

# ── Accent colors for metric cards (same in both themes) ──
ACCENT = {
    "primary": "#0969DA",
    "green": "#1A7F37",
    "purple": "#8250DF",
    "yellow": "#BF8700",
    "teal": "#1B7C83",
    "orange": "#BC4C00",
    "red": "#CF222E",
}


def _dark_palette() -> dict:
    """GitHub-inspired dark theme."""
    return {
        # ── Core surfaces ──
        "bg": "#0D1117",
        "surface": "#161B22",
        "surface_hover": "#1C2128",
        "surface_raised": "#21262D",
        "border": "#30363D",
        "border_subtle": "#21262D",
        "divider": "#21262D",

        # ── Text hierarchy ──
        "text": "#E6EDF3",
        "text_secondary": "#8B949E",
        "text_muted": "#6E7681",
        "text_on_accent": "#FFFFFF",

        # ── Interactive ──
        "primary": "#2F81F7",
        "primary_hover": "#388BFD",
        "primary_text": "#FFFFFF",

        # ── Cards & containers ──
        "card_bg": "#161B22",
        "card_border": "#30363D",
        "card_shadow": "rgba(0,0,0,0.3)",

        # ── Input fields ──
        "input_bg": "#0D1117",
        "input_border": "#30363D",
        "input_border_hover": "#484F58",
        "input_border_focus": "#2F81F7",
        "input_text": "#E6EDF3",
        "input_placeholder": "#6E7681",
        "input_disabled_bg": "#21262D",
        "input_disabled_text": "#6E7681",

        # ── Sidebar ──
        "sidebar_bg": "#010409",
        "sidebar_border": "#21262D",
        "sidebar_text": "#E6EDF3",
        "sidebar_muted": "#8B949E",
        "sidebar_accent": "#2F81F7",

        # ── Status (alert items, health cards) ──
        "status_success_bg": "rgba(46,160,67,0.10)",
        "status_success_border": "#2DA44E",
        "status_warning_bg": "rgba(212,167,44,0.10)",
        "status_warning_border": "#D4A72C",
        "status_danger_bg": "rgba(229,83,75,0.10)",
        "status_danger_border": "#E5534B",
        "status_info_bg": "rgba(47,129,247,0.10)",
        "status_info_border": "#2F81F7",

        # ── Badge colors ──
        "badge_success_bg": "#1A7F37",
        "badge_success_text": "#FFFFFF",
        "badge_warning_bg": "#BF8700",
        "badge_warning_text": "#FFFFFF",
        "badge_danger_bg": "#CF222E",
        "badge_danger_text": "#FFFFFF",

        # ── Charts ──
        "chart_bg": "rgba(0,0,0,0)",
        "chart_paper": "rgba(0,0,0,0)",
        "chart_text": "#E6EDF3",
        "chart_grid": "rgba(139,148,158,0.15)",
        "chart_legend_bg": "rgba(22,27,34,0.8)",
        "chart_legend_border": "#30363D",

        # ── Gauge ──
        "gauge_bar": "#2F81F7",
        "gauge_bg": "rgba(33,38,45,0.5)",
        "gauge_low": "rgba(47,129,247,0.25)",
        "gauge_normal": "rgba(46,160,67,0.25)",
        "gauge_high": "rgba(229,83,75,0.25)",

        # ── Scrollbar ──
        "scrollbar_track": "#0D1117",
        "scrollbar_thumb": "#30363D",

        # ── Metric card inner bg ──
        "metric_bg": "#161B22",
        "metric_value_text": "#E6EDF3",
        "metric_label_text": "#8B949E",
        "metric_inner_bg": "rgba(139,148,158,0.08)",
    }


def _light_palette() -> dict:
    """Google/Zoho-inspired clean light theme."""
    return {
        # ── Core surfaces ──
        "bg": "#F6F8FA",
        "surface": "#FFFFFF",
        "surface_hover": "#F3F4F6",
        "surface_raised": "#F0F2F5",
        "border": "#C9D1D9",
        "border_subtle": "#E1E4E8",
        "divider": "#D8DEE4",

        # ── Text hierarchy ──
        "text": "#1F2328",
        "text_secondary": "#57606A",
        "text_muted": "#6E7781",
        "text_on_accent": "#FFFFFF",

        # ── Interactive ──
        "primary": "#0969DA",
        "primary_hover": "#0550AE",
        "primary_text": "#FFFFFF",

        # ── Cards & containers ──
        "card_bg": "#FFFFFF",
        "card_border": "#D0D7DE",
        "card_shadow": "rgba(31,35,40,0.04)",

        # ── Input fields — stronger contrast for light theme ──
        "input_bg": "#FFFFFF",
        "input_border": "#B0B8C1",
        "input_border_hover": "#8C959F",
        "input_border_focus": "#0969DA",
        "input_text": "#1F2328",
        "input_placeholder": "#8C959F",
        "input_disabled_bg": "#F0F2F5",
        "input_disabled_text": "#8C959F",

        # ── Sidebar ──
        "sidebar_bg": "#FFFFFF",
        "sidebar_border": "#D0D7DE",
        "sidebar_text": "#1F2328",
        "sidebar_muted": "#656D76",
        "sidebar_accent": "#0969DA",

        # ── Status (alert items, health cards) ──
        "status_success_bg": "rgba(26,127,55,0.06)",
        "status_success_border": "#1A7F37",
        "status_warning_bg": "rgba(191,135,0,0.06)",
        "status_warning_border": "#BF8700",
        "status_danger_bg": "rgba(207,34,46,0.06)",
        "status_danger_border": "#CF222E",
        "status_info_bg": "rgba(9,105,218,0.06)",
        "status_info_border": "#0969DA",

        # ── Badge colors ──
        "badge_success_bg": "#1A7F37",
        "badge_success_text": "#FFFFFF",
        "badge_warning_bg": "#BF8700",
        "badge_warning_text": "#FFFFFF",
        "badge_danger_bg": "#CF222E",
        "badge_danger_text": "#FFFFFF",

        # ── Charts ──
        "chart_bg": "rgba(0,0,0,0)",
        "chart_paper": "rgba(0,0,0,0)",
        "chart_text": "#1F2328",
        "chart_grid": "rgba(31,35,40,0.08)",
        "chart_legend_bg": "rgba(255,255,255,0.9)",
        "chart_legend_border": "#D0D7DE",

        # ── Gauge ──
        "gauge_bar": "#0969DA",
        "gauge_bg": "rgba(208,215,222,0.3)",
        "gauge_low": "rgba(9,105,218,0.15)",
        "gauge_normal": "rgba(26,127,55,0.15)",
        "gauge_high": "rgba(207,34,46,0.15)",

        # ── Scrollbar ──
        "scrollbar_track": "#F6F8FA",
        "scrollbar_thumb": "#D0D7DE",

        # ── Metric card inner bg ──
        "metric_bg": "#FFFFFF",
        "metric_value_text": "#1F2328",
        "metric_label_text": "#656D76",
        "metric_inner_bg": "rgba(31,35,40,0.04)",
    }


def get_palette() -> dict:
    """Return the active theme palette."""
    theme = st.session_state.get("theme", "light")
    return _dark_palette() if theme == "dark" else _light_palette()


def health_color(status: str, palette: dict) -> str:
    """Return the appropriate color for a health status."""
    if status in ("critical", "bad", "danger"):
        return palette["status_danger_border"]
    if status == "warning":
        return palette["status_warning_border"]
    return palette["status_success_border"]


def health_bg(status: str, palette: dict) -> str:
    """Return the appropriate background for a health status."""
    if status in ("critical", "bad", "danger"):
        return palette["status_danger_bg"]
    if status == "warning":
        return palette["status_warning_bg"]
    return palette["status_success_bg"]
