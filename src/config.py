import os
from dotenv import load_dotenv

load_dotenv()

TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
MAX_URLS = 2
MAX_IPS = 2
PING_TIMEOUT = 5
REQUEST_TIMEOUT = 5
MONITORING_INTERVAL = 60

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://powerbot:powerbot_password@db/powerbot_db')