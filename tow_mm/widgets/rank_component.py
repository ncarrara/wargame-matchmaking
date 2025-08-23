from typing import List
import pandas as pd
import streamlit as st

from tow_mm.data_model import Player
from tow_mm.utils import is_connected


def display_rank_widget(players: List[Player], current_player: Player, top: int = 25):
    assert top>=1
    # Show players from PostgreSQL
    st.subheader(f"Top {top} players")

    players = sorted(players, key=lambda p: (p.mmr, p.name, p.id))[::-1]

    players_rank_by_id = {p.id: i + 1 for i, p in enumerate(players)}

    if is_connected():
        st.markdown(
            f"🏆 **MMR:** `{current_player.mmr}` | 🎯 **Rank:** `{players_rank_by_id[current_player.id]}`"
        )


    df = pd.DataFrame(
        [
            {
                "MMR": p.mmr,
                "Name": p.get_public_name() + (" 🏆" if (is_connected() and p.id == current_player.id) else ""),
                "Matches": p.games_number,

            }
            for i, p in enumerate(players[:top])
        ]
    )
    st.dataframe(df)
