from typing import List

import streamlit as st

from tow_mm.navigation_utils import nav_to_match_lobby
from tow_mm.widgets.add_match_widget import add_match_widget
from tow_mm.widgets.calendar_widget import display_calendar_widget
from tow_mm.widgets.matches_widget import display_matches_widget
from tow_mm.widgets.rank_component import display_rank_widget
from tow_mm.data_model import Player, Venue
from tow_mm.utils import get_curr_player


def display_main_lobby_page(players: List[Player], venues: List[Venue]):
    display_rank_widget(players=players, current_player=get_curr_player(), top=10)

    st.subheader("Matches")
    match_id = add_match_widget(current_player=get_curr_player(), venues=venues)

    if match_id:
        nav_to_match_lobby(match_id=match_id)

    display_matches_widget(venues=venues, players=players, match_filter=lambda m: not m.is_closed())

    display_calendar_widget()

    st.markdown("## Closed matches")

    display_matches_widget(venues=venues, players=players, match_filter=lambda m: m.is_closed())