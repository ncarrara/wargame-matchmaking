from typing import List, Optional

from tow_mm.data_model import Player, Venue
from tow_mm.db_utils import add_match
from tow_mm.utils import is_connected, normalize
import streamlit as st
from datetime import  datetime

def add_match_widget(venues: List[Venue], current_player: Player)-> Optional[int]:
    # --------------------
    # ADD A MATCH
    # --------------------
    vanues_name_to_id = {f.name: f.id for f in venues}
    match_id = None
    if is_connected():
        # Input for date and time
        col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
        with col1:
            match_date = st.date_input("Match Date", label_visibility="collapsed")
        with col2:
            match_time = st.time_input("Match Time", label_visibility="collapsed")
        with col3:
            names = {normalize(v.name): v.name for v in venues}
            venue_name = st.selectbox(
                "Venue",
                options=[name for normalized_name, name in sorted(list(names.items()), key=lambda x: x[0])],
                index=None,
                placeholder="Venue",
                key=f"venue_selectbox",
                label_visibility="collapsed")

        with col4:
            ranked = st.checkbox("ranked")

        with col5:
            if st.button("Add Match"):
                # Combine date and time into a datetime object
                if not match_date or not venue_name or not match_time:
                    st.error("input issue")
                else:
                    match_datetime = datetime.combine(match_date, match_time)
                    try:
                        match_id = add_match(
                            venue_id=vanues_name_to_id[venue_name],
                            created_by=current_player,
                            match_datetime=match_datetime,
                            ranked=ranked
                        )
                    except Exception as e:
                        st.error(f"Failed to add match: {e}")
    return match_id