from telegram import Update
from telegram.ext import ContextTypes
from core.helpers import send_long_message, load_history, save_history
from core.models import MODELS, DEFAULT_MODEL, MODEL_PERSONALITIES, SYSTEM_PROMPT
from core.openai_client import client
from features.tone import get_user_tone, TONE_SYSTEM_PROMPTS
from features.model_management import get_user_model
from features.discussion import is_discussion_enabled
from features.mail import set_last_ai_response

async def chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id if update.effective_chat else None
    user_text = (update.message.text if update.message and update.message.text else "").strip()
    if chat_id is None or not user_text:
        return
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    # Determine user tone
    tone = get_user_tone(chat_id)
    tone_prompt = TONE_SYSTEM_PROMPTS.get(tone)
    # Discussion Mode logic
    if is_discussion_enabled(chat_id):
        processing_message = None
        if update.message:
            processing_message = await update.message.reply_text("⏳ Response is currently in processing, please wait for a moment...")
        responses = {}
        for key, model in MODELS.items():
            history = []
            personality = MODEL_PERSONALITIES.get(key, SYSTEM_PROMPT)
            if key in {"deepseek", "mistral", "nvidia"}:
                if tone_prompt:
                    history.append({"role": "system", "content": tone_prompt})
                else:
                    history.append({"role": "system", "content": personality})
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
                responses[key] = f"Error: {e}"
        discussion_prompt = (
            "You are an expert AI assistant. Here are answers from four different AI models to the same question. "
            "Discuss, compare, and provide the best possible answer for the user.\n\n" +
            "\n\n".join([f"{k.upper()} says: {v}" for k, v in responses.items()])
        )
        synth_history = [{"role": "system", "content": MODEL_PERSONALITIES["deepseek"]}, {"role": "user", "content": discussion_prompt}]
        try:
            synth_completion = client.chat.completions.create(
                model=MODELS["deepseek"],
                messages=synth_history,
                temperature=0.5,
                top_p=0.95
            )
            final_reply = synth_completion.choices[0].message.content or "(No response)"
        except Exception as e:
            final_reply = "Sorry, I encountered an error during the discussion synthesis."
        if processing_message:
            try:
                await processing_message.delete()
            except Exception:
                pass
        await send_long_message(update.message, "🤖 Discussion Mode Result:\n" + final_reply)
        return
    # Use user-selected model if set, else default
    model_key = get_user_model(chat_id)
    model = MODELS.get(model_key, DEFAULT_MODEL)
    model_display = model_key if model_key in MODELS else list(MODELS.keys())[0]
    models_with_system = {"deepseek", "mistral", "nvidia"}
    history = load_history(chat_id)
    if not history:
        if model_key in models_with_system:
            if tone_prompt:
                history = [{"role": "system", "content": tone_prompt}]
            else:
                personality = MODEL_PERSONALITIES.get(model_key, SYSTEM_PROMPT)
                history = [{"role": "system", "content": personality}]
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
        bot_reply = f"Sorry, I encountered an error fetching the response. {e}"
    if update.message:
        prefix = f"Ryu ({model_display}):\n"
        await send_long_message(update.message, prefix + bot_reply)
        # Store the full formatted message as the last AI response (undo previous change)
        set_last_ai_response(chat_id, prefix + bot_reply)
    history.append({"role": "assistant", "content": str(bot_reply)})
    save_history(chat_id, history)
