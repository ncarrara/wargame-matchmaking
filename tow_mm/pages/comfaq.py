import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder

from tow_mm.comfaq import parse_com_faq


def display_com_faq():

    df = parse_com_faq()
    #
    # # CSS to wrap text in dataframe
    # gb = GridOptionsBuilder.from_dataframe(df)
    #
    # gb.configure_column(
    #     "Description",
    #     wrapText=True,
    #     autoHeight=True,
    # )
    #
    # gridOptions = gb.build()
    #
    # AgGrid(df, gridOptions=gridOptions, fit_columns_on_grid_load=True)

    st.dataframe(df, height=100*len(df)+38, row_height=100)
    # st.table(df) #, row_height=50)
