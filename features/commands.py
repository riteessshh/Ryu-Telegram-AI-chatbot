from telegram import Update
from telegram.ext import ContextTypes
from core.helpers import send_long_message
import logging

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await send_long_message(update.message, "👋 Hi! I'm your AI agent.\n\nType your message to begin!")

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id if update.effective_chat else None
    if chat_id is not None:
        context.user_data['history'] = []
    if update.message:
        await send_long_message(update.message, 'Conversation history cleared.')

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await send_long_message(update.message, "👋 Thank you for chatting! If you need me again, just send a message. Goodbye!")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
