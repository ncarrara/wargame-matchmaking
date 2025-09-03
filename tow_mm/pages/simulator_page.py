from typing import List

import numpy as np
import pandas as pd
import streamlit as st
from streamlit import number_input
from tow_mm.model.unit import Unit, SingleUnit, close_combat_round
from tow_mm.utils import draw_line
import plotly.express as px
import json


@st.cache_resource
def read_json() -> List[SingleUnit]:
    units = []

    with open("static/units.json", "r") as f:
        data = json.load(f)
        parse = lambda x: 0 if x == "-" else int(x)
        for unit in data.values():
            if "troopType" not in unit or unit["troopType"] == "MCr":
                continue

            for unit in unit["stats"]:

                if "+" in unit["S"] or "+" in unit["T"] or "+" in unit["W"] or "D6" in unit["A"] or "*" in unit["A"] or "2D3" in unit["A"] or "D3" in unit["A"]:
                    continue

                if parse(unit["W"]) != 1:
                    continue

                unit = SingleUnit(
                    base_width=0,
                    base_height=0,
                    leadership=parse(unit["Ld"]),
                    attacks=parse(unit["A"]),
                    weapon_skill=parse(unit["WS"]),
                    strength=parse(unit["S"]),
                    wounds=parse(unit["W"]),
                    name=unit["Name"],
                    ballistic_skill=parse(unit["BS"]),
                    toughness=parse(unit["T"]),
                    # regen=unit[""],
                    # armor=unit[""],
                    # ward=unit[""],
                    initiative=parse(unit["I"]),
                )
                # print(unit)
                units.append(unit)
    return units


ALL_UNITS = {u.name: u for u in read_json()}




def display_simulator_page():
    st.title("Combat Simulator")

    units = {}

    for i in [0, 1]:
        draw_line()

        u_str = st.selectbox(label=f"Unit {i}",options= tuple(sorted([u for u in ALL_UNITS.keys()])))
        # u_str = "Necrosphinx" if i == 0 else "Duke"
        unit_0 = ALL_UNITS[u_str]
        cols = st.columns(9)

        with cols[0]:
            weapon_skill = st.number_input(label="WS", key=f"WeaponSkill{i}", value=unit_0.weapon_skill, min_value=0, max_value=10,
                                           step=1)
        with cols[1]:
            strength = st.number_input(label="S", key=f"Strength{i}", value=unit_0.strength, min_value=0, max_value=10, step=1)
        with cols[2]:
            toughness = st.number_input(label="T", key=f"Toughness{i}", value=unit_0.toughness, min_value=0, max_value=10, step=1)
        with cols[3]:
            initiative = st.number_input(label="I", key=f"Initiative{i}", value=unit_0.initiative, min_value=0, max_value=10, step=1)
        with cols[4]:
            attacks = st.number_input(label="A", key=f"Attacks{i}", value=unit_0.attacks, min_value=1, max_value=10, step=1)
        with cols[5]:
            wounds = st.number_input(label="W", key=f"Wounds{i}", value=unit_0.wounds, min_value=0, max_value=10, step=1)
        with cols[6]:
            armor_save = st.number_input(label="Armor", key=f"ArmorSave{i}", value=7, min_value=2, max_value=7, step=1)
        with cols[7]:
            ward_save = st.number_input(label="Ward", key=f"WardSave{i}", value=7, min_value=2, max_value=7, step=1)
        with cols[8]:
            regen_save = st.number_input(label="Regen", key=f"RegenSave{i}", value=7, min_value=2, max_value=7, step=1)

        fighters = st.number_input(label="Fighters", key=f"Fighters{i}", value=10, min_value=1,
                                   step=1)

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
                name=unit_0.name,
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

        name0 = units[0].single_unit.name
        name1 = units[1].single_unit.name

        if name0 == name1:
            name0 = "unit 0:" + name0
            name1 = "unit 1" + name1

        st.markdown(f"Average wounds:  on {name0}:  `{np.mean(all_w0)}` on {name1}:  `{np.mean(all_w1)}`")

        fig = px.histogram(
            pd.DataFrame(data={name0: all_w0,name1: all_w1}),
            marginal="box",
            barmode="overlay",
            color_discrete_map={
                name0: "red",
                name1: "blue"
            }

        )
        st.plotly_chart(fig)
