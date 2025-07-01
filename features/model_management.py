from telegram import Update
from telegram.ext import ContextTypes
from core.models import MODELS, MODEL_DESCRIPTIONS
from core.persistence import load_model_prefs, save_model_prefs
from core.helpers import send_long_message

user_model = load_model_prefs()

def get_user_model(chat_id):
    return user_model.get(str(chat_id), None)

def set_user_model(chat_id, model_key):
    user_model[str(chat_id)] = model_key
    save_model_prefs(user_model)

async def setmodel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id if update.effective_chat else None
    if chat_id is None or not context.args:
        await send_long_message(update.message, "Usage: /setmodel <model>. Available: " + ", ".join([f"{k} - {MODEL_DESCRIPTIONS[k]}" for k in MODELS]))
        return
    model_key = context.args[0].lower()
    if model_key not in MODELS:
        await send_long_message(update.message, "Unknown model. Available: " + ", ".join([f"{k} - {MODEL_DESCRIPTIONS[k]}" for k in MODELS]))
        return
    set_user_model(chat_id, model_key)
    await send_long_message(update.message, f"✅ Model switched to: {model_key}\n{MODEL_DESCRIPTIONS[model_key]}")

async def model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id if update.effective_chat else None
    if chat_id is None:
        return
    model_key = get_user_model(chat_id)
    if model_key and model_key in MODELS:
        desc = MODEL_DESCRIPTIONS.get(model_key, "")
        await send_long_message(update.message, f"Current model: {model_key}\n{desc}")
    else:
        default_key = list(MODELS.keys())[0]
        await send_long_message(update.message, f"Current model: {default_key} (default)\n{MODEL_DESCRIPTIONS[default_key]}")
