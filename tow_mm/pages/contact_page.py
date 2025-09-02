import base64
from datetime import datetime
from typing import List, Optional

from tow_mm.data_model import Player, ContactMessage
from tow_mm.db_utils import get_contact_messages, add_contact_message
from tow_mm.utils import draw_line, is_connected
import streamlit as st

def display_contact_page(player: Optional[Player]):

    message = st.text_area(label="contact_area", label_visibility="collapsed", placeholder="Your suggestions and bug reports", max_chars=2000)
    email = st.text_input(label="email_contact", placeholder="Email (optional)", label_visibility="collapsed")

    def send_message(email_, message_):
        if not email_ and is_connected() and player is not None:
            email_ = player.email
        add_contact_message(message=ContactMessage(
            message=message_,
            email=email_,
            created_at=datetime.now(tz=None),
            id=None,
        ))
        st.success("message sent")

    # Button to send text
    if st.button("Send"):
        if message:  # make sure it's not empty
            send_message(message_=message, email_=email)
        else:
            st.warning("Please enter some text before sending.")
    # else:
    #     if message:
    #         send_message(message_=message, email_=email)

    with open("static/logos/discord.png", "rb") as f:
        b64 = base64.b64encode(f.read()).decode()

    draw_line()

    st.write("Join us on discord! (#matchmaking-app channel)")
    st.markdown(
        f'''
        <a href="https://discord.gg/wSMdzCq3Xd" target="_blank" rel="noopener">
            <img src="data:image/png;base64,{b64}" style="max-width:10%; height:auto; border-radius:12px;" />
        </a>
        ''',
        unsafe_allow_html=True
    )

    if is_connected() and player.pseudo == "Elwiii":
        draw_line()
        st.write("All messages:")
        messages = get_contact_messages()
        for m in messages:
            st.write(f"{m.email if m.email else 'anonymous'} {m.message}")


