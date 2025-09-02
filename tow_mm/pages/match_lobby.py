import logging
from datetime import datetime, timedelta, UTC
from typing import List

import pytz
import streamlit as st
from streamlit_javascript import st_javascript

from tow_mm.data_model import Faction, Venue, Player, ChatMessage
from tow_mm.db_utils import get_match, add_chat_message, get_messages
from tow_mm.db_utils import get_match_participations, delete_match, \
    add_match_participant, \
    delete_participation, set_participation_ready, set_participation_result
from tow_mm.utils import is_connected, get_curr_player, start_of_the_day, draw_line


def display_match_lobby_page(
        match_id: int,
        players: List[Player],
        venues: List[Venue],
        factions: List[Faction],

):


    match = get_match(match_id=match_id)
    if match:
        players_by_id = {p.id: p for p in players}
        factions_name_to_id = {f.name: f.id for f in factions}
        factions_dict = {f.id: f for f in factions}
        venues_dict = {f.id: f for f in venues}

        app_url = st.session_state.config.app_url


        col1, _, col2 = st.columns([5, 1, 2])

        # with col1:
        st.markdown(f"### Match {match.id}")

        # with col2:
        link = f"{app_url}?match_id={match.id}"

        st.markdown(f"[Link to share]({link})")

        c0, c1, c2, c3 = st.columns([1, 1, 1, 1])
        with c0:
            with st.container(border=True):
                st.markdown(f"**Creator**\n`{players_by_id[match.created_by].name}`")
        with c1:
            with st.container(border=True):
                st.markdown(f"**Venue**\n`{venues_dict[match.venue_id].name}`")
        with c2:
            with st.container(border=True):
                st.markdown(f"**Type**\n{'`Ranked`' if match.ranked else '`Not Ranked`'}")
        with c3:
            with st.container(border=True):
                st.markdown(f"**Date**\n`{match.created_at}`")


        # Row with match info and delete button
        participants = get_match_participations(match.id)
        player_id_to_participant = {p.player_id: p for p in participants}

        draw_line()

        if not is_connected():
            st.write("#### Log in to play")

        if not participants:
            st.write("_No participants yet._")
        # Participants list
        else:
            for part in participants:
                # st.write(part)

                # with st.container(border=True):
                with st.container():
                    col1_, col2_, col3_ = st.columns([3, 1, 1])
                    player = players_by_id[part.player_id]
                    with col1_:
                        mmr_txt = f" `{player.mmr}`" if match.ranked else ""
                        st.write(
                            f"{player.name} - {factions_dict[part.faction_id].name}{mmr_txt}"
                        )

                    if match.is_closed():
                        with col2_:
                            color = "red" if part.lost() else ("green" if part.won() else "blue")
                            mmr_txt = "" if not match.ranked else f" [{part.mmr_before} -> {part.mmr_after}]"
                            st.markdown(f"<span style=\"color:{color}\">{part.result}{mmr_txt}</span>",
                                        unsafe_allow_html=True)
                    else:
                        # match not closed
                        if not match.is_ongoing():
                            if is_connected() and (part.player_id == get_curr_player().id):
                                if not part.is_ready:
                                    with col3_:
                                        if st.button("❌ Cancel", key=f"delete_{part.player_id}-{part.match_id}"):
                                            try:
                                                delete_participation(match_id=part.match_id, player_id=part.player_id)
                                                st.rerun()
                                            except Exception as e:
                                                st.error(f"Failed to delete participation: {e}")
                                with col2_:
                                    if st.button("✅ I am ready" if not part.is_ready else "I am not ready",
                                                 key=f"ready_{part.player_id}-{part.match_id}"):
                                        try:
                                            set_participation_ready(
                                                is_ready=not part.is_ready,
                                                match_id=part.match_id,
                                                player_id=part.player_id)
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"Failed to change ready: {e}")
                            else:
                                # not connected or not current player
                                with col2_:
                                    st.write("Ready ✅" if part.is_ready else "Not ready")
                        else:
                            # match ready
                            if is_connected() and part.player_id == get_curr_player().id:
                                with col2_:
                                    result = st.selectbox(
                                        "Result",
                                        options=["win", "lose", "draw"],
                                        index=None,
                                        placeholder="result?" if part.result == "undefined" else part.result,
                                        key=f"res_selectbox_{part.match_id}_{part.player_id}",
                                        label_visibility="collapsed"
                                    )
                                    if result is not None and part.result != result:
                                        set_participation_result(result=result, player_id=part.player_id,
                                                                 match_id=part.match_id)
                                        st.rerun()
                            else:
                                # not connected or not current player
                                with col2_:
                                    st.write(part.result)

        # Add participant form
        if is_connected():
            if not match.is_ongoing():
                if get_curr_player().id not in player_id_to_participant and len(participants) < 2:
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        selected_faction_name = st.selectbox(
                            "Faction ID",
                            index=None,
                            placeholder="select faction",
                            options=sorted([f.name for f in factions]),
                            key=f"fid_{match.id}",
                            label_visibility="collapsed")
                    with col2:

                        if st.button("Play", key=f"add_{match.id}"):
                            if selected_faction_name is None:
                                st.error(f"Select a faction")
                            else:
                                try:
                                    add_match_participant(
                                        match_id=match.id,
                                        player_id=get_curr_player().id,
                                        faction_id=factions_name_to_id[selected_faction_name],
                                        mmr_before=0,
                                        mmr_after=0,
                                        result="undefined")
                                    # st.success("Participant added!")
                                    st.rerun()
                                except Exception as e:
                                    logging.exception(e)
                                    st.error(f"Failed to add participant: {e}")

        if is_connected() and match.can_be_delete() and (get_curr_player().id == match.created_by or  get_curr_player().pseudo == "Elwiii"):
            if st.button("❌ Delete match", key=f"delete_{match.id}"):
                try:
                    delete_match(match.id)
                    st.query_params.clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to delete match: {e}")

        with st.container(border=True):
            st.markdown("#### Private chat")

            other_player_id = None if (len(participants) <= 1 or not is_connected()) else (
                participants[0].player_id if participants[0].player_id != get_curr_player().id else participants[
                    1].player_id)

            if  is_connected() and get_curr_player().id in player_id_to_participant and other_player_id is not None:

                message = st.chat_input("Chat with your opponent", )
                messages = get_messages(match_id=match_id, player_id=get_curr_player().id, destination_player_id=other_player_id)

                if message:
                    created_at = datetime.now(tz=None)
                    m = ChatMessage(
                        message=message,
                        created_at=created_at,
                        player_id=get_curr_player().id,
                        match_id=match_id,
                        id=None,
                        destination_player_id=other_player_id
                    )
                    messages.append(m)
                    add_chat_message(m)

                timezone = st_javascript("""await (async () => {
                            const userTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
                            console.log(userTimezone)
                            return userTimezone
                })().then(returnValue => returnValue)""")

                try:
                    timezone = pytz.timezone(str(timezone))
                except Exception as e:
                    # st.error(f"Could not parse timezone: {timezone} ({type(timezone)})")
                    timezone = UTC # fallback

                import pandas as pd
                for m in messages[::-1]:
                    align = "left" if m.player_id == get_curr_player().id else "right"

                    same_day = start_of_the_day(datetime.now(tz=UTC)) == start_of_the_day(m.created_at.astimezone(tz=UTC))
                    fmt = "%H:%M" if same_day else "%Y-%m-%d %H:%M"
                    date_in_user_tz = pd.to_datetime(m.created_at).tz_localize(timezone)
                    player_name = players_by_id[m.player_id].name
                    time_str = f"[{date_in_user_tz.strftime(fmt)}]"
                    st.markdown(
                        f"<p style='margin: 1px 0; text-align: {align};'>{time_str if align =='left' else ''}{player_name}: {m.message} {'' if align == 'left' else time_str}</p>",
                        unsafe_allow_html=True
                    )
            else:
                st.write("Join the game if you wanna join the private chat")
    else:
        st.write(f"Match {st.query_params.match_id} does not exist")