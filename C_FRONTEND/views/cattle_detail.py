"""
Cattle detail page - full health analytics with interactive Plotly charts.
"""

import streamlit as st
from datetime import datetime, timedelta
from utils.translations import t
from utils.auth import get_lang, get_token, navigate_to
from utils.theme import get_palette, health_color, health_bg
from services.api_client import (
    api_get_cattle, api_get_cattle_latest, api_get_cattle_recent,
    api_get_cattle_last_hour, api_get_cattle_range, api_get_health_events,
)
from components.navbar import render_navbar
from components.charts import (
    build_overview_chart, build_acceleration_chart,
    build_gyroscope_chart, build_heart_signal_chart, build_gauge,
)


def render():
    lang = get_lang()
    token = get_token()
    cid = st.session_state.get("selected_cattle_cid")
    p = get_palette()

    render_navbar()

    if not cid:
        st.warning("No cattle selected. Go back to the dashboard.")
        if st.button(f"← {t('dashboard', lang)}"):
            navigate_to("dashboard")
            st.rerun()
        return

    cattle = api_get_cattle(token, cid)
    if not cattle:
        st.error(f"Cattle with CID {cid} not found.")
        return

    latest = api_get_cattle_latest(token, cid)

    st.markdown(
        f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <div>
                <h2 style="margin: 0; color: {p['text']};">{cattle.get('name', f'Cattle {cid}')}</h2>
                <span style="color: {p['text_secondary']};">CID: {cid} · {cattle.get('breed', '')} ·
                {cattle.get('age', 0)} {t('years', lang)} · Farm: {cattle.get('farm_id', '')}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(f"← {t('dashboard', lang)}"):
        navigate_to("dashboard")
        st.rerun()

    st.markdown("---")

    if latest:
        temp = latest.get("temperature", 0)
        heart = latest.get("heart", {})
        bpm = heart.get("bpm", 0)
        accel = latest.get("accel", {})
        import math
        activity = math.sqrt(accel.get("ax", 0)**2 + accel.get("ay", 0)**2 + accel.get("az", 0)**2)

        st.subheader("📊 Current Readings")
        g1, g2, g3 = st.columns(3)
        with g1:
            fig = build_gauge(temp, f"🌡️ {t('temperature', lang)} (°C)", 20, 45, {"low": 35.0, "high": 39.5})
            st.plotly_chart(fig, use_container_width=True)
        with g2:
            fig = build_gauge(bpm, f"❤️ {t('heart_rate', lang)} (BPM)", 0, 150, {"low": 30.0, "high": 100.0})
            st.plotly_chart(fig, use_container_width=True)
        with g3:
            fig = build_gauge(activity, f"{t('activity', lang)}", 0, 25000, {"low": 500, "high": 20000})
            st.plotly_chart(fig, use_container_width=True)

        st.caption(f"{t('last_updated', lang)}: {str(latest.get('timestamp_iso', ''))[:19]}")
    else:
        st.info(f"ℹ️ {t('no_data', lang)} — no sensor readings yet.")

    st.markdown("---")

    st.subheader("📈 Health Data Trends")

    time_option = st.radio(
        "Select time range:",
        [t("last_hour", lang), t("last_24h", lang), "Recent 500", t("custom_range", lang)],
        horizontal=True,
    )

    readings = []
    with st.spinner(t("loading", lang)):
        if time_option == t("last_hour", lang):
            readings = api_get_cattle_last_hour(token, cid) or []
        elif time_option == t("last_24h", lang):
            end = datetime.utcnow()
            start = end - timedelta(hours=24)
            readings = api_get_cattle_range(token, cid, start.isoformat(), end.isoformat()) or []
        elif time_option == "Recent 500":
            readings = api_get_cattle_recent(token, cid, limit=500) or []
            readings.reverse()
        elif time_option == t("custom_range", lang):
            col_start, col_end = st.columns(2)
            with col_start:
                start_date = st.date_input("Start date", value=datetime.now() - timedelta(days=1))
                start_time = st.time_input("Start time", value=datetime.min.time())
            with col_end:
                end_date = st.date_input("End date", value=datetime.now())
                end_time = st.time_input("End time", value=datetime.now().time())

            if st.button("Fetch Data"):
                start_dt = datetime.combine(start_date, start_time)
                end_dt = datetime.combine(end_date, end_time)
                readings = api_get_cattle_range(token, cid, start_dt.isoformat(), end_dt.isoformat()) or []

    if readings:
        st.caption(f"Showing {len(readings)} readings")

        fig = build_overview_chart(readings)
        st.plotly_chart(fig, use_container_width=True)

        tab1, tab2, tab3 = st.tabs([
            f"{t('acceleration', lang)}",
            f"{t('gyroscope', lang)}",
            f"{t('signal', lang)}",
        ])

        with tab1:
            fig = build_acceleration_chart(readings)
            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            fig = build_gyroscope_chart(readings)
            st.plotly_chart(fig, use_container_width=True)

        with tab3:
            fig = build_heart_signal_chart(readings)
            st.plotly_chart(fig, use_container_width=True)
    elif time_option != t("custom_range", lang):
        st.info(f"ℹ️ {t('no_data', lang)} for the selected time range.")

    st.markdown("---")
    st.subheader(f"🩺 Health Event Timeline")

    events = api_get_health_events(token, cid, limit=20) or []
    if events:
        for event in events:
            status = event.get("status", "info")
            color = health_color(status, p)
            bg = health_bg(status, p)
            emoji = "🔴" if status == "bad" else "🟡" if status == "warning" else "🟢"

            st.markdown(
                f"""
                <div style="padding: 0.75rem; margin: 0.25rem 0;
                            border-left: 3px solid {color};
                            background: {bg}; border-radius: 6px; color: {p['text']};">
                    {emoji} <strong>{event.get('event', 'Health check')}</strong>
                    — Value: {event.get('value', 'N/A')}
                    <span style="color: {p['text_muted']}; font-size: 0.8rem; float: right;">
                        {str(event.get('timestamp', ''))[:19]}
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.success("✅ No health events recorded — cattle appears healthy.")
