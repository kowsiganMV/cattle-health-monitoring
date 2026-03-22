"""
User profile page - view and display user information.
"""

import streamlit as st
from utils.translations import t
from utils.auth import get_lang, get_token, get_user, get_effective_role
from utils.theme import get_palette
from services.api_client import api_get_me
from components.navbar import render_navbar


def render():
    lang = get_lang()
    token = get_token()
    user = get_user()
    p = get_palette()

    render_navbar()

    st.markdown(f"## 👤 {t('profile', lang)}")
    st.markdown("---")

    fresh_user = api_get_me(token)
    if fresh_user:
        user = fresh_user

    eff_role = get_effective_role()
    role_labels = {
        "super_admin": ("🛡️", t("super_admin", lang)),
        "admin": ("��‍⚕️", t("admin", lang)),
        "user": ("👤", t("user", lang)),
    }
    role_emoji, role_label = role_labels.get(eff_role, ("👤", "User"))

    st.markdown(
        f"""
        <div style="background: {p['card_bg']}; border: 1px solid {p['card_border']};
                    border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem;
                    box-shadow: 0 1px 3px {p['card_shadow']};">
            <div style="text-align: center; margin-bottom: 1rem;">
                <div style="font-size: 3rem;">{role_emoji}</div>
                <h3 style="margin: 0.5rem 0 0; color: {p['text']};">{user.get('full_name', 'User')}</h3>
                <span style="background: {p['primary']}; color: {p['primary_text']}; padding: 2px 10px;
                             border-radius: 12px; font-size: 0.8rem; font-weight: 600;">
                    {role_label}
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"**{t('username', lang)}**")
        st.text_input("username_display", value=user.get("username", ""), disabled=True, label_visibility="collapsed")

        st.markdown(f"**{t('email', lang)}**")
        st.text_input("email_display", value=user.get("email", ""), disabled=True, label_visibility="collapsed")

        st.markdown(f"**{t('full_name', lang)}**")
        st.text_input("fullname_display", value=user.get("full_name", ""), disabled=True, label_visibility="collapsed")

    with col2:
        st.markdown(f"**{t('role', lang)}**")
        st.text_input("role_display", value=role_label, disabled=True, label_visibility="collapsed")

        st.markdown(f"**{t('status', lang)}**")
        is_active = user.get("is_active", False)
        status_label = t("active", lang) if is_active else t("inactive", lang)
        st.text_input("status_display", value=f"{'🟢' if is_active else '🔴'} {status_label}",
                      disabled=True, label_visibility="collapsed")

        st.markdown(f"**{t('member_since', lang)}**")
        created = str(user.get("created_at", "N/A"))[:10]
        st.text_input("created_display", value=created, disabled=True, label_visibility="collapsed")

    st.markdown("---")
    st.subheader(f"🏠 {t('assigned_farms', lang)}")

    farm_ids = user.get("farm_ids", [])
    if farm_ids:
        cols = st.columns(min(len(farm_ids), 4))
        for i, farm in enumerate(farm_ids):
            with cols[i % len(cols)]:
                st.markdown(
                    f"""
                    <div style="background: {p['status_info_bg']}; border: 1px solid {p['border']};
                                border-radius: 8px; padding: 0.75rem; text-align: center; margin: 0.25rem 0;">
                        <div style="font-size: 1.5rem;"></div>
                        <div style="font-weight: 600; color: {p['text']};">{farm}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    else:
        st.info("No farms assigned yet.")
