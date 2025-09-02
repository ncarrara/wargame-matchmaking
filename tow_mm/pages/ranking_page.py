from typing import List

from tow_mm.data_model import Player
from tow_mm.widgets.rank_component import display_rank_widget


def display_ranking_page(players: List[Player], current_player: Player, top: int):

    display_rank_widget(players=players, current_player=current_player, top=top)
