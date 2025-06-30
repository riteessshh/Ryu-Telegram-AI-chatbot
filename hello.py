import os
import json
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from openai import OpenAI
from dotenv import load_dotenv
import re

# ===== Configuration =====
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = "https://openrouter.ai/api/v1"
HISTORY_DIR = "chat_histories"

MODELS = {
    "gemma": "google/gemma-3n-e4b-it:free",
    "deepseek": "deepseek/deepseek-chat-v3-0324:free",
    "mistral": "mistralai/mistral-small-3.2-24b-instruct:free",
    "nvidia": "nvidia/llama-3.3-nemotron-super-49b-v1:free"
}
DEFAULT_MODEL = MODELS["deepseek"]
SYSTEM_PROMPT = "You are a helpful AI assistant."

MODEL_DESCRIPTIONS = {
    "gemma": "Gemma (Google): General-purpose, high-quality model.",
    "deepseek": "Deepseek: Fast, balanced, and reliable for most tasks.",
    "mistral": "Mistral: Good for creative and open-ended responses.",
    "nvidia": "Nvidia Llama: Large, advanced, and powerful model."
}

# ===== Logging =====
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ===== Ensure Directories =====
os.makedirs(HISTORY_DIR, exist_ok=True)

# ===== OpenAI Client =====
client = OpenAI(
    base_url=BASE_URL,
    api_key=OPENROUTER_KEY,
)

# Persist user model choices in a file
MODEL_PREFS_FILE = "model_prefs.json"

def load_model_prefs():
    if os.path.exists(MODEL_PREFS_FILE):
        with open(MODEL_PREFS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_model_prefs(prefs):
    with open(MODEL_PREFS_FILE, "w", encoding="utf-8") as f:
        json.dump(prefs, f, ensure_ascii=False, indent=2)

# Store user model preferences in memory (per session)
user_model = load_model_prefs()

# ===== Helpers =====
def get_history_path(chat_id: int) -> str:
    return os.path.join(HISTORY_DIR, f"{chat_id}.json")

def load_history(chat_id: int) -> list:
    path = get_history_path(chat_id)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_history(chat_id: int, messages: list):
    path = get_history_path(chat_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

def escape_markdown(text: str) -> str:
    # Escape all special MarkdownV2 characters
    escape_chars = r'[_*\[\]()~`>#+\-=|{}.!]'  # Telegram MarkdownV2
    return re.sub(escape_chars, lambda m: '\\' + m.group(0), text)

# ===== Bot Handlers =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        chat_id = update.effective_chat.id if update.effective_chat else None
        model_key = user_model.get(str(chat_id), None)
        model = model_key if model_key in MODELS else list(MODELS.keys())[0]
        desc = MODEL_DESCRIPTIONS.get(model, "")
        await update.message.reply_text(
            f"👋 Hi! I'm your AI agent.\n\n"
            f"Current model: {model}\n{desc}\n\n"
            "You can switch models anytime with /setmodel <model>.\n"
            f"Available: {', '.join([f'{k} ("{MODEL_DESCRIPTIONS[k].split(":")[0]}")' for k in MODELS])}.\n"
            "Use /model to see your current model.\nUse /clear to reset the conversation.\n\nType your message to begin!"
        )

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id if update.effective_chat else None
    if chat_id is not None:
        save_history(chat_id, [])
    if update.message:
        await update.message.reply_text('Conversation history cleared.')

async def setmodel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id if update.effective_chat else None
    if chat_id is None or not context.args:
        await update.message.reply_text(
            "Usage: /setmodel <model>. Available: " +
            ", ".join([f"{k} - {MODEL_DESCRIPTIONS[k]}" for k in MODELS])
        )
        return
    model_key = context.args[0].lower()
    if model_key not in MODELS:
        await update.message.reply_text(
            "Unknown model. Available: " +
            ", ".join([f"{k} - {MODEL_DESCRIPTIONS[k]}" for k in MODELS])
        )
        return
    user_model[str(chat_id)] = model_key
    save_model_prefs(user_model)
    await update.message.reply_text(
        f"✅ Model switched to: {model_key}\n{MODEL_DESCRIPTIONS[model_key]}"
    )

async def model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id if update.effective_chat else None
    if chat_id is None:
        return
    model_key = user_model.get(str(chat_id), None)
    if model_key and model_key in MODELS:
        desc = MODEL_DESCRIPTIONS.get(model_key, "")
        await update.message.reply_text(f"Current model: {model_key}\n{desc}")
    else:
        default_key = list(MODELS.keys())[0]
        await update.message.reply_text(f"Current model: {default_key} (default)\n{MODEL_DESCRIPTIONS[default_key]}")

async def chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id if update.effective_chat else None
    user_text = (update.message.text if update.message and update.message.text else "").strip()
    if chat_id is None or not user_text:
        return
    history = load_history(chat_id)
    if not history:
        history = [{"role": "system", "content": SYSTEM_PROMPT}]
    history.append({"role": "user", "content": str(user_text)})
    # Use user-selected model if set, else default
    model_key = user_model.get(str(chat_id), None)
    model = MODELS.get(model_key, DEFAULT_MODEL)
    model_display = model_key if model_key in MODELS else list(MODELS.keys())[0]
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=history,
            temperature=0.5,
            top_p=0.95
        )
        bot_reply = completion.choices[0].message.content or "(No response)"
    except Exception as e:
        logger.error(f"OpenRouter API error: {e}")
        bot_reply = "Sorry, I encountered an error fetching the response."
    if update.message:
        await update.message.reply_text(
            f"Ryu ({model_display}):\n{bot_reply}"
        )
    history.append({"role": "assistant", "content": str(bot_reply)})
    save_history(chat_id, history)

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text(
            "👋 Thank you for chatting! If you need me again, just send a message. Goodbye!"
        )

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

# ===== Main =====
def main():
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_TOKEN environment variable not set.")
        return
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(CommandHandler("setmodel", setmodel))
    app.add_handler(CommandHandler("model", model))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), chat_handler))
    app.add_error_handler(error_handler)
    logger.info("Bot started. Listening for messages...")
    app.run_polling()

if __name__ == '__main__':
    main()
