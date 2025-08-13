import logging
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Dict

import streamlit as st
import psycopg2
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Player:
    id: int
    name: str
    email: str
    mmr: int
    discord_id: int
    discord_username: str
    discord_discriminator: str

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
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


def get_players():
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM players")
    rows = cur.fetchall()
    cur.close()
    # conn.close()
    return [{"id": r[0], "name": r[1]} for r in rows]

def add_match(match_datetime: datetime):
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO matches (created_at) VALUES (%s) RETURNING id",
        (match_datetime,)
    )
    match_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    # conn.close()
    return match_id

def insert_or_get_player(user_info: Dict)->Player:
    logging.info(f"insert_or_get_player: {user_info}")
    cur = conn.cursor()

    tx = """
    INSERT INTO players (
        name,
        email,
        password_hash,
        mmr,
        discord_id,
        discord_username,
        discord_discriminator
    )
    VALUES (
        %s, '', '', 2000, %s, %s, %s
    )
    ON CONFLICT (discord_id)
    DO UPDATE SET
        name = EXCLUDED.name,
        discord_username = EXCLUDED.discord_username,
        discord_discriminator = EXCLUDED.discord_discriminator
    RETURNING id, name, email, mmr, discord_id, discord_username, discord_discriminator
    """

    params = (
        user_info['username'],
        user_info['id'],
        user_info['username'],
        user_info['discriminator']
    )

    logging.info(f"Executing insert/update for discord_id={user_info['id']}")
    cur.execute(tx, params)
    row = cur.fetchone()
    conn.commit()
    cur.close()
    return Player(*row)

def delete_match(match_id):
    cur = conn.cursor()
    cur.execute("DELETE FROM matches WHERE id = %s", (match_id,))
    conn.commit()
    cur.close()
    # conn.close()

def get_matches():
    cur = conn.cursor()
    cur.execute("SELECT id, created_at FROM matches ORDER BY created_at DESC")
    rows = cur.fetchall()
    cur.close()
    # conn.close()
    return [{"id": r[0], "created_at": r[1]} for r in rows]

def add_match_participant(match_id, player_id, faction_id, mmr_before, mmr_after, result):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO match_participants
            (match_id, player_id, faction_id, mmr_before, mmr_after, result)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (match_id, player_id, faction_id, mmr_before, mmr_after, result))
    conn.commit()
    cur.close()
    # conn.close()

def get_match_participants(match_id):
    cur = conn.cursor()
    cur.execute("""
        SELECT mp.player_id, p.name, mp.faction_id, mp.mmr_before, mp.mmr_after, mp.result
        FROM match_participants mp
        JOIN players p ON mp.player_id = p.id
        WHERE mp.match_id = %s
        ORDER BY p.name
    """, (match_id,))
    rows = cur.fetchall()
    cur.close()
    # conn.close()
    return [
        {
            "player_id": r[0],
            "player_name": r[1],
            "faction_id": r[2],
            "mmr_before": r[3],
            "mmr_after": r[4],
            "result": r[5],
        }
        for r in rows
    ]
