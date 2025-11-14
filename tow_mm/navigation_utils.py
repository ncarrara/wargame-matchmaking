from typing import Optional

import streamlit as st


def nav_to_match_lobby_button(match_id: int, extra_key: str):
    if st.button("Join lobby", key=f"nav_to_match_lobby_button_{match_id}_{extra_key}"):
        nav_to_match_lobby(match_id=match_id)


def nav_to_match_lobby(match_id: int):
    st.query_params["match_id"] = match_id
    st.rerun()

def nav_to_player_id_page(player_id: int):
    st.query_params.clear()
    st.query_params["player_id"] = player_id
    st.rerun()

def nav_to_page(page: str):
    st.query_params.clear()
    st.query_params["page"] = page
    st.rerun()

def nav_to_contact_page():
    nav_to_page("contact")

def nav_to_simulator_page():
    nav_to_page("simulator")

def nav_to_ranking_page(top: int):
    st.query_params.clear()
    st.query_params["ranking"] = top
    st.rerun()

def nav_to_battle_report_page(report_id: Optional[int]):
    st.query_params.clear()
    st.query_params["page"] = "report"

    if report_id is not None:
        st.query_params["id"] = report_id
    st.rerun()


def nav_to_main_lobby_button():
    if st.button("Lobby"):
        st.query_params.clear()
        st.rerun()