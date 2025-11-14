from contextlib import nullcontext
from typing import Optional, Dict

import streamlit as st

from tow_mm.data_model import Player
from tow_mm.db_utils import get_battle_reports
from tow_mm.navigation_utils import nav_to_battle_report_page, nav_to_page
from tow_mm.utils import draw_line


def display_battle_report(report_id: Optional[int], players: Dict[int, Player]):

    draw_line(margin=2)

    if report_id is not None:
            if st.button("All battle reports", key="all_reports"):
                nav_to_battle_report_page(report_id=None)

    if st.button("Create your own battle report", key="create_report"):
        nav_to_page("create_battle_report")



    reports = get_battle_reports(report_ids=None if report_id is None else [report_id])
    reports_by_id = {x.id: x for x in reports}

    # ---- LIST VIEW ----
    if report_id is None:
        st.markdown("## 🏆 Battle Reports")

        if not reports:
            st.info("No battle reports available yet.")
            return

        for report in reports:
            author = players[report.created_by].name
            label = f"Battle Report #{report.id} — by **{author}**"

            if st.button(label, key=f"report_btn_{report.id}"):
                nav_to_battle_report_page(report_id=report.id)

    # ---- DETAIL VIEW ----
    else:
        if report_id not in reports_by_id:
            st.error(f"Battle report {report_id} not found.")
            return

        report = reports_by_id[report_id]

        st.markdown(f"## 🏆 Battle Report #{report_id}")
        st.markdown(f"**Author:** {players[report.created_by].name}")
        st.markdown("---")
        st.markdown(report.content)
