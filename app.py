import logging
import os

import colorlog
import streamlit as st
from dotenv import load_dotenv
from streamlit_autorefresh import st_autorefresh

from tow_mm.config import Config
from tow_mm.db_utils import get_players, get_factions, get_venues
from tow_mm.pages.battle_report_page import display_battle_report
from tow_mm.pages.comfaq import display_com_faq
from tow_mm.pages.contact_page import display_contact_page
from tow_mm.pages.create_bp_page import display_create_battle_report
from tow_mm.pages.main_lobby import display_main_lobby_page
from tow_mm.pages.match_lobby import display_match_lobby_page
from tow_mm.pages.profile_page import display_profile_page
from tow_mm.pages.ranking_page import display_ranking_page
from tow_mm.pages.simulator_page import display_simulator_page
from tow_mm.widgets.head_widget import display_header

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


st.session_state.config = Config(app_url=os.getenv("APP_URL", None), uploads_url=os.getenv("UPLOADS_URL", None))

simulation = st.query_params and "page" in st.query_params and st.query_params["page"] == "simulator"
battle_report = st.query_params and "page" in st.query_params and st.query_params["page"] == "report"
create_battle_report = st.query_params and "page" in st.query_params and st.query_params["page"] == "create_battle_report"
com_faq = st.query_params and "page" in st.query_params and st.query_params["page"] == "com_faq"

autorefresh= not simulation

if autorefresh:
    interval = 3000
else:
    interval =  500_000

# st_autorefresh(interval=interval)


if not com_faq:
    st.set_page_config(page_title="WMM", page_icon="static/logos/transparent_green.png")
    player = display_header()
else:
    st.set_page_config(page_title="WMM", page_icon="static/logos/transparent_green.png", layout="wide")
    player= None

st.session_state.player = player

factions = get_factions()
venues = get_venues()
players = get_players()

players_by_id = {p.id: p for p in players}

if player is not None and player.id not in players_by_id:
    players_by_id[player.id] = player
    players.append(player)

if st.query_params and "match_id" in st.query_params:
    display_match_lobby_page(
        players=players,
        venues=venues,
        factions=factions,
        match_id=st.query_params.match_id
    )
elif st.query_params and "player_id" in st.query_params:
    display_profile_page(player=players_by_id[int(st.query_params.player_id)], players=players)
elif st.query_params and "ranking" in st.query_params:
    display_ranking_page(current_player=player, players=players, top=int(st.query_params["ranking"]))
elif st.query_params and "page" in st.query_params and st.query_params["page"] == "contact":
    display_contact_page(player=player)
elif simulation:
    display_simulator_page()
elif battle_report:
    display_battle_report(report_id=int(st.query_params.id) if "id" in st.query_params else None, players=players_by_id)
elif create_battle_report:
    display_create_battle_report(player=player)
elif com_faq:
    display_com_faq()
else:
    display_main_lobby_page(players=players, venues=venues)

