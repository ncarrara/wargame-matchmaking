import dataclasses
import random
import numpy as np

TO_HIT_CHART = [
    [4, 4, 5, 5, 5, 5, 5, 5, 5, 5],
    [3, 4, 4, 4, 5, 5, 5, 5, 5, 5],
    [2, 3, 4, 4, 4, 4, 5, 5, 5, 5],
    [2, 3, 3, 4, 4, 4, 4, 4, 5, 5],
    [2, 2, 3, 3, 4, 4, 4, 4, 4, 4],
    [2, 2, 3, 3, 3, 4, 4, 4, 4, 4],
    [2, 2, 2, 3, 3, 3, 4, 4, 4, 4],
    [2, 2, 2, 3, 3, 3, 3, 4, 4, 4],
    [2, 2, 2, 2, 3, 3, 3, 3, 4, 4],
    [2, 2, 2, 2, 3, 3, 3, 3, 3, 4],

]

TO_WOUND_CHART = [
    [4, 5, 6, 6, 6, 6, 0, 0, 0, 0],
    [3, 4, 5, 6, 6, 6, 6, 0, 0, 0],
    [2, 3, 4, 5, 6, 6, 6, 6, 0, 0],
    [2, 2, 3, 4, 5, 6, 6, 6, 6, 0],
    [2, 2, 2, 3, 4, 5, 6, 6, 6, 6],
    [2, 2, 2, 2, 3, 4, 5, 6, 6, 6],
    [2, 2, 2, 2, 2, 3, 4, 5, 6, 6],
    [2, 2, 2, 2, 2, 2, 3, 4, 5, 6],
    [2, 2, 2, 2, 2, 2, 2, 3, 4, 5],
    [2, 2, 2, 2, 2, 2, 2, 2, 3, 4],
]


@dataclasses.dataclass
class SingleUnit:
    name: str
    weapon_skill: int  # WS
    ballistic_skill: int  # BS
    strength: int  # S
    toughness: int  # T
    wounds: int  # W
    initiative: int  # I
    attacks: int  # A (number of attacks per model/actor)
    leadership: int  # Ld
    base_width: int
    base_height: int
    ward: int = 7
    armor: int = 7
    regen: int = 7


@dataclasses.dataclass
class Unit:
    single_unit: SingleUnit
    fighters: int


def roll_d6(size: int):
    return np.random.randint(low=1, high=6, size=size)


def unit_attack(attacker: Unit, defender: Unit):
    total_attack = attacker.single_unit.attacks * attacker.fighters

    hit_proba = TO_HIT_CHART[attacker.single_unit.weapon_skill][defender.single_unit.weapon_skill]
    wound_proba = TO_WOUND_CHART[attacker.single_unit.weapon_skill][defender.single_unit.weapon_skill]

    hits = sum([x >= hit_proba for x in roll_d6(total_attack)])
    wounds = sum([x >= wound_proba for x in roll_d6(hits)])

    wound_after_amor = wounds - sum([x >= defender.single_unit.armor for x in roll_d6(wounds)])
    wound_after_ward = wound_after_amor - sum([x >= defender.single_unit.ward for x in roll_d6(wound_after_amor)])
    wound_after_regen = wound_after_ward - sum([x >= defender.single_unit.regen for x in roll_d6(wound_after_ward)])

    return wound_after_regen


def close_combat_round(u0: Unit, u1: Unit):
    if u0.single_unit.initiative == u1.single_unit.initiative:
        wounds_on_u1 = unit_attack(u0, u1)
        wounds_on_u0 = unit_attack(u1, u0)
    elif u0.single_unit.initiative > u1.single_unit.initiative:
        wounds_on_u1 = unit_attack(u0, u1)
        wounds_on_u0 = unit_attack(dataclasses.replace(u1, fighters=max(u1.fighters - wounds_on_u1,0)), u0)
    else:
        wounds_on_u0 = unit_attack(u1, u0)
        wounds_on_u1 = unit_attack(dataclasses.replace(u0, fighters=max(u0.fighters - wounds_on_u0,0)), u1)

    return wounds_on_u0, wounds_on_u1


if __name__  == "__main__":

    u0 = Unit(
        single_unit=SingleUnit(
            name="u0",
            attacks=2,
            wounds=1,
            toughness=4,
            strength=3,
            base_width=0,
            initiative=4,
            leadership=0,
            base_height=0,
            ward=7,
            armor=5,
            weapon_skill=3,
            ballistic_skill=3,
            regen=7,
        ),
        fighters=10
    )

    u1 = Unit(
        single_unit=SingleUnit(
            name="u1",
            attacks=2,
            wounds=1,
            toughness=4,
            strength=3,
            base_width=0,
            initiative=5,
            leadership=0,
            base_height=0,
            ward=7,
            armor=5,
            weapon_skill=3,
            ballistic_skill=3,
            regen=7,
        ),
        fighters=10
    )

    all_w0 = 0
    all_w1 = 0

    for _ in range(1000):

        w0, w1 = close_combat_round(u0,u1)
        all_w0+=w0
        all_w1+=w1

    print(all_w0,all_w1)

