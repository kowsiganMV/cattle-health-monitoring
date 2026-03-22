"""
Cattle management page - admin only: add, edit, and manage cattle.
"""

import streamlit as st
import pandas as pd
from utils.translations import t
from utils.auth import get_lang, get_token, navigate_to
from utils.theme import get_palette
from services.api_client import api_get_cattle_list, api_create_cattle, api_update_cattle
from components.navbar import render_navbar


def render():
    lang = get_lang()
    token = get_token()
    p = get_palette()

    render_navbar()

    st.markdown(f"## 🐄 {t('cattle_management', lang)}")
    st.markdown("---")

    tab_list, tab_add, tab_edit = st.tabs([
        f"All Cattle",
        f"{t('add_cattle', lang)}",
        f"{t('edit_cattle', lang)}",
    ])

    with tab_list:
        _render_cattle_list(lang, token, p)

    with tab_add:
        _render_add_cattle(lang, token, p)

    with tab_edit:
        _render_edit_cattle(lang, token, p)


def _render_cattle_list(lang: str, token: str, p: dict):
    cattle_list = api_get_cattle_list(token) or []

    if not cattle_list:
        st.info(t("no_data", lang))
        return

    table_data = []
    for c in cattle_list:
        table_data.append({
            "CID": c["cid"],
            t("cattle_name", lang): c.get("name", ""),
            t("breed", lang): c.get("breed", ""),
            t("age", lang): c.get("age", 0),
            t("farm_id", lang): c.get("farm_id", ""),
            t("status", lang): "🟢 " + c.get("status", "") if c.get("status") == "active" else "🔴 " + c.get("status", ""),
        })

    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.caption(f"Total: {len(cattle_list)} cattle")


def _render_add_cattle(lang: str, token: str, p: dict):
    with st.form("add_cattle_form"):
        col1, col2 = st.columns(2)
        with col1:
            cid = st.number_input(t("cattle_id", lang), min_value=1, step=1)
            name = st.text_input(t("cattle_name", lang), placeholder="e.g. Lakshmi")
            breed = st.text_input(t("breed", lang), placeholder="e.g. Holstein")
        with col2:
            age = st.number_input(t("age", lang), min_value=0, step=1)
            farm_id = st.text_input(t("farm_id", lang), placeholder="e.g. farm_01")
            status = st.selectbox(t("status", lang), ["active", "inactive"])

        submitted = st.form_submit_button(
            f"{t('add_cattle', lang)}", use_container_width=True, type="primary"
        )

    if submitted:
        if not all([name, breed, farm_id]):
            st.error("Please fill in all required fields.")
            return

        with st.spinner(t("loading", lang)):
            result = api_create_cattle(token, cid, name.strip(), farm_id.strip(),
                                       breed.strip(), age, status)

        if result:
            st.success(f"✅ Cattle '{name}' (CID: {cid}) created successfully!")
            st.rerun()
        else:
            st.error("❌ Failed to create cattle. CID may already exist or server error.")


def _render_edit_cattle(lang: str, token: str, p: dict):
    cattle_list = api_get_cattle_list(token) or []

    if not cattle_list:
        st.info(t("no_data", lang))
        return

    selected_cid = st.selectbox(
        "Select cattle to edit:",
        options=[c["cid"] for c in cattle_list],
        format_func=lambda x: f"CID {x} — {next((c['name'] for c in cattle_list if c['cid'] == x), '')}",
    )

    cattle = next((c for c in cattle_list if c["cid"] == selected_cid), None)
    if not cattle:
        return

    with st.form("edit_cattle_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input(t("cattle_name", lang), value=cattle.get("name", ""))
            breed = st.text_input(t("breed", lang), value=cattle.get("breed", ""))
        with col2:
            age = st.number_input(t("age", lang), value=cattle.get("age", 0), min_value=0)
            farm_id = st.text_input(t("farm_id", lang), value=cattle.get("farm_id", ""))
            status_options = ["active", "inactive"]
            current_status = cattle.get("status", "active")
            status = st.selectbox(
                t("status", lang),
                status_options,
                index=status_options.index(current_status) if current_status in status_options else 0,
            )

        submitted = st.form_submit_button(
            f"{t('save', lang)}", use_container_width=True, type="primary"
        )

    if submitted:
        update_data = {}
        if name != cattle.get("name"):
            update_data["name"] = name.strip()
        if breed != cattle.get("breed"):
            update_data["breed"] = breed.strip()
        if age != cattle.get("age"):
            update_data["age"] = age
        if farm_id != cattle.get("farm_id"):
            update_data["farm_id"] = farm_id.strip()
        if status != cattle.get("status"):
            update_data["status"] = status

        if not update_data:
            st.info("No changes detected.")
            return

        with st.spinner(t("loading", lang)):
            result = api_update_cattle(token, selected_cid, update_data)

        if result:
            st.success(f"✅ Cattle CID {selected_cid} updated successfully!")
            st.rerun()
        else:
            st.error("❌ Failed to update cattle.")
