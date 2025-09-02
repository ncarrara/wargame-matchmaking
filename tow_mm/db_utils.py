import logging
import os
from datetime import datetime
from email.message import Message
from typing import List, Optional

import psycopg2
import streamlit as st
from dotenv import load_dotenv

from tow_mm.data_model import Player, Match, Faction, MatchParticipation, MatchResult, Venue, ChatMessage, \
    ContactMessage

load_dotenv()

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")


class CloseException(Exception):
    pass

def build_cursor():
    cur = conn.cursor()
    cur.execute("SET TIME ZONE 'UTC';")
    return cur


# --------------------
# DATABASE HELPERS
# --------------------
@st.cache_resource
def get_db_connection():
    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD
    )
    return conn


conn = get_db_connection()


def get_player(player_id: int) -> Player:
    return get_players(player_ids=[player_id])[0]


def get_players(player_ids: Optional[List[int]] = None) -> List[Player]:
    cur = build_cursor()
    if player_ids:
        query = """
                SELECT name, email, mmr, id, games_number, pseudo
                FROM players
                WHERE id in %s
            """
        cur.execute(query, (tuple(player_ids),))
    else:
        query = """
                SELECT name, email, mmr, id, games_number, pseudo
                FROM players
            """
        cur.execute(query)

    rows = cur.fetchall()
    cur.close()
    return [Player(name=row[0], email=row[1], mmr=row[2], id=row[3], games_number=row[4], pseudo=row[5]) for row in rows]


def get_messages(match_id: int, player_id: int, destination_player_id: int) -> List[ChatMessage]:
    cur = build_cursor()
    cur.execute("""
        SELECT id, message, created_at, player_id, match_id, destination_player_id
        FROM chat_messages
        WHERE match_id = %s AND ((player_id = %s AND destination_player_id = %s) OR (player_id = %s AND destination_player_id = %s))
        ORDER BY created_at ASC
    """, (match_id, player_id, destination_player_id,destination_player_id,player_id))

    rows = cur.fetchall()
    cur.close()
    return [
        ChatMessage(
            id=r[0],
            message=r[1],
            created_at=r[2],
            player_id=r[3],
            match_id=r[4],
            destination_player_id=r[5],
        )
        for r in rows
    ]

def get_contact_messages() -> List[ContactMessage]:
    cur = build_cursor()
    cur.execute("""
        SELECT id, message, created_at, email
        FROM contact_messages
        ORDER BY created_at ASC
    """, )

    rows = cur.fetchall()
    cur.close()
    return [
        ContactMessage(
            id=r[0],
            message=r[1],
            created_at=r[2],
            email=r[3],
        )
        for r in rows
    ]

def add_chat_message(message: ChatMessage):
    cur = build_cursor()
    cur.execute(
        "INSERT INTO chat_messages (match_id, player_id, message, created_at, destination_player_id) VALUES (%s, %s, %s, %s, %s) RETURNING id",
        (message.match_id, message.player_id, message.message, message.created_at, message.destination_player_id)
    )
    message_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    return message_id


def add_contact_message(message: ContactMessage):
    cur = build_cursor()
    cur.execute(
        "INSERT INTO contact_messages ( email, message, created_at) VALUES (%s, %s, %s) RETURNING id",
        (message.email, message.message, message.created_at)
    )
    message_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    return message_id

def add_match(created_by: Player, match_datetime: datetime, venue_id: int, ranked: bool):
    cur = build_cursor()
    cur.execute(
        "INSERT INTO matches (created_at, created_by, venue_id, state, ranked) VALUES (%s, %s, %s, %s, %s) RETURNING id",
        (match_datetime, created_by.id, venue_id, "open", ranked)
    )
    match_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    return match_id


def update_match(match_id: int):
    match = get_match(match_id=match_id)
    if match.is_closed():
        logging.info(f"match {match_id} already closed, nothing to do")
    else:
        parts = get_match_participations(match_id=match_id)
        cur = conn.cursor()

        if match.is_open():
            match_can_start = len(parts) ==2 and all([part.is_ready for part in parts])

            if match_can_start:
                cur.execute(
                    query="UPDATE matches SET state = %s WHERE id = %s",
                    vars=("ongoing", match_id)
                )

        elif match.is_ongoing():

            players_agree = all([part.result == "draw" for part in parts]) or {part.result for part in parts} == {"win",
                                                                                                                  "lose"}

            if not players_agree:
                logging.info("Players disagree on the result, you cannot close the match")
            else:
                p0 = get_player(parts[0].player_id)
                p1 = get_player(parts[1].player_id)

                delta = {
                    "win": 25 if match.ranked else 0,
                    "lose": -25 if match.ranked else 0,
                    "draw": 0,
                    "undefined": 0
                }

                delta_p0 = delta[parts[0].result]
                delta_p1 = delta[parts[1].result]

                d0 = {"mmr_before": p0.mmr, "mmr_after": p0.mmr + delta_p0, "player_id": p0.id, "games_number": p0.games_number+1}
                d1 = {"mmr_before": p1.mmr, "mmr_after": p1.mmr + delta_p1, "player_id": p1.id, "games_number": p1.games_number+1}
                for d in [d0, d1]:
                    cur.execute(
                        query="UPDATE match_participants SET mmr_before = %s, mmr_after = %s WHERE match_id = %s AND player_id = %s",
                        vars=(d["mmr_before"], d["mmr_after"], match_id, d["player_id"])
                    )
                    cur.execute(
                        query="UPDATE players SET mmr = %s, games_number = %s WHERE id = %s",
                        vars=(d["mmr_after"], d["games_number"], d["player_id"])
                    )

                cur.execute(
                    query="UPDATE matches SET state = %s WHERE id = %s",
                    vars=("closed", match_id)
                )
        else:
            assert False, "impossible"

        conn.commit()
        cur.close()


def insert_or_get_player(player: Player) -> Player:
    cur = build_cursor()

    tx = """
    INSERT INTO players (
        name,
        email,
        mmr,
        games_number,
        pseudo
    )
    VALUES (
        %s, %s, %s, %s, %s
    )
    ON CONFLICT (email)
    DO UPDATE SET name = players.name
    RETURNING  name, email, mmr, id, games_number, pseudo
    """

    params = (
        player.name, player.email, player.mmr, player.games_number, player.pseudo
    )

    cur.execute(tx, params)
    row = cur.fetchone()
    conn.commit()
    cur.close()
    return Player(name=row[0], email=row[1], mmr=row[2], id=row[3], games_number=row[4], pseudo=row[5])


def delete_match(match_id):
    cur = build_cursor()
    cur.execute("DELETE FROM matches WHERE id = %s", (match_id,))
    conn.commit()
    cur.close()
    # conn.close()


# @st.cache_resource
def get_factions() -> List[Faction]:
    cur = build_cursor()
    cur.execute("SELECT id, name FROM factions ORDER BY name DESC")
    rows = cur.fetchall()
    cur.close()
    return [Faction(id=r[0], name=r[1]) for r in rows]


def get_venues() -> List[Venue]:
    cur = build_cursor()
    cur.execute("SELECT id, name, address FROM venues ORDER BY id DESC")
    rows = cur.fetchall()
    cur.close()
    return [Venue(id=r[0], name=r[1], address=r[2]) for r in rows]


def get_match(match_id: int) -> Match:

    matches =  get_matches([match_id])

    if matches:
        return matches[0]
    else:
        return None

def change_pseudo(player_id: int, pseudo: str):
    cur = build_cursor()

    cur.execute(
        query="UPDATE players SET pseudo = %s WHERE id = %s",
        vars=(pseudo, player_id)
    )

def get_matches(match_ids: Optional[List[int]] = None) -> List[Match]:
    cur = build_cursor()

    if match_ids:
        query = f"""
            SELECT id, created_by, created_at, venue_id, state, ranked
            FROM matches
            WHERE id IN %s
            ORDER BY created_at DESC
        """
        cur.execute(query, (tuple(match_ids),))
    else:
        query = """
            SELECT id, created_by, created_at, venue_id, state, ranked
            FROM matches
            ORDER BY created_at DESC
        """
        cur.execute(query)

    rows = cur.fetchall()
    cur.close()
    # conn.close()
    return [Match(id=r[0], created_by=r[1], created_at=r[2], venue_id=r[3], state=r[4], ranked=r[5]) for r in rows]


def add_match_participant(match_id, player_id, faction_id, mmr_before, mmr_after, result):
    cur = build_cursor()
    cur.execute("""
        INSERT INTO match_participants
            (match_id, player_id, faction_id, mmr_before, mmr_after, result)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (match_id, player_id, faction_id, mmr_before, mmr_after, result))
    conn.commit()
    cur.close()
    # conn.close()


def delete_participation(
        match_id: int,
        player_id: int,
) -> None:
    cur = build_cursor()
    cur.execute("DELETE FROM match_participants WHERE match_id = %s AND player_id = %s", (match_id, player_id))
    conn.commit()
    cur.close()


def set_participation_ready(is_ready: bool, match_id: int, player_id: int, ):
    cur = build_cursor()
    cur.execute("UPDATE match_participants SET is_ready = %s WHERE match_id = %s AND player_id = %s",
                (is_ready, match_id, player_id))
    conn.commit()
    cur.close()

    update_match(match_id=match_id)


def set_participation_result(result: MatchResult, match_id: int, player_id: int, ):
    cur = build_cursor()
    cur.execute("UPDATE match_participants SET result = %s WHERE match_id = %s AND player_id = %s",
                (result, match_id, player_id))
    conn.commit()
    cur.close()

    update_match(match_id=match_id)


def get_match_participations(match_id: int) -> List[MatchParticipation]:
    cur = build_cursor()
    cur.execute("""
        SELECT mp.match_id, mp.player_id, mp.faction_id, mp.mmr_before, mp.mmr_after, mp.result, mp.is_ready
        FROM match_participants mp
        WHERE mp.match_id = %s
    """, (match_id,))
    rows = cur.fetchall()
    cur.close()
    return [MatchParticipation(
        match_id=r[0],
        player_id=r[1],
        faction_id=r[2],
        mmr_before=r[3],
        mmr_after=r[4],
        result=r[5],
        is_ready=r[6],
    )
        for r in rows
    ]

def get_matches_with_participations(match_ids: Optional[List[int]] = None):
    """
    Fetch matches with their participations in a single SQL query.
    Returns a list of dicts:
    {
        "match": Match,
        "participations": List[MatchParticipation]
    }
    """
    cur = build_cursor()

    if match_ids:
        query = """
            SELECT 
                m.id, m.created_by, m.created_at, m.venue_id, m.state, m.ranked,
                mp.player_id, mp.faction_id, mp.mmr_before, mp.mmr_after, mp.result, mp.is_ready
            FROM matches m
            LEFT JOIN match_participants mp ON m.id = mp.match_id
            WHERE m.id = ANY(%s)
            ORDER BY m.created_at DESC
        """
        cur.execute(query, (match_ids,))
    else:
        query = """
            SELECT 
                m.id, m.created_by, m.created_at, m.venue_id, m.state, m.ranked,
                mp.player_id, mp.faction_id, mp.mmr_before, mp.mmr_after, mp.result, mp.is_ready
            FROM matches m
            LEFT JOIN match_participants mp ON m.id = mp.match_id
            ORDER BY m.created_at DESC
        """
        cur.execute(query)

    rows = cur.fetchall()
    cur.close()

    matches_dict = {}
    for r in rows:
        match_id = r[0]
        if match_id not in matches_dict:
            matches_dict[match_id] = {
                "match": Match(
                    id=r[0],
                    created_by=r[1],
                    created_at=r[2],
                    venue_id=r[3],
                    state=r[4],
                    ranked=r[5]
                ),
                "participations": []
            }

        # If the join found a participant (can be None if no participation yet)
        if r[6] is not None:
            matches_dict[match_id]["participations"].append(
                MatchParticipation(
                    match_id=match_id,
                    player_id=r[6],
                    faction_id=r[7],
                    mmr_before=r[8],
                    mmr_after=r[9],
                    result=r[10],
                    is_ready=r[11]
                )
            )

    return matches_dict