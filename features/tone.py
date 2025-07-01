from telegram import Update
from telegram.ext import ContextTypes
from core.helpers import send_long_message

# Per-user tone storage (in-memory)
user_tone = {}

TONE_SYSTEM_PROMPTS = {
    "default": None,
    "sarcastic": "You are a sarcastic AI assistant. Respond to the user with a witty, dry, and sarcastic tone, but do not be rude or offensive.",
    "friendly": "You are a friendly and supportive AI assistant. Respond warmly, positively, and with encouragement.",
    "professional": "You are a professional AI assistant. Respond formally, clearly, and with expert-level detail.",
    "concise": "You are a concise AI assistant. Respond with short, direct, and to-the-point answers, avoiding unnecessary detail.",
    "motivational": "You are a motivational AI assistant. Respond with uplifting, inspiring, and positive language to encourage the user.",
    "humorous": "You are a humorous AI assistant. Respond with light-hearted, playful, and appropriate humor, but stay helpful."
}

def get_user_tone(chat_id):
    return user_tone.get(str(chat_id), "default")

def set_user_tone(chat_id, tone):
    user_tone[str(chat_id)] = tone

async def settone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id if update.effective_chat else None
    if chat_id is None or not context.args:
        await send_long_message(update.message, "Usage: /settone <tone>. Available: " + ', '.join(TONE_SYSTEM_PROMPTS.keys()))
        return
    tone = context.args[0].lower()
    if tone not in TONE_SYSTEM_PROMPTS:
        await send_long_message(update.message, "Unknown tone. Available: " + ', '.join(TONE_SYSTEM_PROMPTS.keys()))
        return
    set_user_tone(chat_id, tone)
    await send_long_message(update.message, f"✅ Tone set to: <b>{tone}</b>.")
