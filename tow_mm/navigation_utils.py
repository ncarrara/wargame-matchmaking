import streamlit as st


def nav_to_match_lobby_button(match_id: int, extra_key: str):
    if st.button("Join lobby", key=f"nav_to_match_lobby_button_{match_id}_{extra_key}"):
        nav_to_match_lobby(match_id=match_id)


def nav_to_match_lobby(match_id: int):
    st.query_params["match_id"] = match_id
    st.rerun()

def nav_to_player_id_page(player_id: int):
    st.query_params["player_id"] = player_id
    st.rerun()

def nav_to_main_lobby_button():
    if st.button("Main lobby"):
        st.query_params.clear()
        st.rerun()