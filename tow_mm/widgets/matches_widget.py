from collections.abc import Callable
from typing import List

import streamlit as st

from tow_mm.data_model import Match, Venue, Player
from tow_mm.db_utils import get_matches_with_participations
from tow_mm.navigation_utils import nav_to_match_lobby_button


def truncate(text: str, length: int = 10) -> str:
    return text if len(text) <= length else text[:length-3] + "..."


def display_matches_widget(venues: List[Venue], players: List[Player], match_filter: Callable[[Match,], bool] = None):
    venues_by_id = {v.id: v for v in venues}
    players_by_id = {v.id: v for v in players}
    matches_and_parts = get_matches_with_participations()

    matches_and_parts = [(match_id, match_data["match"], match_data["participations"]) for match_id, match_data in matches_and_parts.items()]
    matches_and_parts = sorted(matches_and_parts, key=lambda t: t[1].created_at)

    if not matches_and_parts:
        st.write("No matches found")
        return

    for match_id, match, participations in matches_and_parts:
        if match_filter and not match_filter(match):
            continue

        p0 = participations[0] if len(participations) > 0 else None
        p1 = participations[1] if len(participations) > 1 else None

        p0_str = "?" if p0 is None else players_by_id[p0.player_id].get_public_name()
        p1_str = "?" if p1 is None else players_by_id[p1.player_id].get_public_name()

        venue_name = venues_by_id[match.venue_id].name

        # Create a card for each match
        with st.container(border=True):
            col1, col2,col3 = st.columns([1,1,1])
            with col1:
                st.markdown(f"### Match {match_id} {'(Ranked)' if match.ranked else ''}")
            with col2:
                st.markdown(f"**State:** {match.state}")
                st.markdown(f"**Venue:** {venue_name}")
                st.markdown(f"**Fight:** {p0_str} ⚔️ {p1_str}")
            with col3:
                nav_to_match_lobby_button(match_id=match_id, extra_key="display_matches_widget")