from telegram import Update
from telegram.ext import ContextTypes
from core.helpers import send_long_message

# Placeholder for scheduling logic
async def schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_long_message(update.message, "[Schedule feature coming soon!] Usage: /schedule <date> <time> <event>")
