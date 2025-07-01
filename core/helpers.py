import os
import json
import re
import logging
from telegram.constants import ParseMode
from core.config import HISTORY_DIR

logger = logging.getLogger(__name__)

def get_history_path(chat_id: int) -> str:
    return os.path.join(HISTORY_DIR, f"{chat_id}.json")

def load_history(chat_id: int) -> list:
    path = get_history_path(chat_id)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, ValueError):
            logger.warning(f"History file {path} is empty or invalid. Resetting history.")
            return []
    return []

def save_history(chat_id: int, messages: list):
    path = get_history_path(chat_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

def escape_markdown(text: str) -> str:
    escape_chars = r'[_*\[\]()~`>#+\-=|{}.!]'  # Telegram MarkdownV2
    return re.sub(escape_chars, lambda m: '\\' + m.group(0), text)

async def send_long_message(message, text):
    max_length = 4096
    for i in range(0, len(text), max_length):
        await message.reply_text(text[i:i+max_length], parse_mode='HTML', disable_web_page_preview=True)
