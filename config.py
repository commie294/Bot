import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TOKEN = os.getenv("BOT_TOKEN")
    ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
    HASH_SALT = os.getenv("HASH_SALT", "default_salt")
