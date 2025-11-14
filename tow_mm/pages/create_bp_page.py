import re
import shutil
import uuid
from pathlib import Path
from typing import Optional

import streamlit as st

from tow_mm.data_model import BattleReport, Player
from tow_mm.db_utils import add_battle_report
from tow_mm.navigation_utils import nav_to_battle_report_page
from tow_mm.utils import draw_line

DEFAULT_MD = """

**Date:** November 12, 2025  
**Scenario:** Meeting Engagement  
**Game Size:** 2000 Points  
**Battlefield:** The Fields of Averland  
**Turn Limit:** 6 Turns  

---

## 🧙‍♂️ Armies

### **Empire of Man**
**Commander:** General Otto von Reik  
**Army Composition:**
- General of the Empire on Griffon (Warlord)
- Battle Wizard (Lore of Heavens)
- 20 Halberdiers (Full Command)
- 10 Handgunners
- 5 Inner Circle Knights
- Great Cannon
- Steam Tank  

**Total:** 1995 pts  

---

### **Orcs & Goblins**
**Commander:** Gromm da Smashy  
**Army Composition:**
- Orc Warboss (War Boar, Heavy Armour)
- Night Goblin Shaman (Level 2, Mushrooms)
- 30 Orc Boyz (Full Command)
- 20 Night Goblins (2 Fanatics)
- 10 Orc Boar Boyz
- Rock Lobber  
- Giant  

**Total:** 1998 pts  

---

## 🌍 Deployment

**Empire:**  
Deployed with artillery on the hill, infantry in the centre, and knights on the right flank.  

**Orcs & Goblins:**  
Orc Boyz opposite the Halberdiers, Night Goblins on the left, Giant near the centre to threaten the line.


---

## ⚔️ Turn-by-Turn Summary

### **Turn 1**
**Empire:**  
- Cannon misfires (no explosion!).  
- Wizard casts *Harmonic Convergence* on Halberdiers.  
- Handgunners kill 3 Orc Boyz.  

**Orcs & Goblins:**  
- Fanatics released! One kills 5 Halberdiers.  
- Giant moves up aggressively.  
- Rock Lobber misses the Steam Tank.

---

### **Turn 2**
**Empire:**  
- Knights charge Boar Boyz and win combat by 2 — Orcs hold.  
- Steam Tank crushes 6 Orc Boyz with impact hits.  

**Orcs & Goblins:**  
- Giant charges Halberdiers; causes Terror test — they hold!  
- Shaman miscasts *Foot of Gork*, taking a wound.  

---

### **Turn 3–4**
- Empire artillery finally hits, killing the Giant.  
- Orc morale begins to crumble after their general is slain by the Griffon.  
- Steam Tank holds the center while Knights sweep the flank.

---

## 🏁 Result

**Victory:** Empire of Man (Massacre)  
**Final Score:**  
- Empire: 1450 Victory Points  
- Orcs & Goblins: 670 Victory Points  

---

## 🧩 MVPs

- **Empire:** Steam Tank — destroyed two units and held the line.  
- **Orcs & Goblins:** Night Goblin Fanatics — caused early chaos and panic.  

---

## 📜 Post-Game Thoughts

> “The Griffon’s charge broke their will before steel ever did.” — General Otto von Reik

**Lessons Learned:**
- Keep artillery protected from Fanatics.
- Giants are unreliable — but terrifying while they last.
- Synergy between Wizard buffs and Steam Tank was devastating.

---

## 📸 Gallery

| Turn | Description | Image |
|------|--------------|-------|
| 1 | Deployment phase overview | ![deployment](deployment.jpg) |
| 3 | Griffon charges Giant | ![charge](griffon-vs-giant.jpg) |
| 6 | Endgame overview | ![endgame](battle-end.jpg) |

---

*Recorded by:* **Marcus the Chronicler**  
*Campaign:* *Defenders of the Reik, Game 3/10*



"""

def update_key():
    st.session_state.uploader_key += 1

def display_create_battle_report(player: Optional[Player]):

    if player is None:
        st.markdown("You must be connected to create a battle report")
        if st.button("Log in", type="primary", icon=":material/login:", width=100, key="login-display_create_battle_report"):
            st.login("google")
    else:

        tmp_dir = Path("uploads") / str(player.id) / ".tmp"
        tmp_dir.mkdir(exist_ok=True, parents=True)

        # Initialize session state for markdown
        if "markdown_text" not in st.session_state:
            st.session_state.markdown_text = DEFAULT_MD

        if "uploader_key" not in st.session_state:
            st.session_state.uploader_key = 0

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
            return file_uuid, file, f"{st.session_state.config.uploads_url}/{file_path}"

        st.subheader("✍️ Create battle report")

        uploaded_file = st.file_uploader(
            "Upload images (PNG, JPG, JPEG)",
            type=["png", "jpg", "jpeg"],
            accept_multiple_files=False,
            key = f"uploader_{st.session_state.uploader_key}",

        )

        if uploaded_file:
            print(f"uploaded_file: {uploaded_file}")
            file_uuid, file, link = save_image_locally(uploaded_file)
            st.session_state.markdown_text += f"\n![{file.name}]({link})\n"
            # st.text(f"copy this to insert the image: ")
            # st.text(f"[{file.name}]({link})")
            print(st.session_state.markdown_text)
            update_key()
            st.rerun()




        st.text_area(
            label="battle_report",
            label_visibility="hidden",
            height=400,
            key="markdown_text",
        )

        col1,col2 = st.columns([5,5])
        with col1:

            if st.button('preview', width=500):
                st.markdown(st.session_state.markdown_text)
        with col2:
            if st.button(f"Submit battle report", key=f"submit_battle_report", width=500):
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
                    # st.session_state.markdown_text = ""
                    st.session_state.all_uploaded_files.clear()
                    nav_to_battle_report_page(report_id=bp_id)

