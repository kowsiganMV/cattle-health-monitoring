"""
User dashboard - farmer's view: their cattle with health status.
"""

import streamlit as st
from utils.translations import t
from utils.auth import get_lang, get_token, get_user, navigate_to
from utils.theme import get_palette, health_color, health_bg, ACCENT
from services.api_client import api_get_cattle_list, api_get_all_latest, api_get_recent_health_events
from components.navbar import render_navbar


def render():
    lang = get_lang()
    token = get_token()
    user = get_user()
    p = get_palette()

    render_navbar()

    st.markdown(f"### 👋 {t('welcome', lang)}, {user.get('full_name', 'User')}!")

    cattle_list = api_get_cattle_list(token) or []
    latest_data = api_get_all_latest(token) or []
    recent_events = api_get_recent_health_events(token, limit=10) or []

    latest_by_cid = {item["cid"]: item for item in latest_data}

    total = len(cattle_list)
    active = sum(1 for c in cattle_list if c.get("status") == "active")
    alert_count = len(recent_events)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(_card(p, "", t("my_cattle", lang), str(total), ACCENT["primary"]),
                    unsafe_allow_html=True)
    with col2:
        st.markdown(_card(p, "✅", t("active", lang), str(active), ACCENT["green"]),
                    unsafe_allow_html=True)
    with col3:
        st.markdown(_card(p, "", t("active_alerts", lang), str(alert_count),
                          ACCENT["red"] if alert_count > 0 else ACCENT["green"]),
                    unsafe_allow_html=True)

    st.markdown("---")

    st.subheader(f"🐄 {t('my_cattle', lang)}")

    if not cattle_list:
        st.info(t("no_data", lang))
        return

    search = st.text_input(f"{t('search', lang)}", placeholder="Search by name, breed...",
                           label_visibility="collapsed")
    filtered = cattle_list
    if search:
        s = search.lower()
        filtered = [c for c in cattle_list if s in c.get("name", "").lower() or s in c.get("breed", "").lower()]

    cols_per_row = 3
    for i in range(0, len(filtered), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, col in enumerate(cols):
            idx = i + j
            if idx >= len(filtered):
                break
            cattle = filtered[idx]
            cid = cattle["cid"]
            sensor = latest_by_cid.get(cid)

            with col:
                _render_cattle_card(cattle, sensor, lang, p)

    if recent_events:
        st.markdown("---")
        st.subheader(f"🔔 {t('recent_alerts', lang)}")
        for event in recent_events[:5]:
            level = event.get("status", "warning")
            emoji = "🟡" if level == "warning" else "🔴"
            st.markdown(
                f"""<div style="padding: 0.75rem; margin: 0.25rem 0;
                    background: {health_bg(level, p)};
                    border-left: 3px solid {health_color(level, p)};
                    border-radius: 6px; color: {p['text']};">
                    {emoji} <strong style="color: {p['text']};">Cattle {event.get('cid', '?')}</strong> —
                    {event.get('event', event.get('status', 'Alert'))}
                    <span style="color: {p['text_muted']}; font-size: 0.8rem; float: right;">
                        {str(event.get('timestamp', ''))[:19]}</span></div>""",
                unsafe_allow_html=True,
            )


def _render_cattle_card(cattle: dict, sensor: dict | None, lang: str, p: dict):
    cid = cattle["cid"]
    name = cattle.get("name", f"Cattle {cid}")
    breed = cattle.get("breed", "Unknown")
    age = cattle.get("age", 0)

    temp = sensor.get("temperature", 0) if sensor else 0
    bpm = sensor.get("heart", {}).get("bpm", 0) if sensor else 0

    h_status = "healthy"
    if temp > 39.5 or (bpm > 100 and bpm > 0) or (bpm < 30 and bpm > 0):
        h_status = "critical"
    elif temp < 35.0 and temp > 0:
        h_status = "warning"

    h_color = health_color(h_status, p)
    h_label = t(h_status if h_status != "critical" else "critical", lang)

    temp_str = f"{temp:.1f}°C" if temp > 0 else "N/A"
    bpm_str = f"{bpm:.0f}" if bpm > 0 else "N/A"
    ts = str(sensor.get("timestamp_iso", ""))[:16] if sensor else "No data"

    st.markdown(
        f"""<div style="background: {p['card_bg']}; border: 1px solid {p['card_border']};
            border-radius: 10px; padding: 1rem; margin-bottom: 0.75rem;
            box-shadow: 0 1px 3px {p['card_shadow']};">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: 700; font-size: 1.1rem; color: {p['text']};">{name}</span>
                <span style="background: {h_color}; color: #fff; padding: 2px 8px;
                    border-radius: 12px; font-size: 0.75rem; font-weight: 600;">{h_label}</span></div>
            <div style="color: {p['text_secondary']}; font-size: 0.85rem; margin-top: 0.5rem;">
                {t('breed', lang)}: {breed} · {t('age', lang)}: {age} {t('years', lang)}</div>
            <div style="display: flex; gap: 0.75rem; margin-top: 0.75rem;">
                <div style="flex:1; text-align:center; background: {p['metric_inner_bg']};
                    padding: 0.5rem; border-radius: 6px;">
                    <div style="font-size: 0.7rem; color: {p['text_muted']};">🌡️ Temp</div>
                    <div style="font-weight: 600; color: {p['text']};">{temp_str}</div></div>
                <div style="flex:1; text-align:center; background: {p['metric_inner_bg']};
                    padding: 0.5rem; border-radius: 6px;">
                    <div style="font-size: 0.7rem; color: {p['text_muted']};">❤️ BPM</div>
                    <div style="font-weight: 600; color: {p['text']};">{bpm_str}</div></div></div>
            <div style="color: {p['text_muted']}; font-size: 0.7rem; margin-top: 0.5rem;">
                {t('last_updated', lang)}: {ts}</div></div>""",
        unsafe_allow_html=True,
    )

    if st.button(f"{t('view_details', lang)}", key=f"view_{cid}", use_container_width=True):
        navigate_to("cattle_detail", selected_cattle_cid=cid)
        st.rerun()


def _card(p: dict, icon: str, label: str, value: str, color: str) -> str:
    return f"""
    <div style="background: {p['card_bg']}; border: 1px solid {p['card_border']};
                border-radius: 10px; padding: 1.25rem; text-align: center;
                box-shadow: 0 1px 3px {p['card_shadow']};">
        <div style="font-size: 1.5rem;">{icon}</div>
        <div style="font-size: 1.8rem; font-weight: 700; color: {color};">{value}</div>
        <div style="color: {p['text_secondary']}; font-size: 0.85rem;">{label}</div>
    </div>"""
