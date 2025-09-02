from contextlib import nullcontext
from typing import Optional

import streamlit as st
from streamlit_js_eval import streamlit_js_eval

from tow_mm.db_utils import Player, insert_or_get_player
from tow_mm.navigation_utils import nav_to_main_lobby_button, nav_to_player_id_page, nav_to_ranking_page, \
    nav_to_contact_page, nav_to_simulator_page


def display_header()-> Optional[Player]:

    col1, _, col2 = st.columns([4,1, 1])

    with col1:
        st.image("static/logos/banner.png")

    player = None

    screen_width = streamlit_js_eval(js_expressions='screen.width', key='SCR')
    on_mobile = screen_width is not None and screen_width < 500

    with col2:
        with st.expander(label="🍔 Menu") if on_mobile else nullcontext():
            nav_to_main_lobby_button()
            if not st.user.is_logged_in:
                if st.button("Log in", type="primary", icon=":material/login:", width=100):
                    st.login("google")
            else:

                player = insert_or_get_player(
                    Player(
                        id=None,
                        name=st.user.given_name,
                        email=st.user.email,
                        mmr=2000,
                        games_number=0,
                        pseudo=None
                    )
                )

                if st.button(f"Log out ({st.user.given_name})", width=100):
                    st.logout()

                if st.button("Profile", key=f"nav_to_profile_button", width=100):
                    nav_to_player_id_page(player_id=player.id)

            if st.button("Contact", key=f"nav_to_contact_button", width=100):
                nav_to_contact_page()

            if st.button("Simulator", key=f"nav_to_simulator_button", width=100):
                nav_to_simulator_page()

    return player