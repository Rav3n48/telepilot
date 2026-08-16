import os

from dotenv import load_dotenv

load_dotenv(".env")

PROXY_URL = os.getenv("PROXY_URL")
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found in .env file")
