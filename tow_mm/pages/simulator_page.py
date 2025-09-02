import numpy as np
import pandas as pd
import streamlit as st
from streamlit import number_input
import matplotlib.pyplot as plt
from tow_mm.model.unit import Unit, SingleUnit, close_combat_round
from tow_mm.utils import draw_line
import plotly.express as px


def display_simulator_page():
    st.title("Combat Simulator")

    units = {}

    for i in [0, 1]:
        draw_line()
        st.subheader(f"Unit {i}")
        cols = st.columns(9)
        # cols_2 = st.columns(3)

        with cols[0]:
            weapon_skill = st.number_input(label="WS", key=f"WeaponSkill{i}", value=4, min_value=0, max_value=10,
                                           step=1)
        with cols[1]:
            strength = st.number_input(label="S", key=f"Strength{i}", value=4, min_value=0, max_value=10, step=1)
        with cols[2]:
            toughness = st.number_input(label="T", key=f"Toughness{i}", value=3, min_value=0, max_value=10, step=1)
        with cols[3]:
            initiative = st.number_input(label="I", key=f"Initiative{i}", value=4, min_value=0, max_value=10, step=1)
        with cols[4]:
            attacks = st.number_input(label="A", key=f"Attacks{i}", value=1, min_value=1, max_value=10, step=1)
        with cols[5]:
            wounds = st.number_input(label="W", key=f"Wounds{i}", value=1, min_value=1, max_value=10, step=1)
        with cols[6]:
            armor_save = st.number_input(label="Armor", key=f"ArmorSave{i}", value=5, min_value=2, max_value=7, step=1)
        with cols[7]:
            ward_save = st.number_input(label="Ward", key=f"WardSave{i}", value=7, min_value=2, max_value=7, step=1)
        with cols[8]:
            regen_save = st.number_input(label="Regen", key=f"RegenSave{i}", value=7, min_value=2, max_value=7, step=1)

        fighters = st.number_input(label="Fighters", key=f"Fighters{i}", value=10 if i==0 else 25, min_value=1, step=1)

        unit = Unit(
            single_unit=SingleUnit(
                toughness=toughness,
                initiative=initiative,
                ballistic_skill=None,
                weapon_skill=weapon_skill,
                attacks=attacks,
                strength=strength,
                regen=regen_save,
                armor=armor_save,
                ward=ward_save,
                base_height=None,
                base_width=None,
                leadership=None,
                wounds=wounds,
                name=f"unit {i}",
            ),
            fighters=fighters
        )

        units[i] = unit

    draw_line()

    n = number_input("Sample size", value=1000, min_value=1, max_value=10000)

    # Simulation button
    if st.button("Run Simulation"):
        st.write("⚔️ Running combat simulation...")
        # Here you would add your simulation logic
        # Example: compare WS, Strength vs Toughness, etc.
        all_w0 = []
        all_w1 = []

        for _ in range(n):
            w0, w1 = close_combat_round(units[0], units[1])
            all_w0.append(w0)
            all_w1.append(w1)

        st.success(f"Simulation complete!")

        st.markdown(f"Average wounds:  on unit 0:  `{np.mean(all_w0)}` on unit 1:  `{np.mean(all_w1)}`")

        fig = px.histogram(
            pd.DataFrame(data={"unit 0": all_w0, "unit 1": all_w1}),
            marginal="box",
            barmode="overlay",
            color_discrete_map={
                "unit 0": "red",
                "unit 1": "blue"
            }

        )
        st.plotly_chart(fig)
