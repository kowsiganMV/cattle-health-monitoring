"""
Cattle Health Monitoring System — Streamlit Frontend
Main application entry point with role-based routing and enterprise theme.
"""

import streamlit as st
from utils.auth import (
    init_session_state, is_authenticated, is_super_admin, is_admin, is_user,
    get_effective_role, get_theme,
)
from utils.theme import get_palette
from components.sidebar import render_sidebar

st.set_page_config(
    page_title="Cattle Health Monitor",
    page_icon="🐄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state
init_session_state()


def _inject_theme_css():
    """Inject enterprise-grade CSS based on current theme."""
    p = get_palette()
    theme = get_theme()

    # Secondary button colors based on theme
    if theme == "dark":
        sec_bg = "#21262D"
        sec_text = "#E6EDF3"
        sec_border = "#363B42"
        sec_hover_bg = "#30363D"
        sec_hover_border = "#8B949E"
        label_color = "#C9D1D9"
    else:
        sec_bg = "#FFFFFF"
        sec_text = "#1F2328"
        sec_border = "#C9D1D9"
        sec_hover_bg = "#F3F4F6"
        sec_hover_border = "#0969DA"
        label_color = "#1F2328"

    st.markdown(
        f"""
        <style>
        /* ══════════ GLOBAL ══════════ */
        .stApp {{
            background-color: {p['bg']} !important;
            color: {p['text']} !important;
        }}

        /* ══════════ SIDEBAR ══════════ */
        section[data-testid="stSidebar"] {{
            background-color: {p['sidebar_bg']} !important;
            border-right: 1px solid {p['sidebar_border']} !important;
        }}
        section[data-testid="stSidebar"] .stMarkdown,
        section[data-testid="stSidebar"] .stMarkdown * {{
            color: {p['sidebar_text']} !important;
        }}

        /* ══════════ TYPOGRAPHY ══════════ */
        .stMarkdown, .stMarkdown * {{
            color: {p['text']};
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: {p['text']} !important;
        }}
        .stCaption, .stCaption * {{
            color: {p['text_muted']} !important;
        }}
        /* Labels for ALL input widgets */
        label,
        .stTextInput label,
        .stTextArea label,
        .stNumberInput label,
        .stSelectbox label,
        .stMultiSelect label,
        .stDateInput label,
        .stTimeInput label,
        .stCheckbox label,
        .stRadio label,
        .stFileUploader label,
        [data-testid="stWidgetLabel"],
        [data-testid="stWidgetLabel"] * {{
            color: {label_color} !important;
        }}
        /* Help text under inputs */
        .stTooltipIcon,
        div[data-testid="stTooltipHoverTarget"] {{
            color: {p['text_muted']} !important;
        }}

        /* ══════════ BUTTONS ══════════ */

        /* ALL buttons — base */
        .stButton > button,
        .stButton > button > div,
        .stButton > button > div > p,
        .stButton > button span {{
            border-radius: 6px !important;
            font-weight: 500 !important;
            transition: all 0.15s ease !important;
        }}

        /* Secondary / default buttons */
        .stButton > button[kind="secondary"],
        .stButton > button:not([kind="primary"]) {{
            background-color: {sec_bg} !important;
            color: {sec_text} !important;
            border: 1px solid {sec_border} !important;
        }}
        .stButton > button[kind="secondary"] *,
        .stButton > button:not([kind="primary"]) * {{
            color: {sec_text} !important;
        }}
        .stButton > button[kind="secondary"]:hover,
        .stButton > button:not([kind="primary"]):hover {{
            background-color: {sec_hover_bg} !important;
            border-color: {sec_hover_border} !important;
            color: {sec_text} !important;
        }}
        .stButton > button[kind="secondary"]:hover *,
        .stButton > button:not([kind="primary"]):hover * {{
            color: {sec_text} !important;
        }}
        .stButton > button[kind="secondary"]:active,
        .stButton > button:not([kind="primary"]):active,
        .stButton > button[kind="secondary"]:focus,
        .stButton > button:not([kind="primary"]):focus {{
            background-color: {sec_hover_bg} !important;
            color: {sec_text} !important;
        }}
        .stButton > button[kind="secondary"]:active *,
        .stButton > button:not([kind="primary"]):active *,
        .stButton > button[kind="secondary"]:focus *,
        .stButton > button:not([kind="primary"]):focus * {{
            color: {sec_text} !important;
        }}

        /* Primary buttons */
        .stButton > button[kind="primary"] {{
            background-color: {p['primary']} !important;
            color: {p['primary_text']} !important;
            border: 1px solid {p['primary']} !important;
        }}
        .stButton > button[kind="primary"] *,
        .stButton > button[kind="primary"] p,
        .stButton > button[kind="primary"] div {{
            color: {p['primary_text']} !important;
        }}
        .stButton > button[kind="primary"]:hover {{
            background-color: {p['primary_hover']} !important;
            border-color: {p['primary_hover']} !important;
            color: {p['primary_text']} !important;
            transform: translateY(-1px);
            box-shadow: 0 2px 8px {p['card_shadow']};
        }}
        .stButton > button[kind="primary"]:hover * {{
            color: {p['primary_text']} !important;
        }}
        .stButton > button[kind="primary"]:active,
        .stButton > button[kind="primary"]:focus {{
            background-color: {p['primary']} !important;
            color: {p['primary_text']} !important;
        }}
        .stButton > button[kind="primary"]:active *,
        .stButton > button[kind="primary"]:focus * {{
            color: {p['primary_text']} !important;
        }}

        /* Form submit buttons */
        .stFormSubmitButton > button {{
            background-color: {p['primary']} !important;
            color: {p['primary_text']} !important;
            border: 1px solid {p['primary']} !important;
            border-radius: 6px !important;
            font-weight: 600 !important;
        }}
        .stFormSubmitButton > button *,
        .stFormSubmitButton > button p {{
            color: {p['primary_text']} !important;
        }}
        .stFormSubmitButton > button:hover {{
            background-color: {p['primary_hover']} !important;
            color: {p['primary_text']} !important;
        }}
        .stFormSubmitButton > button:hover * {{
            color: {p['primary_text']} !important;
        }}
        .stFormSubmitButton > button:active,
        .stFormSubmitButton > button:focus {{
            background-color: {p['primary']} !important;
            color: {p['primary_text']} !important;
        }}
        .stFormSubmitButton > button:active *,
        .stFormSubmitButton > button:focus * {{
            color: {p['primary_text']} !important;
        }}

        /* ══════════ INPUT FIELDS (COMPREHENSIVE) ══════════ */

        /* --- Text inputs, password, number --- */
        .stTextInput input,
        .stTextInput > div > div > input,
        .stTextArea textarea,
        .stTextArea > div > div > textarea,
        .stNumberInput input,
        .stNumberInput > div > div > input,
        .stDateInput input,
        .stTimeInput input,
        input[data-testid="stTextInput"],
        input[data-testid="stNumberInput"],
        textarea[data-testid="stTextArea"] {{
            background-color: {p['input_bg']} !important;
            border: 1px solid {p['input_border']} !important;
            color: {p['input_text']} !important;
            border-radius: 6px !important;
            -webkit-text-fill-color: {p['input_text']} !important;
            caret-color: {p['input_text']} !important;
        }}

        /* Hover on inputs */
        .stTextInput input:hover,
        .stTextArea textarea:hover,
        .stNumberInput input:hover,
        .stDateInput input:hover {{
            border-color: {p['input_border_hover']} !important;
        }}

        /* Focus on inputs */
        .stTextInput input:focus,
        .stTextInput > div > div > input:focus,
        .stTextArea textarea:focus,
        .stTextArea > div > div > textarea:focus,
        .stNumberInput input:focus,
        .stNumberInput > div > div > input:focus,
        .stDateInput input:focus {{
            border-color: {p['input_border_focus']} !important;
            box-shadow: 0 0 0 2px rgba({','.join(str(int(p['input_border_focus'][i:i+2], 16)) for i in (1,3,5))}, 0.25) !important;
            outline: none !important;
        }}

        /* Placeholder text */
        .stTextInput input::placeholder,
        .stTextArea textarea::placeholder,
        .stNumberInput input::placeholder,
        .stDateInput input::placeholder {{
            color: {p['input_placeholder']} !important;
            -webkit-text-fill-color: {p['input_placeholder']} !important;
            opacity: 1 !important;
        }}

        /* Disabled inputs */
        .stTextInput input:disabled,
        .stTextInput > div > div > input:disabled,
        .stTextArea textarea:disabled,
        .stNumberInput input:disabled {{
            background-color: {p['input_disabled_bg']} !important;
            color: {p['input_disabled_text']} !important;
            -webkit-text-fill-color: {p['input_disabled_text']} !important;
            border-color: {p['border']} !important;
            opacity: 0.8 !important;
            cursor: not-allowed !important;
        }}

        /* Number input +/- buttons */
        .stNumberInput button {{
            background-color: {p['surface']} !important;
            border-color: {p['input_border']} !important;
            color: {p['text']} !important;
        }}
        .stNumberInput button svg {{
            fill: {p['text']} !important;
            stroke: {p['text']} !important;
        }}

        /* --- Select box (dropdown) --- */
        .stSelectbox > div > div,
        .stSelectbox [data-baseweb="select"] > div {{
            background-color: {p['input_bg']} !important;
            border: 1px solid {p['input_border']} !important;
            border-radius: 6px !important;
        }}
        .stSelectbox [data-baseweb="select"] > div:hover {{
            border-color: {p['input_border_hover']} !important;
        }}
        /* Selected value text */
        .stSelectbox [data-baseweb="select"] span,
        .stSelectbox [data-baseweb="select"] div[data-testid="stMarkdownContainer"],
        .stSelectbox div[role="combobox"],
        .stSelectbox div[role="combobox"] *,
        .stSelectbox input {{
            color: {p['input_text']} !important;
            -webkit-text-fill-color: {p['input_text']} !important;
        }}
        /* Dropdown arrow icon */
        .stSelectbox svg {{
            fill: {p['text_secondary']} !important;
        }}
        /* Dropdown menu (popover) */
        [data-baseweb="popover"],
        [data-baseweb="popover"] > div {{
            background-color: {p['surface']} !important;
            border: 1px solid {p['border']} !important;
        }}
        [data-baseweb="popover"] ul {{
            background-color: {p['surface']} !important;
        }}
        [data-baseweb="popover"] li,
        [data-baseweb="popover"] li * {{
            color: {p['text']} !important;
        }}
        [data-baseweb="popover"] li:hover,
        [data-baseweb="popover"] li[aria-selected="true"] {{
            background-color: {p['surface_hover']} !important;
        }}
        /* Focused dropdown */
        .stSelectbox [data-baseweb="select"][aria-expanded="true"] > div {{
            border-color: {p['input_border_focus']} !important;
            box-shadow: 0 0 0 2px rgba({','.join(str(int(p['input_border_focus'][i:i+2], 16)) for i in (1,3,5))}, 0.25) !important;
        }}

        /* --- MultiSelect --- */
        .stMultiSelect > div > div,
        .stMultiSelect [data-baseweb="select"] > div {{
            background-color: {p['input_bg']} !important;
            border: 1px solid {p['input_border']} !important;
            border-radius: 6px !important;
        }}
        .stMultiSelect [data-baseweb="select"] > div:hover {{
            border-color: {p['input_border_hover']} !important;
        }}
        .stMultiSelect span,
        .stMultiSelect input {{
            color: {p['input_text']} !important;
            -webkit-text-fill-color: {p['input_text']} !important;
        }}
        .stMultiSelect input::placeholder {{
            color: {p['input_placeholder']} !important;
            -webkit-text-fill-color: {p['input_placeholder']} !important;
        }}
        /* Selected tags */
        .stMultiSelect [data-baseweb="tag"] {{
            background-color: {p['primary']} !important;
        }}
        .stMultiSelect [data-baseweb="tag"] span {{
            color: {p['primary_text']} !important;
            -webkit-text-fill-color: {p['primary_text']} !important;
        }}

        /* --- Date input --- */
        .stDateInput > div > div {{
            background-color: {p['input_bg']} !important;
            border: 1px solid {p['input_border']} !important;
            border-radius: 6px !important;
        }}
        .stDateInput > div > div:hover {{
            border-color: {p['input_border_hover']} !important;
        }}
        /* Calendar popup */
        [data-baseweb="calendar"] {{
            background-color: {p['surface']} !important;
            color: {p['text']} !important;
        }}
        [data-baseweb="calendar"] * {{
            color: {p['text']} !important;
        }}

        /* --- Checkbox --- */
        .stCheckbox label span {{
            color: {p['text']} !important;
        }}

        /* --- Radio buttons --- */
        .stRadio label,
        .stRadio label span {{
            color: {p['text']} !important;
        }}

        /* --- Slider --- */
        .stSlider label span {{
            color: {p['text']} !important;
        }}

        /* --- File uploader --- */
        .stFileUploader > div {{
            background-color: {p['input_bg']} !important;
            border: 1px dashed {p['input_border']} !important;
            border-radius: 6px !important;
        }}
        .stFileUploader label,
        .stFileUploader span {{
            color: {p['text']} !important;
        }}

        /* ══════════ TABS ══════════ */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 4px;
            border-bottom: 1px solid {p['border']};
        }}
        .stTabs [data-baseweb="tab"] {{
            border-radius: 6px 6px 0 0;
            padding: 8px 16px;
            color: {p['text_secondary']} !important;
        }}
        .stTabs [data-baseweb="tab"][aria-selected="true"] {{
            color: {p['text']} !important;
            border-bottom: 2px solid {p['primary']};
        }}
        .stTabs [data-baseweb="tab-panel"] {{
            color: {p['text']} !important;
        }}

        /* ══════════ EXPANDERS ══════════ */
        .streamlit-expanderHeader,
        details summary,
        details summary span {{
            color: {p['text']} !important;
        }}

        /* ══════════ ALERTS ══════════ */
        .stAlert > div {{
            color: {p['text']} !important;
        }}

        /* ══════════ DIVIDERS ══════════ */
        hr {{
            border-color: {p['divider']} !important;
        }}

        /* ══════════ DATAFRAME / TABLE (COMPREHENSIVE) ══════════ */
        .stDataFrame,
        [data-testid="stDataFrame"] {{
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid {p['border']} !important;
        }}

        /* Glide Data Grid CSS custom properties — controls canvas-rendered cells */
        [data-testid="stDataFrame"] > div,
        .dvn-scroller,
        [data-testid="stDataFrame"] [class*="glide"] {{
            --gdg-bg-cell: {p['surface']} !important;
            --gdg-bg-cell-medium: {p['surface']} !important;
            --gdg-bg-header: {p['surface_raised']} !important;
            --gdg-bg-header-has-focus: {p['surface_hover']} !important;
            --gdg-bg-header-hovered: {p['surface_hover']} !important;
            --gdg-text-dark: {p['text']} !important;
            --gdg-text-medium: {p['text_secondary']} !important;
            --gdg-text-light: {p['text_muted']} !important;
            --gdg-text-bubble: {p['text']} !important;
            --gdg-text-header: {p['text']} !important;
            --gdg-border-color: {p['border']} !important;
            --gdg-horizontal-border-color: {p['border']} !important;
            --gdg-accent-color: {p['primary']} !important;
            --gdg-accent-fg: {p['primary_text']} !important;
            --gdg-accent-light: {p['status_info_bg']} !important;
            --gdg-bg-search-result: {p['status_info_bg']} !important;
            --gdg-link-color: {p['primary']} !important;
            --gdg-cell-horizontal-padding: 8px !important;
            --gdg-cell-vertical-padding: 3px !important;
        }}

        /* Fallback: directly style any internal wrappers */
        [data-testid="stDataFrame"] > div {{
            background-color: {p['surface']} !important;
        }}
        [data-testid="stDataFrame"] canvas {{
            border-radius: 6px;
        }}

        /* Toolbar (search, download buttons) */
        [data-testid="stDataFrame"] [data-testid="stDataFrameToolbar"],
        [data-testid="stElementToolbar"] {{
            background-color: {p['surface']} !important;
            border-color: {p['border']} !important;
        }}
        [data-testid="stDataFrame"] [data-testid="stDataFrameToolbar"] button {{
            color: {p['text']} !important;
        }}
        [data-testid="stDataFrame"] [data-testid="stDataFrameToolbar"] svg {{
            fill: {p['text_secondary']} !important;
        }}

        /* st.table() — pure HTML table */
        .stTable,
        .stTable table {{
            background-color: {p['surface']} !important;
            color: {p['text']} !important;
        }}
        .stTable thead th {{
            background-color: {p['surface_raised']} !important;
            color: {p['text']} !important;
            border-bottom: 2px solid {p['border']} !important;
            font-weight: 600;
        }}
        .stTable tbody td {{
            background-color: {p['surface']} !important;
            color: {p['text']} !important;
            border-bottom: 1px solid {p['border']} !important;
        }}
        .stTable tbody tr:hover td {{
            background-color: {p['surface_hover']} !important;
        }}

        /* ══════════ DROPDOWN POPOVER (COMPREHENSIVE) ══════════ */

        /* BaseWeb popover — the floating menu */
        [data-baseweb="popover"],
        [data-baseweb="popover"] > div,
        [data-baseweb="popover"] [data-baseweb="menu"],
        [data-baseweb="popover"] [data-baseweb="list"],
        div[role="listbox"],
        div[role="listbox"] > div {{
            background-color: {p['surface']} !important;
            border: 1px solid {p['border']} !important;
            border-radius: 6px !important;
            box-shadow: 0 4px 16px {p['card_shadow']} !important;
        }}

        /* Menu items (all variants) */
        [data-baseweb="popover"] ul,
        [data-baseweb="menu"] ul,
        div[role="listbox"] ul {{
            background-color: {p['surface']} !important;
            padding: 4px 0 !important;
        }}
        [data-baseweb="popover"] li,
        [data-baseweb="popover"] li *,
        [data-baseweb="menu"] li,
        [data-baseweb="menu"] li *,
        div[role="listbox"] li,
        div[role="listbox"] li *,
        [role="option"],
        [role="option"] * {{
            color: {p['text']} !important;
            -webkit-text-fill-color: {p['text']} !important;
            background-color: {p['surface']} !important;
        }}
        /* Hovered & selected items */
        [data-baseweb="popover"] li:hover,
        [data-baseweb="popover"] li:hover *,
        [data-baseweb="menu"] li:hover,
        div[role="listbox"] li:hover,
        [role="option"]:hover,
        [role="option"][aria-selected="true"],
        [data-baseweb="popover"] li[aria-selected="true"],
        [data-baseweb="popover"] li[aria-selected="true"] *,
        li[data-highlighted="true"],
        li[data-highlighted="true"] * {{
            background-color: {p['surface_hover']} !important;
            color: {p['text']} !important;
            -webkit-text-fill-color: {p['text']} !important;
        }}

        /* "No results" text */
        [data-baseweb="menu"] [role="option"][aria-disabled="true"],
        [data-baseweb="popover"] div[class*="empty"],
        div[role="listbox"] div[class*="empty"] {{
            color: {p['text_muted']} !important;
        }}

        /* ══════════ METRIC WIDGET ══════════ */
        [data-testid="stMetricValue"] {{
            color: {p['text']} !important;
        }}
        [data-testid="stMetricLabel"] {{
            color: {p['text_secondary']} !important;
        }}
        [data-testid="stMetricDelta"] {{
            color: {p['text_secondary']} !important;
        }}

        /* ══════════ TOAST / SNACKBAR ══════════ */
        [data-testid="stToast"],
        [data-testid="stNotification"] {{
            background-color: {p['surface']} !important;
            color: {p['text']} !important;
            border: 1px solid {p['border']} !important;
        }}

        /* ══════════ SCROLLBAR ══════════ */
        ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
        ::-webkit-scrollbar-track {{ background: {p['scrollbar_track']}; }}
        ::-webkit-scrollbar-thumb {{ background: {p['scrollbar_thumb']}; border-radius: 3px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: {p['text_muted']}; }}

        /* ══════════ HIDE STREAMLIT DEFAULTS ══════════ */
        #MainMenu {{ visibility: hidden; }}
        footer {{ visibility: hidden; }}
        header {{ visibility: hidden; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def main():
    _inject_theme_css()

    if not is_authenticated():
        from views.login import render as render_login
        render_login()
        return

    render_sidebar()

    page = st.session_state.get("current_page", "dashboard")
    eff_role = get_effective_role()

    # ── Dashboard routing by role ──
    if page == "dashboard":
        if is_super_admin():
            from views.dashboard_super_admin import render
        elif is_admin():
            from views.dashboard_admin import render
        else:
            from views.dashboard_user import render
        render()

    elif page == "cattle_detail":
        from views.cattle_detail import render
        render()

    elif page == "profile":
        from views.profile import render
        render()

    elif page == "messages":
        from views.messages import render
        render()

    elif page == "alerts":
        from views.alerts import render
        render()

    # ── Super Admin pages ──
    elif page == "mapping":
        if is_super_admin():
            from views.dashboard_super_admin import render
            render()
        else:
            st.error("Access denied. Super Admin only.")

    elif page == "admin_management":
        if is_super_admin():
            from views.user_management import render
            render()
        else:
            st.error("Access denied. Super Admin only.")

    # ── Admin / Super Admin pages ──
    elif page == "cattle_management":
        if is_admin():
            from views.cattle_management import render
            render()
        else:
            st.error("Access denied. Admin only.")

    elif page == "user_management":
        if is_admin():
            from views.user_management import render
            render()
        else:
            st.error("Access denied. Admin only.")

    else:
        st.warning(f"Unknown page: {page}")


if __name__ == "__main__":
    main()
