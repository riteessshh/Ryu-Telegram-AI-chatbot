from telegram import Update
from telegram.ext import ContextTypes
from core.helpers import send_long_message

discussion_mode = {}

async def discussion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id if update.effective_chat else None
    if chat_id is None:
        return
    enabled = discussion_mode.get(str(chat_id), False)
    if enabled:
        discussion_mode[str(chat_id)] = False
        await send_long_message(update.message, "Discussion Mode disabled. You will now get answers from your selected model only.")
    else:
        discussion_mode[str(chat_id)] = True
        await send_long_message(update.message, "Discussion Mode enabled! All four AI models will discuss and provide a combined answer.")

def is_discussion_enabled(chat_id):
    return discussion_mode.get(str(chat_id), False)
