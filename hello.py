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

# Store user discussion mode preferences in memory (per session)
discussion_mode = {}

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

# Helper to send long messages in chunks (no formatting)
async def send_long_message(message, text):
    max_length = 4096
    for i in range(0, len(text), max_length):
        await message.reply_text(text[i:i+max_length])

# ===== Bot Handlers =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        chat_id = update.effective_chat.id if update.effective_chat else None
        model_key = user_model.get(str(chat_id), None)
        model = model_key if model_key in MODELS else list(MODELS.keys())[0]
        desc = MODEL_DESCRIPTIONS.get(model, "")
        available_models = ', '.join([f"{k} ({MODEL_DESCRIPTIONS[k].split(':')[0]})" for k in MODELS])
        text = (
            f"👋 Hi! I'm your AI agent.\n\n"
            f"Current model: {model}\n{desc}\n\n"
            "You can switch models anytime with /setmodel <model>.\n"
            f"Available: {available_models}.\n"
            "Use /model to see your current model.\nUse /clear to reset the conversation.\n\nType your message to begin!"
        )
        await send_long_message(update.message, text)

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id if update.effective_chat else None
    if chat_id is not None:
        save_history(chat_id, [])
    if update.message:
        await send_long_message(update.message, 'Conversation history cleared.')

async def setmodel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id if update.effective_chat else None
    if chat_id is None or not context.args:
        text = (
            "Usage: /setmodel <model>. Available: " +
            ", ".join([f"{k} - {MODEL_DESCRIPTIONS[k]}" for k in MODELS])
        )
        await send_long_message(update.message, text)
        return
    model_key = context.args[0].lower()
    if model_key not in MODELS:
        text = (
            "Unknown model. Available: " +
            ", ".join([f"{k} - {MODEL_DESCRIPTIONS[k]}" for k in MODELS])
        )
        await send_long_message(update.message, text)
        return
    user_model[str(chat_id)] = model_key
    save_model_prefs(user_model)
    await send_long_message(update.message, f"✅ Model switched to: {model_key}\n{MODEL_DESCRIPTIONS[model_key]}")

async def model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id if update.effective_chat else None
    if chat_id is None:
        return
    model_key = user_model.get(str(chat_id), None)
    if model_key and model_key in MODELS:
        desc = MODEL_DESCRIPTIONS.get(model_key, "")
        await send_long_message(update.message, f"Current model: {model_key}\n{desc}")
    else:
        default_key = list(MODELS.keys())[0]
        await send_long_message(update.message, f"Current model: {default_key} (default)\n{MODEL_DESCRIPTIONS[default_key]}")

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

async def chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id if update.effective_chat else None
    user_text = (update.message.text if update.message and update.message.text else "").strip()
    if chat_id is None or not user_text:
        return
    # Discussion Mode logic
    if discussion_mode.get(str(chat_id), False):
        processing_message = None
        if update.message:
            processing_message = await update.message.reply_text("⏳ Response is currently in processing, please wait for a moment...")
        responses = {}
        models_with_system = {"deepseek", "mistral", "nvidia"}
        for key, model in MODELS.items():
            history = []
            if key in models_with_system:
                history.append({"role": "system", "content": SYSTEM_PROMPT})
            history.append({"role": "user", "content": user_text})
            try:
                completion = client.chat.completions.create(
                    model=model,
                    messages=history,
                    temperature=0.5,
                    top_p=0.95
                )
                responses[key] = completion.choices[0].message.content or "(No response)"
            except Exception as e:
                logger.error(f"OpenRouter API error ({key}): {e}")
                responses[key] = f"Error: {e}"
        # Synthesize final answer using Deepseek (or Mistral if you prefer)
        discussion_prompt = (
            "You are an expert AI assistant. Here are answers from four different AI models to the same question. "
            "Discuss, compare, and provide the best possible answer for the user.\n\n" +
            "\n\n".join([f"{k.upper()} says: {v}" for k, v in responses.items()])
        )
        synth_history = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": discussion_prompt}]
        try:
            synth_completion = client.chat.completions.create(
                model=MODELS["deepseek"],
                messages=synth_history,
                temperature=0.5,
                top_p=0.95
            )
            final_reply = synth_completion.choices[0].message.content or "(No response)"
        except Exception as e:
            logger.error(f"OpenRouter API error (synth): {e}")
            final_reply = "Sorry, I encountered an error during the discussion synthesis."
        if processing_message:
            try:
                await processing_message.delete()
            except Exception:
                pass
        await send_long_message(update.message, "🤖 Discussion Mode Result:\n" + final_reply)
        return
    # Use user-selected model if set, else default
    model_key = user_model.get(str(chat_id), None)
    model = MODELS.get(model_key, DEFAULT_MODEL)
    model_display = model_key if model_key in MODELS else list(MODELS.keys())[0]
    # Only add system prompt for models that support it
    models_with_system = {"deepseek", "mistral", "nvidia"}
    history = load_history(chat_id)
    if not history:
        if model_key in models_with_system:
            history = [{"role": "system", "content": SYSTEM_PROMPT}]
        else:
            history = []
    history.append({"role": "user", "content": str(user_text)})
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
        prefix = f"Ryu ({model_display}):\n"
        await send_long_message(update.message, prefix + bot_reply)
    history.append({"role": "assistant", "content": str(bot_reply)})
    save_history(chat_id, history)

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await send_long_message(update.message, "👋 Thank you for chatting! If you need me again, just send a message. Goodbye!")

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
    app.add_handler(CommandHandler("discussion", discussion))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), chat_handler))
    app.add_error_handler(error_handler)
    logger.info("Bot started. Listening for messages...")
    app.run_polling()

if __name__ == '__main__':
    main()
