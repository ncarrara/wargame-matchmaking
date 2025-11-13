from typing import Optional

import streamlit as st

from tow_mm.db_utils import get_battle_reports
from tow_mm.navigation_utils import nav_to_battle_report_page, nav_to_page


def display_battle_report(report_id: Optional[int]):

    reports = get_battle_reports(report_ids=None if report_id is None else [report_id])
    reports_by_id = {x.id: x for x in reports}
    print(reports)
    if report_id is None:

        st.markdown(
            f"🏆 **battle report**"
        )
        for bp in reports:
            if st.button(f"Battle Reports {bp.id}", key=f"nav_to_battle_report_button_{bp.id}", width=400):
                nav_to_battle_report_page(report_id=bp.id)

    else:
        st.markdown(
            f"🏆 **battle report {report_id}**"
        )
        st.markdown(reports_by_id[report_id].content)

    if st.button("Create your own battle report", key="create_report"):
        nav_to_page("create_battle_report")