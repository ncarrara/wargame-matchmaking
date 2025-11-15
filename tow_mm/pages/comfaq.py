import streamlit as st

from tow_mm.comfaq import parse_com_faq


def display_com_faq():

    df = parse_com_faq()

    # CSS to wrap text in dataframe
    st.markdown("""
    <style>
    [data-testid="stDataFrame"] div[data-testid="stGridCell"] {
        white-space: normal !important;
        text-overflow: clip !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.dataframe(df, height=150*len(df)+38, row_height=150)
    # st.table(df) #, row_height=50)
