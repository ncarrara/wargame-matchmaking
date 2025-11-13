import re
import shutil
import uuid
from pathlib import Path

import streamlit as st

from tow_mm.data_model import BattleReport, Player
from tow_mm.db_utils import add_battle_report
from tow_mm.navigation_utils import nav_to_battle_report_page


def display_create_battle_report(player: Player):
    st.set_page_config(layout="wide")
    st.title("📝 Markdown Editor with Local Image Uploads")

    # Ensure the upload directory exists
    tmp_dir = Path("uploads") / str(player.id) / ".tmp"
    tmp_dir.mkdir(exist_ok=True, parents=True)

    # Initialize session state for markdown
    if "markdown_text" not in st.session_state:
        st.session_state.markdown_text = "# Welcome!\n\nWrite your Markdown here..."

    if "all_uploaded_files" not in st.session_state:
        shutil.rmtree(tmp_dir)  # remove old tmps files
        st.session_state.all_uploaded_files = []

    # Function to save image locally and return Markdown path
    def save_image_locally(file):
        print(f"saving {file} locally")
        file_uuid = uuid.uuid4()
        file_name = str(file_uuid) + "." + str(file.name.split(".")[-1])
        file_path = tmp_dir / file_name
        st.session_state.all_uploaded_files.append(str(file_path))
        with open(file_path, "wb") as f:
            f.write(file.getbuffer())
        return file_uuid, file, f"http://localhost:8000/{file_path}"

    st.subheader("✍️ Markdown Editor")

    uploaded_file = st.file_uploader(
        "Upload images (PNG, JPG, JPEG)",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=False,

    )


    if st.button(f"Submit battle report", key=f"submit_battle_report", width=300):
        image_paths = [Path("uploads") / x for x in
                       re.findall(r'!\[.*?\]\(.*?/uploads/(.*?)\)', st.session_state.markdown_text)]
        has_error = []
        for image_path in image_paths:
            if not image_path.exists():
                has_error.append(image_path)

        print(f"==============================")
        print(f"==============================")
        print(f"==============================")
        print(f"{image_paths}")
        print(f"st.session_state.markdown_text: {st.session_state.markdown_text}")

        if len(has_error) > 0:
            st.error(f"files {has_error} does not exists")
        else:
            for image_path in image_paths:
                target_location = image_path.parent.parent / image_path.name
                shutil.move(image_path, target_location)

            shutil.rmtree(tmp_dir)

            # Regex to replace /uploads/<player_id>/.tmp/ with /uploads/<player_id>/
            pattern = rf'/{player.id}/\.tmp/'
            replacement = f'/{player.id}/'

            new_markdown_text = re.sub(pattern, replacement, st.session_state.markdown_text)

            bp_id = add_battle_report(bp=BattleReport(content=new_markdown_text, id=None, created_by=player.id))
            st.session_state.markdown_text = ""
            st.session_state.all_uploaded_files.clear()
            nav_to_battle_report_page(report_id=bp_id)
    else:
        if uploaded_file:
            file_uuid, file, link = save_image_locally(uploaded_file)
            st.session_state.markdown_text += f"\n![{file.name}]({link})\n"
            
    st.session_state.markdown_text = st.text_area(
        "Edit your Markdown",
        value=st.session_state.markdown_text,
        height=400
    )
