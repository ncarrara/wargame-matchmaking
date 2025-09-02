import datetime
import unicodedata
from typing import Optional
from streamlit_js_eval import get_geolocation

from tow_mm.data_model import Player
import streamlit as st

def normalize(s):
    # Convert to lowercase
    s = s.lower()
    # Remove accents/diacritics
    s = unicodedata.normalize("NFD", s)
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    return s

def is_connected():
    return st.user.is_logged_in


def get_curr_player() -> Optional[Player]:
    return None if not is_connected() else st.session_state.player


def start_of_the_day(dt: datetime.datetime):
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)

def draw_line(margin: float = 0.3):
    st.markdown(f"<hr style='margin: {margin}em 0;'>", unsafe_allow_html=True)
