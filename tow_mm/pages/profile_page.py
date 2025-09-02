from typing import List

import streamlit as st

from tow_mm.data_model import Player
from tow_mm.db_utils import change_pseudo
from tow_mm.utils import is_connected, draw_line, get_curr_player


def display_profile_page(player: Player, players: List[Player]):
    draw_line()
    st.markdown(f"### {player.get_public_name()}")

    players = sorted(players, key=lambda p: (p.mmr, p.name, p.id))[::-1]
    players_rank_by_id = {p.id: i + 1 for i, p in enumerate(players)}
    st.markdown(
        f"🏆 **MMR:** `{player.mmr}` | 🎯 **Rank:** `{players_rank_by_id[player.id]}`"
    )


    if is_connected() and player.id == get_curr_player().id:
        draw_line()
        st.markdown("#### My info")
        pseudo = st.text_input("Pseudo", placeholder="not defined" if player.pseudo is None else player.pseudo, max_chars=20)
        if pseudo:
            change_pseudo(player_id=player.id, pseudo=pseudo)