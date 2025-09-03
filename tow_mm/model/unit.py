import dataclasses

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
    res =  np.random.randint(low=1, high=7, size=size)
    # print(res)
    return res

def unit_attack(attacker: Unit, defender: Unit):
    # print(attacker.single_unit.name)
    total_attack = attacker.single_unit.attacks * attacker.fighters

    hit_th = TO_HIT_CHART[attacker.single_unit.weapon_skill - 1][defender.single_unit.weapon_skill - 1]
    wound_th = TO_WOUND_CHART[attacker.single_unit.strength - 1][defender.single_unit.toughness - 1]
    # print(f"to hit: {hit_th}+")
    # print(f"to wound: {wound_th}+")
    hits = sum([x >= hit_th for x in roll_d6(total_attack)])
    wounds = sum([x >= wound_th for x in roll_d6(hits)])
    # print(f"wound on {defender.single_unit.name} => {wounds}")
    # return wounds
    if wounds == 0:
        return 0

    wound_after_amor = wounds - sum([x >= defender.single_unit.armor for x in roll_d6(wounds)])

    if wound_after_amor == 0:
        return 0

    wound_after_ward = wound_after_amor - sum([x >= defender.single_unit.ward for x in roll_d6(wound_after_amor)])

    if wound_after_ward == 0:
        return 0

    wound_after_regen = wound_after_ward - sum([x >= defender.single_unit.regen for x in roll_d6(wound_after_ward)])

    return wound_after_regen

# TODO fix bug here for multiples wounds units

def close_combat_round(u0: Unit, u1: Unit):
    if u0.single_unit.initiative == u1.single_unit.initiative:
        wounds_on_u1 = unit_attack(u0, u1)
        wounds_on_u0 = unit_attack(u1, u0)
    elif u0.single_unit.initiative > u1.single_unit.initiative:
        wounds_on_u1 = unit_attack(u0, u1)
        wounds_on_u0 = unit_attack(dataclasses.replace(u1, fighters=max(u1.fighters - wounds_on_u1, 0)), u0)
    else:
        wounds_on_u0 = unit_attack(u1, u0)
        wounds_on_u1 = unit_attack(dataclasses.replace(u0, fighters=max(u0.fighters - wounds_on_u0, 0)), u1)

    return wounds_on_u0, wounds_on_u1


if __name__ == "__main__":


    u0 = Unit(
        single_unit=SingleUnit(
            name="u0",
            attacks=5,
            wounds=6,
            toughness=6,
            strength=5,
            base_width=0,
            initiative=1,
            leadership=0,
            base_height=0,
            ward=7,
            armor=7,
            weapon_skill=4,
            ballistic_skill=0,
            regen=7,
        ),
        fighters=1
    )

    u1 = Unit(
        single_unit=SingleUnit(
            name="u1",
            attacks=5,
            wounds=4,
            toughness=4,
            strength=5,
            base_width=0,
            initiative=5,
            leadership=0,
            base_height=0,
            ward=7,
            armor=7,
            weapon_skill=7,
            ballistic_skill=0,
            regen=7,
        ),
        fighters=1
    )

    all_w0 = 0
    all_w1 = 0

    N = 1

    for _ in range(N):
        w0, w1 = close_combat_round(u0, u1)
        all_w0 += w0
        all_w1 += w1

    print(all_w0/N, all_w1/N)
