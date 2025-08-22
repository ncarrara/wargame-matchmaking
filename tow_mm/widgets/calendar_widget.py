from datetime import datetime

import pandas as pd
import streamlit as st
from streamlit_calendar import calendar

from tow_mm.db_utils import get_matches, get_match_participations, get_players
from tow_mm.navigation_utils import nav_to_match_lobby_button
from tow_mm.utils import draw_line


def display_calendar_widget():
    # Call this
    draw_line(margin=1)
    players = get_players()
    players_by_id = {p.id: p for p in players}

    matches = get_matches()

    events = [
        {
            # "title": f"{m.id}",
            "title": f"",
            "match_id": m.id,
            "start": m.created_at.isoformat(),
            "end": (m.created_at + pd.Timedelta(hours=1)).isoformat(),
        }
        for m in matches
    ]
    # events = []

    calendar_options = {
        "initialView": "dayGridMonth",
        "editable": False,
        "selectable": False,
        "locale":"fr",
    }

    calendar_return = calendar(events=events, options=calendar_options)

    # If user clicks on an event
    if calendar_return and "eventClick" in calendar_return:
        event_info = calendar_return["eventClick"]["event"]["extendedProps"]
        match_id = event_info["match_id"]
        dt = calendar_return['eventClick']['event']['start']
        dt = datetime.fromisoformat(dt.replace("Z", "+00:00"))
        # format to human readable
        dt_str = dt.strftime("%a, %b %d %Y at %I:%M %p")

        participants = get_match_participations(match_id=match_id)
        p0 = None if len(participants) ==0 else players_by_id[participants[0].player_id]
        p1 = None if len(participants)  < 2 else players_by_id[participants[1].player_id]
        p0_txt = '?' if p0 is None else f"{p0.name}[{p0.mmr}]"
        p1_txt = '?' if p1 is None else f"{p1.name}[{p1.mmr}]"
        if p0 is None and p1 is None:
            fight_text = "No players yet"
        else:
            fight_text = f"{p0_txt} ⚔️ {p1_txt}"

        # fight_text = f"{fight_text} {dt_str}"
        #
        # st.info(fight_text)

        fight_markdown = f"""
        ### 🗓️ {dt_str}
        #### {fight_text}
        """

        st.markdown(fight_markdown, unsafe_allow_html=True)
        nav_to_match_lobby_button(match_id=match_id, extra_key="calendar")
