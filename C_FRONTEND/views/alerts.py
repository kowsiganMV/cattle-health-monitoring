"""
Alerts page - view-only alert history with owner info.
Health evaluation available to super admin only.
"""

import streamlit as st
import pandas as pd
from utils.translations import t
from utils.auth import get_lang, get_token, is_super_admin, is_admin
from utils.theme import get_palette, health_color, health_bg
from services.api_client import (
    api_get_cattle_list, api_get_recent_alerts, api_get_cattle_alerts,
    api_get_alert_counter, api_evaluate_cattle, api_evaluate_all,
    api_get_users,
)
from components.navbar import render_navbar


def render():
    lang = get_lang()
    token = get_token()
    p = get_palette()

    render_navbar()

    st.markdown(f"## 🔔 {t('alerts', lang)}")
    st.markdown("---")

    tabs = [f"{t('recent_alerts', lang)}", f"Cattle Alerts"]
    if is_super_admin():
        tabs.append(f"{t('evaluate_health', lang)}")

    active_tabs = st.tabs(tabs)

    with active_tabs[0]:
        _render_recent_alerts(lang, token, p)

    with active_tabs[1]:
        _render_cattle_alerts(lang, token, p)

    if is_super_admin() and len(active_tabs) > 2:
        with active_tabs[2]:
            _render_evaluate(lang, token, p)


def _render_recent_alerts(lang: str, token: str, p: dict):
    alerts = api_get_recent_alerts(token, limit=50) or []
    cattle_list = api_get_cattle_list(token) or []
    users = api_get_users(token) if (is_admin() or is_super_admin()) else []

    cattle_by_cid = {c["cid"]: c for c in cattle_list}
    farmers = [u for u in (users or []) if u.get("role") == "user"]

    if not alerts:
        st.success("✅ No recent alerts — all cattle appear healthy!")
        return

    for a in alerts:
        cid = a.get("cid", "?")
        level = a.get("status", "warning")
        emoji = "🔴" if level == "critical" else "🟡"
        ts = str(a.get("timestamp", ""))[:19]
        count = a.get("consecutive_count", 0)
        details = a.get("health_details", {})

        cattle = cattle_by_cid.get(cid, {})
        cattle_name = cattle.get("name", f"Cattle {cid}")
        farm = cattle.get("farm_id", "")

        owner = "—"
        for u in farmers:
            if farm in u.get("farm_ids", []):
                owner = u.get("full_name", u.get("username", ""))
                break

        with st.expander(f"{emoji} CID {cid} — {cattle_name} | {level.upper()} | {ts}"):
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**Level:** {level.upper()}")
                st.markdown(f"**Bad readings:** {count}")
                st.markdown(f"**Farm:** {farm}")
            with c2:
                st.markdown(f"**Owner:** {owner}")
                temp = details.get("latest_temperature")
                bpm = details.get("latest_bpm")
                if temp:
                    st.markdown(f"**🌡️ Temp:** {temp:.1f}°C")
                if bpm:
                    st.markdown(f"**❤️ BPM:** {bpm:.0f}")

            reasons = details.get("reasons", [])
            if reasons:
                for r in reasons:
                    st.markdown(f"- {r}")


def _render_cattle_alerts(lang: str, token: str, p: dict):
    cattle_list = api_get_cattle_list(token) or []

    if not cattle_list:
        st.info(t("no_data", lang))
        return

    selected_cid = st.selectbox(
        "Select cattle:",
        options=[c["cid"] for c in cattle_list],
        format_func=lambda x: f"CID {x} — {next((c['name'] for c in cattle_list if c['cid'] == x), '')}",
        key="alert_cattle_select",
    )

    counter = api_get_alert_counter(token, selected_cid) or {}
    consecutive = counter.get("consecutive_bad_count", 0)
    last_status = counter.get("last_status", "healthy")
    last_checked = str(counter.get("last_checked", ""))[:19]

    status_color = health_color(last_status, p)

    st.markdown(
        f"""<div style="background: {p['card_bg']}; border: 1px solid {p['card_border']};
            border-radius: 10px; padding: 1rem; margin: 1rem 0;
            box-shadow: 0 1px 3px {p['card_shadow']};">
            <div style="display: flex; justify-content: space-between; color: {p['text']};">
                <div>
                    <div style="font-size: 0.8rem; color: {p['text_muted']};">Current Status</div>
                    <div style="font-size: 1.2rem; font-weight: 700; color: {status_color};">{last_status.upper()}</div></div>
                <div style="text-align: center;">
                    <div style="font-size: 0.8rem; color: {p['text_muted']};">{t('consecutive_bad', lang)}</div>
                    <div style="font-size: 1.5rem; font-weight: 700;">{consecutive}</div></div>
                <div style="text-align: right;">
                    <div style="font-size: 0.8rem; color: {p['text_muted']};">Last Checked</div>
                    <div style="font-size: 0.9rem;">{last_checked}</div></div></div></div>""",
        unsafe_allow_html=True,
    )

    alerts = api_get_cattle_alerts(token, selected_cid, limit=30) or []
    if alerts:
        st.subheader("Alert History")
        for a in alerts:
            level = a.get("status", "warning")
            emoji = "🔴" if level == "critical" else "🟡"
            st.markdown(
                f"""<div style="padding: 0.6rem; margin: 0.2rem 0;
                    border-left: 3px solid {health_color(level, p)};
                    background: {health_bg(level, p)}; border-radius: 6px;
                    font-size: 0.85rem; color: {p['text']};">
                    {emoji} <strong>{level.upper()}</strong> — Count: {a.get('consecutive_count', 0)}
                    <span style="color: {p['text_muted']}; float: right;">{str(a.get('timestamp', ''))[:19]}</span></div>""",
                unsafe_allow_html=True,
            )
    else:
        st.success("✅ No alerts for this cattle.")


def _render_evaluate(lang: str, token: str, p: dict):
    """Health evaluation - super admin only."""
    cattle_list = api_get_cattle_list(token) or []

    st.subheader(f"🩺 {t('evaluate_health', lang)}")

    col1, col2 = st.columns([3, 1])
    with col1:
        if cattle_list:
            selected_cid = st.selectbox(
                "Select cattle to evaluate:",
                options=[c["cid"] for c in cattle_list],
                format_func=lambda x: f"CID {x} — {next((c['name'] for c in cattle_list if c['cid'] == x), '')}",
                key="eval_cattle_select",
            )
        else:
            selected_cid = None
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(f"Evaluate", type="primary", disabled=selected_cid is None):
            with st.spinner("Evaluating..."):
                result = api_evaluate_cattle(token, selected_cid)
            if result:
                _show_result(result, p)
            else:
                st.error("Evaluation failed.")

    st.markdown("---")
    st.subheader(f"{t('evaluate_all', lang)}")
    if st.button(f"{t('evaluate_all', lang)}", type="primary"):
        with st.spinner("Evaluating all cattle..."):
            result = api_evaluate_all(token)
        if result:
            st.success(f"✅ Evaluated {result.get('total_evaluated', 0)} cattle. "
                       f"Alerts: {result.get('alerts_triggered', 0)}. Emails: {result.get('emails_sent', 0)}.")
            for r in result.get("results", []):
                _show_result(r, p)
        else:
            st.error("Batch evaluation failed.")


def _show_result(result: dict, p: dict):
    status = result.get("status", "unknown")
    color = health_color(status, p)
    bg = health_bg(status, p)
    emoji = "🟢" if status == "healthy" else "🟡" if status == "warning" else "🔴"
    st.markdown(
        f"""<div style="padding: 0.75rem; margin: 0.5rem 0; border-left: 4px solid {color};
            background: {bg}; border-radius: 6px; color: {p['text']};">
            {emoji} <strong>CID {result.get('cid', '?')}</strong> — {status.upper()}
            <br><span style="color: {p['text_secondary']}; font-size: 0.85rem;">{result.get('message', '')}</span></div>""",
        unsafe_allow_html=True,
    )
