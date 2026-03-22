"""
Top navbar component with logo, language toggle, and theme toggle.
"""

import streamlit as st
from utils.auth import get_lang, get_theme
from utils.translations import t
from utils.theme import get_palette
from utils.logo import logo_html

LANGUAGES = {"en": "English", "ta": "\u0ba4\u0bae\u0bbf\u0bb4\u0bcd", "hi": "\u0939\u093f\u0928\u094d\u0926\u0940"}


def render_navbar():
    lang = get_lang()
    theme = get_theme()
    p = get_palette()

    col_logo, col_title, col_theme, col_lang = st.columns([0.6, 6, 1.5, 1.5])
    with col_logo:
        st.markdown(
            f'<div style="padding-top:0.3rem;">{logo_html(height=36, margin="0")}</div>',
            unsafe_allow_html=True,
        )
    with col_title:
        st.markdown(
            f"<h2 style='margin:0; padding:0.4rem 0; color:{p['text']};'>"
            f"{t('app_title', lang)}</h2>",
            unsafe_allow_html=True,
        )
    with col_theme:
        theme_label = "Light" if theme == "dark" else "Dark"
        if st.button(theme_label, key="theme_toggle",
                     help="Switch between light and dark theme"):
            st.session_state.theme = "light" if theme == "dark" else "dark"
            st.rerun()
    with col_lang:
        options = list(LANGUAGES.keys())
        selected = st.selectbox(
            "Lang",
            options=options,
            format_func=lambda x: LANGUAGES[x],
            index=options.index(lang) if lang in options else 0,
            label_visibility="collapsed",
        )
        if selected != lang:
            st.session_state.lang = selected
            st.rerun()
