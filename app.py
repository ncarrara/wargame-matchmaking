import logging
from datetime import datetime
import colorlog
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
	'%(log_color)s%(levelname)s:%(name)s:%(message)s'))

import pandas as pd
import streamlit as st

from db_utils import get_players, add_match, get_matches, get_match_participants, delete_match, add_match_participant, \
    insert_or_get_player
from discord_utils import exchange_code_for_token, get_user_info, get_discord_auth_url, load_token_data_from_cookie, \
    save_token_data_to_cookie, token_is_valid

logging.basicConfig(level=logging.INFO)


# --------------------
# STREAMLIT APP
# --------------------
st.set_page_config(page_title="Warhammer", page_icon="🎮")

st.title("Warhammer Matchmaking")

# Show players from PostgreSQL
st.subheader("Top 5 players")
try:
    players = get_players()
    for p in players[:5]:
        st.write(f" [{2000}] {p['name']}")
except Exception as e:
    st.error(f"Failed to fetch players: {e}")

query_params = st.query_params

if "token_data" not in st.session_state:
    token_data = load_token_data_from_cookie()
    if token_is_valid(token_data):
        st.session_state["token_data"] = token_data

if "token_data" not in st.session_state and "code" in query_params:
    token_data = exchange_code_for_token(query_params["code"])
    if token_is_valid(token_data):
        st.session_state["token_data"] = token_data

        save_token_data_to_cookie(token_data)
    else:
        logging.error(f"Token is invalid, token_data: {token_data}")

def is_connected():
    return "token_data" in st.session_state and token_is_valid(st.session_state["token_data"])

# Later, when you need it
if is_connected():
    user_info = get_user_info(st.session_state["token_data"])
    st.success(f"Logged in as {user_info['username']}#{user_info['discriminator']}")
    st.image(f"https://cdn.discordapp.com/avatars/{user_info['id']}/{user_info['avatar']}.png")
    insert_or_get_player(user_info)
    st.session_state["player_name"] = user_info['username']

else:
    st.markdown(f"[Login with Discord]({get_discord_auth_url()})")

# # --------------------
# # ADD A PLAYER
# # --------------------
#
# st.subheader("Add a new player")
# new_name = st.text_input("Player Name")
#
# if st.button("Add Player"):
#     if new_name.strip() == "":
#         st.warning("Please enter a player name")
#     else:
#         try:
#             player_id = add_player(new_name.strip())
#             st.success(f"Player '{new_name}' added with ID {player_id}")
#             # Refresh the player list
#             players = get_players()
#             st.subheader("Updated Players in Database")
#             for p in players:
#                 st.write(f"**ID:** {p['id']} — **Name:** {p['name']}")
#         except Exception as e:
#             st.error(f"Failed to add player: {e}")

# --------------------
# ADD A MATCH
# --------------------
if is_connected():
    st.subheader("Add a new match")

    # Input for date and time
    col1, col2,col3 = st.columns([1, 1,1])
    with col1:
        match_date = st.date_input("Match Date", label_visibility="collapsed")
    with col2:
        match_time = st.time_input("Match Time", label_visibility="collapsed")
    with col3:
        if st.button("Add Match"):
            # Combine date and time into a datetime object
            match_datetime = datetime.combine(match_date, match_time)
            try:
                match_id = add_match(match_datetime)
                # st.success(f"Match added with ID {match_id} at {match_datetime}")
            except Exception as e:
                st.error(f"Failed to add match: {e}")


##############
st.subheader("All Matches")
matches = get_matches()

if not is_connected():
    st.write("connect to play")

if matches:
    for match in matches:
        # Row with match info and delete button
        participants = get_match_participants(match['id'])

        col1, col2, col3 = st.columns([4, 1, 1])

        match_ready = len(participants) == 2

        with col1:
            st.markdown(f"### Match {match['id']} — {match['created_at'].strftime('%Y-%m-%d %H:%M:%S')}")

        if not match_ready:
            with col2:
                if st.button("❌ Delete", key=f"delete_{match['id']}"):
                    try:
                        delete_match(match['id'])
                        # st.success(f"Deleted match {match['id']}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to delete match: {e}")

        # Participants list
        if participants:
            for part in participants:
                st.write(
                    f"- **{part['player_name']}** "
                    f"(Faction {part['faction_id']} | "
                    f"MMR {part['mmr_before']} → {part['mmr_after']} | "
                    f"Result: {part['result']})"
                )
        else:
            st.write("_No participants yet._")

        # Add participant form
        # if is_connected():
        if not match_ready:
            with col3:
                # with st.expander(f"Play"):
                with st.popover("Play"):
                    st.subheader(f"Match {match['id']}")
                    player_id = st.number_input("Player ID", min_value=1, step=1, key=f"pid_{match['id']}")
                    faction_id = st.number_input("Faction ID", min_value=1, step=1, key=f"fid_{match['id']}")
                    mmr_before = st.number_input("MMR Before", step=1, key=f"mmrb_{match['id']}")
                    mmr_after = st.number_input("MMR After", step=1, key=f"mmra_{match['id']}")
                    result = st.selectbox("Result", ["win", "lose", "draw"], key=f"res_{match['id']}")

                    if st.button("✅ Add", key=f"add_{match['id']}"):
                        try:
                            add_match_participant(match['id'], player_id, faction_id, mmr_before, mmr_after, result)
                            # st.success("Participant added!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to add participant: {e}")

        if match_ready:
            with col3:
                result = st.selectbox("Result", ["result","win", "lose", "draw"], key=f"res_{match['id']}", label_visibility="collapsed")
                if result != "result":
                    print(f"player enter result: {result}")
                    # if st.button("✅ Add", key=f"add_{match['id']}"):
                    #     try:
                    #         add_match_participant(match['id'], player_id, faction_id, mmr_before, mmr_after, result)
                    #         st.success("Participant added!")
                    #         st.rerun()
                    #     except Exception as e:
                    #         st.error(f"Failed to add participant: {e}")

else:
    st.info("No matches found.")

from streamlit_calendar import calendar


def show_matches_calendar():
    matches = get_matches()
    if not matches:
        st.info("No matches found.")
        return

    events = [
        {
            "title": f"Match {m['id']}",
            "start": m["created_at"].isoformat(),
            "end": (m["created_at"] + pd.Timedelta(hours=1)).isoformat()
        }
        for m in matches
    ]

    calendar_options = {
        "initialView": "dayGridMonth",
        "editable": False,
        "selectable": False
    }

    calendar(events=events, options=calendar_options)


# Call this
st.subheader("Matches Calendar")
show_matches_calendar()
