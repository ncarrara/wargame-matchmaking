import logging
import os

import colorlog
import streamlit as st
from dotenv import load_dotenv
from streamlit_autorefresh import st_autorefresh

from tow_mm.config import Config
from tow_mm.db_utils import get_players, Player, insert_or_get_player, get_factions, get_venues
from tow_mm.navigation_utils import nav_to_main_lobby_button
from tow_mm.pages.main_lobby import display_main_lobby_page
from tow_mm.pages.match_lobby import display_match_lobby_page

load_dotenv()

handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    '%(log_color)s%(levelname)s:%(name)s:%(message)s'))
logging.basicConfig(level=logging.INFO)


# Remove whitespace from the top of the page and sidebar
st.markdown("""
        <style>
               .block-container {
                    padding-top: 1rem;
                }
        </style>
        """, unsafe_allow_html=True)


st.session_state.config = Config(app_url=os.getenv("APP_URL", None))
# This gives browser info including timezone offset

# st.write(get_geolocation())
count = st_autorefresh(interval=3000)

st.set_page_config(page_title="Warhammer", page_icon="static/logos/transparent_green.png")


col1,  col2  = st.columns([1,1])


with col1:
    st.image("static/logos/banner.png")

with col2:
    nav_to_main_lobby_button()
    if not st.user.is_logged_in:
        if st.button("Log in with Google", type="primary", icon=":material/login:"):
            st.login("google")
    else:
        # st.image(st.user.picture, width=50)
        player = insert_or_get_player(
            Player(
                id=None,
                name=st.user.given_name,
                email=st.user.email,
                mmr=2000,
                games_number=0,
            )
        )

        st.session_state.player = player
        if st.button(f"Log out ({st.user.given_name})"):
            st.logout()

factions = get_factions()
venues = get_venues()
players = get_players()

if st.query_params and "match_id" in st.query_params:
    display_match_lobby_page(
        players=players,
        venues=venues,
        factions=factions,
        match_id=st.query_params.match_id
    )
else:
    display_main_lobby_page(players=players, venues=venues)

