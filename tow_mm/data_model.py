from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Optional

MatchResult = Literal['win', 'lose', 'draw']
MatchState = Literal['open', 'ongoing','closed', 'cancel']

@dataclass
class ChatMessage:
    message: str
    created_at: datetime
    player_id: int
    destination_player_id: int
    match_id: int
    id: Optional[int]


@dataclass
class ContactMessage:
    id: Optional[int]
    message: str
    created_at: datetime
    email: str


@dataclass
class Player:
    name: str
    email: str
    mmr: int
    id: Optional[int]
    pseudo: Optional[str]
    games_number: Optional[int]

    def get_public_name(self)-> str:
        pseudo_str = "" if not self.pseudo else f" - {self.pseudo}"

        return f"{self.name}{pseudo_str}"

@dataclass
class Match:
    created_at: datetime
    created_by: int
    venue_id: int
    id: Optional[int]
    state: MatchState
    ranked: bool

    def is_open(self)-> bool:
        return self.state == "open"

    def is_closed(self)-> bool:
        return self.state == "closed"

    def is_ongoing(self) -> bool:
        """
        Pretty obvious right
        :return:
        """
        return self.state == "ongoing"

    def can_be_delete(self)-> bool:
        return self.is_open()


@dataclass
class MatchParticipation:
    match_id: int
    player_id : int
    faction_id : int
    mmr_before : int
    mmr_after : int
    result: MatchResult
    is_ready: bool

    def won(self)-> bool:
        return self.result == "win"

    def lost(self)-> bool:
        return self.result == "lose"


@dataclass
class Faction:
    name: str
    id: Optional[int]


@dataclass
class Venue:
    name: str
    address: str
    id: Optional[int]


@dataclass
class BattleReport:
    id: Optional[int]
    content: str
    created_by: int