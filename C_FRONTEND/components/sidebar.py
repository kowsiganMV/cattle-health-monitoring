"""
Sidebar navigation component with role-based menu items.
"""

import streamlit as st
from utils.auth import (
    is_super_admin, is_admin, is_user,
    get_user, get_lang, get_effective_role,
    logout_user, navigate_to,
)
from utils.translations import t
from utils.theme import get_palette
from utils.logo import logo_html


def render_sidebar():
    lang = get_lang()
    user = get_user()
    eff_role = get_effective_role()
    p = get_palette()

    role_labels = {
        "super_admin": ("S.Admin", t("super_admin", lang)),
        "admin": ("Admin", t("admin", lang)),
        "user": ("User", t("user", lang)),
    }
    role_tag, role_label = role_labels.get(eff_role, ("User", "User"))

    with st.sidebar:
        # Logo at top of sidebar
        st.markdown(
            f"""
            <div style="text-align:center; padding: 0.75rem 0 0.25rem;">
                {logo_html(height=56)}
                <div style="font-size: 0.65rem; color: {p['sidebar_muted']}; letter-spacing: 0.5px;
                     margin-top: 4px;">Cattle Health Monitor</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")

        # User card
        st.markdown(
            f"""
            <div style="padding: 0.5rem 0.75rem; background: {p['status_info_bg']};
                        border: 1px solid {p['border_subtle']}; border-radius: 8px; margin-bottom: 1rem;">
                <div style="font-weight: 600; color: {p['sidebar_text']}; font-size: 0.9rem;">
                    {user.get('full_name', 'User')}</div>
                <div style="font-size: 0.7rem; color: {p['sidebar_muted']};">
                    {role_label}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        current = st.session_state.get("current_page", "dashboard")

        if st.button(f"\U0001f4ca {t('dashboard', lang)}", use_container_width=True,
                     type="primary" if current == "dashboard" else "secondary"):
            navigate_to("dashboard")
            st.rerun()

        if st.button(f"\U0001f514 {t('alerts', lang)}", use_container_width=True,
                     type="primary" if current == "alerts" else "secondary"):
            navigate_to("alerts")
            st.rerun()

        if st.button(f"\U0001f4ac {t('messages', lang)}", use_container_width=True,
                     type="primary" if current == "messages" else "secondary"):
            navigate_to("messages")
            st.rerun()

        if st.button(f"\U0001f464 {t('profile', lang)}", use_container_width=True,
                     type="primary" if current == "profile" else "secondary"):
            navigate_to("profile")
            st.rerun()

        # Super Admin only
        if is_super_admin():
            st.markdown("---")
            st.markdown(
                f'<div style="font-size: 0.65rem; color: {p["sidebar_accent"]}; text-transform: uppercase; '
                f'letter-spacing: 1.5px; margin-bottom: 0.5rem; font-weight: 700;">'
                f'\U0001f6e1\ufe0f ADMINISTRATION</div>',
                unsafe_allow_html=True,
            )

            if st.button(f"\U0001f5fa\ufe0f {t('mapping_view', lang)}", use_container_width=True,
                         type="primary" if current == "mapping" else "secondary"):
                navigate_to("mapping")
                st.rerun()

            if st.button(f"\u2795 {t('create_admin', lang)}", use_container_width=True,
                         type="primary" if current == "admin_management" else "secondary"):
                navigate_to("admin_management")
                st.rerun()

            if st.button(f"\U0001f465 {t('user_management', lang)}", use_container_width=True,
                         type="primary" if current == "user_management" else "secondary"):
                navigate_to("user_management")
                st.rerun()

            if st.button(f"\U0001f404 {t('cattle_management', lang)}", use_container_width=True,
                         type="primary" if current == "cattle_management" else "secondary"):
                navigate_to("cattle_management")
                st.rerun()

        # Admin only
        elif is_admin() and not is_super_admin():
            st.markdown("---")
            st.markdown(
                f'<div style="font-size: 0.65rem; color: {p["sidebar_muted"]}; text-transform: uppercase; '
                f'letter-spacing: 1.5px; margin-bottom: 0.5rem; font-weight: 700;">'
                f'\u2695\ufe0f MANAGEMENT</div>',
                unsafe_allow_html=True,
            )

            if st.button(f"\u2795 {t('create_user', lang)}", use_container_width=True,
                         type="primary" if current == "user_management" else "secondary"):
                navigate_to("user_management")
                st.rerun()

            if st.button(f"\U0001f404 {t('cattle_management', lang)}", use_container_width=True,
                         type="primary" if current == "cattle_management" else "secondary"):
                navigate_to("cattle_management")
                st.rerun()

        # Logout
        st.markdown("---")
        if st.button(f"\U0001f6aa {t('logout', lang)}", use_container_width=True):
            logout_user()
            st.rerun()
