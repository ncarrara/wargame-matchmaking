from typing import Optional

import streamlit as st
import pandas as pd

from tow_mm.comfaq import parse_com_faq
from tow_mm.navigation_utils import nav_to_page

# Map categories to colors
category_to_color = {
    "Characters": "#FFCDD2",           # soft red
    "Charge": "#F8BBD0",               # pink
    "Close Combat": "#E1BEE7",         # purple
    "Combat": "#D1C4E9",               # lavender
    "General Principles": "#C5CAE9",   # light indigo
    "Magic": "#B3E5FC",                # light blue
    "Magic Items": "#B2EBF2",          # cyan
    "Magical Items": "#80DEEA",        # teal-ish
    "Movement": "#C8E6C9",             # light green
    "Moving": "#A5D6A7",               # green
    "Shooting": "#DCEDC8",             # lime
    "Special Rules": "#FFF9C4",        # yellow
    "Universal Rules": "#FFECB3",      # amber
    "Universal Special Rules": "#FFE0B2", # orange
    "Low linear obstacle": "#FFCCBC",  # light coral
    "Deployment": "#D7CCC8",           # brownish
    "Scoring": "#F0F4C3",              # pale lime
    "Skirmisher": "#E6EE9C",           # soft yellow-green
    "Scenarios": "#CFD8DC",            # grey-blue
}


def display_com_faq(entry_id: Optional[int] = None):
    df = parse_com_faq()

    st.title("Community FAQ")

    st.sidebar.image("static/logos/banner.png")

    if st.sidebar.button("Home"):
        nav_to_page("Lobby")

    st.sidebar.header("Filters")


    search_text = st.sidebar.text_input("Enter search term:")


    categories = ["All"] + list(df['Category'].dropna().unique())
    selected_category = st.sidebar.selectbox("Category", options=categories, index=0)

    rule_refs = ["All"] + list(df['Rule Reference'].dropna().unique())
    selected_rule = st.sidebar.selectbox("Rule Reference", options=rule_refs, index=0)

    # Apply filters
    filtered_df = df.copy()

    if search_text:
        mask = (
                df['Question'].str.contains(search_text, case=False, na=False) |
                df['Ruling'].str.contains(search_text, case=False, na=False) |
                df['Category'].str.contains(search_text, case=False, na=False) |
                df['Rule Reference'].str.contains(search_text, case=False, na=False)
        )
        filtered_df = df[mask]

    if selected_category != "All":
        filtered_df = filtered_df[filtered_df['Category'] == selected_category]
    if selected_rule != "All":
        filtered_df = filtered_df[filtered_df['Rule Reference'] == selected_rule]

    if filtered_df.empty:
        st.warning("No FAQs match your filters.")
        return

    print(filtered_df["Category"].unique())

    # --- Display FAQs ---
    for idx, row in filtered_df.iterrows():
        # print(row.Category)
        color = category_to_color.get(row.Category, "#E0E0E0")  # default color

        st.markdown("---")  # horizontal line

        # Colored header with inline HTML
        st.markdown(
            f"""
            <div style="
                background-color: {color};
                padding: 10px;
                border-radius: 5px;
                display: block;
            ">
                <strong>ID:</strong> {row.ID} &nbsp;&nbsp;
                <strong>Category:</strong> {row.Category} &nbsp;&nbsp;
                <strong>Rule Reference:</strong> {row['Rule Reference']}
            </div>
            """,
            unsafe_allow_html=True
        )

        # Question and Ruling
        st.markdown(f"**Question:** {row.Question}")
        st.markdown(f"**Ruling:** {row.Ruling}")

        # Optional fields
        if pd.notna(row.Notes):
            st.markdown(f"**Notes:** {row.Notes}")
        if pd.notna(row['Rules Reference or page Number']):
            st.markdown(f"**Rules Reference/Page:** {row['Rules Reference or page Number']}")
        if pd.notna(row['Change Log']):
            st.markdown(f"**Change Log:** {row['Change Log']}")

        st.markdown(f"*Date:* {row.Date}")

        # if st.button("share", key=f"share_{idx}"):
        #     nav_to_page()


if __name__ == "__main__":
    display_com_faq()
