"""
Admin dashboard - scoped to their farms: their users, cattle, and alerts.
"""

import streamlit as st
import pandas as pd
from utils.translations import t
from utils.auth import get_lang, get_token, get_user, navigate_to
from utils.theme import get_palette, health_color, health_bg, ACCENT
from services.api_client import (
    api_get_cattle_list, api_get_all_latest, api_get_users,
    api_get_recent_alerts, api_get_recent_health_events,
)
from components.navbar import render_navbar


def render():
    lang = get_lang()
    token = get_token()
    user = get_user()
    my_farms = user.get("farm_ids", [])
    p = get_palette()

    render_navbar()

    st.markdown(f"### 👋 {t('welcome', lang)}, Dr. {user.get('full_name', 'Admin')}!")

    all_cattle = api_get_cattle_list(token) or []
    latest_data = api_get_all_latest(token) or []
    all_users = api_get_users(token) or []
    recent_alerts = api_get_recent_alerts(token, limit=20) or []

    my_cattle = [c for c in all_cattle if c.get("farm_id") in my_farms]
    my_users = [u for u in all_users if u.get("role") == "user" and
                any(f in my_farms for f in u.get("farm_ids", []))]
    latest_by_cid = {item["cid"]: item for item in (latest_data or [])}

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(_card(p, "", t("total_cattle", lang), str(len(my_cattle)), ACCENT["green"]),
                    unsafe_allow_html=True)
    with c2:
        st.markdown(_card(p, "👨‍🌾", t("total_users", lang), str(len(my_users)), ACCENT["primary"]),
                    unsafe_allow_html=True)
    with c3:
        st.markdown(_card(p, "", t("assigned_farms", lang), str(len(my_farms)), ACCENT["purple"]),
                    unsafe_allow_html=True)
    with c4:
        st.markdown(_card(p, "", t("active_alerts", lang), str(len(recent_alerts)),
                          ACCENT["red"] if recent_alerts else ACCENT["green"]),
                    unsafe_allow_html=True)

    st.markdown("---")

    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.subheader(f"🐄 {t('total_cattle', lang)}")
        if my_cattle:
            table = []
            for c in my_cattle:
                cid = c["cid"]
                sensor = latest_by_cid.get(cid, {})
                temp = sensor.get("temperature", 0) if sensor else 0
                bpm = sensor.get("heart", {}).get("bpm", 0) if sensor else 0

                farm = c.get("farm_id", "")
                owners = [u for u in my_users if farm in u.get("farm_ids", [])]
                owner_name = owners[0].get("full_name", "") if owners else "Unassigned"

                health = "🟢"
                if temp > 39.5 or (bpm > 100 and bpm > 0) or (bpm < 30 and bpm > 0):
                    health = "🔴"
                elif temp < 35 and temp > 0:
                    health = "🟡"

                table.append({
                    "CID": cid,
                    t("cattle_name", lang): c.get("name", ""),
                    t("owned_by", lang): owner_name,
                    "🌡️": f"{temp:.1f}" if temp > 0 else "-",
                    "❤️": f"{bpm:.0f}" if bpm > 0 else "-",
                    "": health,
                })

            st.dataframe(pd.DataFrame(table), use_container_width=True, hide_index=True)

            selected = st.selectbox(
                f"{t('view_details', lang)}",
                options=[c["cid"] for c in my_cattle],
                format_func=lambda x: f"CID {x} — {next((c['name'] for c in my_cattle if c['cid'] == x), '')}",
            )
            if st.button(f"{t('view_details', lang)}", key="admin_view"):
                navigate_to("cattle_detail", selected_cattle_cid=selected)
                st.rerun()
        else:
            st.info(t("no_data", lang))

    with col_right:
        st.subheader(f"🔔 {t('recent_alerts', lang)}")
        if recent_alerts:
            for alert in recent_alerts[:8]:
                level = alert.get("status", "warning")
                emoji = "🔴" if level == "critical" else "🟡"
                cid = alert.get("cid", "?")

                cattle = next((c for c in my_cattle if c["cid"] == cid), None)
                owner = ""
                if cattle:
                    farm = cattle.get("farm_id", "")
                    owners = [u for u in my_users if farm in u.get("farm_ids", [])]
                    owner = owners[0].get("full_name", "") if owners else ""

                st.markdown(
                    f"""<div style="padding: 0.5rem 0.75rem; margin: 0.2rem 0;
                        background: {health_bg(level, p)};
                        border-left: 3px solid {health_color(level, p)};
                        border-radius: 6px; font-size: 0.85rem; color: {p['text']};">
                        {emoji} <strong>CID {cid}</strong> — {level.upper()}
                        {f'<br>{owner}' if owner else ''}
                        <br><span style="color: {p['text_muted']}; font-size: 0.75rem;">{str(alert.get('timestamp', ''))[:19]}</span>
                    </div>""",
                    unsafe_allow_html=True,
                )
        else:
            st.success("✅ No recent alerts.")

        st.markdown("---")
        st.subheader(f"👥 {t('total_users', lang)}")
        if my_users:
            for u in my_users:
                status_dot = "🟢" if u.get("is_active") else "🔴"
                st.markdown(
                    f"""<div style="padding: 0.4rem 0.75rem; margin: 0.2rem 0;
                        background: {p['status_info_bg']}; border: 1px solid {p['border_subtle']};
                        border-radius: 6px; font-size: 0.85rem; color: {p['text']};">
                        {status_dot} <strong>{u.get('full_name', '')}</strong>
                        <span style="color: {p['text_secondary']};"> — {u.get('email', '')}</span>
                    </div>""",
                    unsafe_allow_html=True,
                )
        else:
            st.info("No users assigned to your farms yet.")


def _card(p: dict, icon: str, label: str, value: str, color: str) -> str:
    return f"""
    <div style="background: {p['card_bg']}; border: 1px solid {p['card_border']};
                border-radius: 10px; padding: 1rem; text-align: center;
                box-shadow: 0 1px 3px {p['card_shadow']};">
        <div style="font-size: 1.3rem;">{icon}</div>
        <div style="font-size: 1.6rem; font-weight: 700; color: {color};">{value}</div>
        <div style="color: {p['text_secondary']}; font-size: 0.8rem;">{label}</div>
    </div>
    """
