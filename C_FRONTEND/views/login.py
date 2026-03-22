"""
Login page - sign-in only (no public registration).
User creation is handled by Super Admin / Admin.
"""

import streamlit as st
from utils.translations import t
from utils.auth import login_user, get_lang, get_theme
from utils.theme import get_palette
from utils.logo import logo_html
from services.api_client import api_login

LANGUAGES = {"en": "English", "ta": "\u0ba4\u0bae\u0bbf\u0bb4\u0bcd", "hi": "\u0939\u093f\u0928\u094d\u0926\u0940"}


def render():
    lang = get_lang()
    theme = get_theme()
    p = get_palette()

    # Top bar: spacer | theme toggle | language selector
    col_spacer, col_theme, col_lang = st.columns([6, 1.5, 1.5])
    with col_theme:
        theme_label = "Light" if theme == "dark" else "Dark"
        if st.button(theme_label, key="login_theme_toggle",
                     help="Switch between light and dark theme"):
            st.session_state.theme = "light" if theme == "dark" else "dark"
            st.rerun()
    with col_lang:
        options = list(LANGUAGES.keys())
        selected = st.selectbox(
            "Language",
            options=options,
            format_func=lambda x: LANGUAGES[x],
            index=options.index(lang) if lang in options else 0,
            label_visibility="collapsed",
        )
        if selected != lang:
            st.session_state.lang = selected
            st.rerun()

    # Centered login card
    spacer_l, center, spacer_r = st.columns([1, 2, 1])
    with center:
        # Logo + branding
        st.markdown(
            f"""
            <div style="text-align: center; margin: 1rem 0 0.5rem;">
                {logo_html(height=120)}
                <h1 style="margin: 0.75rem 0 0; color: {p['text']}; font-size: 1.8rem;">
                    {t('app_title', lang)}</h1>
                <p style="color: {p['text_secondary']}; margin-top: 0.25rem; font-size: 0.9rem;">
                    Cattle Health Monitoring System</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div style="background: {p['card_bg']}; border: 1px solid {p['card_border']};
                 border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem;
                 box-shadow: 0 2px 8px {p['card_shadow']};">
                <h3 style="margin: 0 0 0.25rem; color: {p['text']};">Sign In</h3>
                <p style="color: {p['text_muted']}; font-size: 0.85rem; margin: 0;">
                    Sign in to access your dashboard</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("login_form"):
            username = st.text_input(
                t("username", lang), placeholder="Enter username",
                help="Your account username"
            )
            password = st.text_input(
                t("password", lang), type="password", placeholder="Enter password",
                help="Your account password"
            )
            submitted = st.form_submit_button(
                t("sign_in", lang), use_container_width=True, type="primary"
            )

        if submitted:
            if not username or not password:
                st.error("Please fill in all fields.")
                return

            with st.spinner(t("loading", lang)):
                result = api_login(username.strip(), password)

            if result:
                token = result.get("access_token", "")
                user = result.get("user", {})
                login_user(token, user)
                st.success(f"{t('welcome', lang)}, {user.get('full_name', username)}!")
                st.session_state.current_page = "dashboard"
                st.rerun()
            else:
                st.error("Invalid username or password. Please try again.")

        st.markdown(
            f"""
            <div style="text-align: center; margin-top: 1.5rem; color: {p['text_muted']}; font-size: 0.8rem;">
                Don't have an account? Contact your administrator.
            </div>
            """,
            unsafe_allow_html=True,
        )
