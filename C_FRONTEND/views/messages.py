"""
Messages / Alerts viewing page - read-only.
Shows alerts with cattle ID, owner info, and phone number.
"""

import streamlit as st
from utils.translations import t
from utils.auth import get_lang, get_token, is_admin, is_super_admin
from utils.theme import get_palette
from services.api_client import api_get_recent_alerts, api_get_cattle_list, api_get_users
from components.navbar import render_navbar


def render():
    lang = get_lang()
    token = get_token()
    p = get_palette()

    render_navbar()

    st.markdown(f"## 💬 {t('messages', lang)}")
    st.markdown("---")

    alerts = api_get_recent_alerts(token, limit=50) or []
    cattle_list = api_get_cattle_list(token) or []
    users = api_get_users(token) if (is_admin() or is_super_admin()) else []

    cattle_by_cid = {c["cid"]: c for c in cattle_list}
    farmers = [u for u in (users or []) if u.get("role") == "user"]

    if not alerts:
        st.markdown(
            f"""<div style="text-align: center; padding: 3rem;">
                <div style="font-size: 4rem;">✅</div>
                <h3 style="color: {p['status_success_border']};">No alerts or messages</h3>
                <p style="color: {p['text_secondary']};">All cattle appear healthy.</p>
            </div>""",
            unsafe_allow_html=True,
        )
        return

    st.caption(f"Showing {len(alerts)} recent alerts (view-only)")

    for alert in alerts:
        cid = alert.get("cid", "?")
        level = alert.get("status", "warning")
        emoji = "🔴" if level == "critical" else "🟡"
        ts = str(alert.get("timestamp", ""))[:19]
        details = alert.get("health_details", {})
        reasons = details.get("reasons", [])
        temp = details.get("latest_temperature")
        bpm = details.get("latest_bpm")
        count = alert.get("consecutive_count", 0)

        cattle = cattle_by_cid.get(cid, {})
        cattle_name = cattle.get("name", f"Cattle {cid}")
        farm = cattle.get("farm_id", "")

        owner_name = "—"
        owner_phone = "—"
        if farmers:
            for u in farmers:
                if farm in u.get("farm_ids", []):
                    owner_name = u.get("full_name", u.get("username", ""))
                    owner_phone = u.get("phone", "N/A")
                    break

        with st.expander(f"{emoji} **CID {cid} — {cattle_name}** | {level.upper()} | {ts}", expanded=False):
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"**{t('cattle_name', lang)}:** {cattle_name}")
                st.markdown(f"**{t('farm_id', lang)}:** {farm}")
                st.markdown(f"**{t('alert_level', lang)}:** {level.upper()}")
                st.markdown(f"**{t('consecutive_bad', lang)}:** {count}")

            with col2:
                st.markdown(f"**{t('owned_by', lang)}:** {owner_name}")
                st.markdown(f"**{t('phone_number', lang)}:** {owner_phone}")
                if temp:
                    st.markdown(f"**🌡️ {t('temperature', lang)}:** {temp:.1f}°C")
                if bpm:
                    st.markdown(f"**❤️ {t('heart_rate', lang)}:** {bpm:.0f} BPM")

            if reasons:
                st.markdown("**Details:**")
                for r in reasons:
                    st.markdown(f"- {r}")
