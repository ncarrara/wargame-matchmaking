import requests
from dotenv import load_dotenv
import os
import urllib.parse
from datetime import  datetime
import logging
load_dotenv()

# --------------------
# CONFIGURATION
# --------------------
DISCORD_CLIENT_ID =  os.getenv("DISCORD_CLIENT_ID", None)
DISCORD_CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET", None)
DISCORD_REDIRECT_URI = os.getenv("DISCORD_REDIRECT_URI", "http://localhost:8501")

DISCORD_AUTH_BASE = "https://discord.com/api/oauth2/authorize"
DISCORD_TOKEN_URL = "https://discord.com/api/oauth2/token"
DISCORD_API_BASE = "https://discord.com/api"
SCOPES = ["identify"]

# --------------------
# AUTH HELPERS
# --------------------
def get_discord_auth_url():
    params = {
        "client_id": DISCORD_CLIENT_ID,
        "redirect_uri": DISCORD_REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "prompt": "consent"
    }
    return f"{DISCORD_AUTH_BASE}?{urllib.parse.urlencode(params)}"


def exchange_code_for_token(code):
    data = {
        "client_id": DISCORD_CLIENT_ID,
        "client_secret": DISCORD_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": DISCORD_REDIRECT_URI,
        "scope": " ".join(SCOPES)
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    r = requests.post(DISCORD_TOKEN_URL, data=data, headers=headers)
    return r.json()


def get_user_info(token_data):
    logging.info(f"get_user_info with token_data: {token_data}")
    token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{DISCORD_API_BASE}/users/@me", headers=headers)
    return r.json()

import extra_streamlit_components as stx
import json

COOKIE_KEY = "discord_token"

def get_cookie_manager():
    return stx.CookieManager()

COOKIE_MANAGER = get_cookie_manager()

# Save token to cookie
def save_token_data_to_cookie(token_data):
    logging.info(f"persisting token {token_data} to {COOKIE_KEY}")
    COOKIE_MANAGER.set(COOKIE_KEY, json.dumps(token_data), expires_at=datetime(2099, 1, 1))

def token_is_valid(token_data):
    return token_data is not None and "access_token" in token_data

# Load token from cookie
def load_token_data_from_cookie():

    token_json = COOKIE_MANAGER.get(COOKIE_KEY)

    logging.info(f"load_token_from_cookie {token_json} from {COOKIE_KEY}")

    if token_json:
        try:
            return json.loads(token_json)
        except Exception as e:
            logging.error(f"Cannot parse {token_json}")
            logging.exception(e)
            return None
    return None