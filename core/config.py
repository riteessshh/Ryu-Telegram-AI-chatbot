import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = "https://openrouter.ai/api/v1"
HISTORY_DIR = "chat_histories"
MODEL_PREFS_FILE = "model_prefs.json"
