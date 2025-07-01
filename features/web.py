import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ContextTypes
from core.helpers import send_long_message
from core.models import MODELS, DEFAULT_MODEL, MODEL_PERSONALITIES, SYSTEM_PROMPT
from core.openai_client import client

async def scrape(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id if update.effective_chat else None
    if chat_id is None or not context.args:
        await send_long_message(update.message, "Usage: /scrape <url>")
        return
    url = context.args[0]
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        paragraphs = soup.find_all('p')
        text = '\n'.join(p.get_text() for p in paragraphs)
        if not text.strip():
            text = soup.get_text()
        max_len = 4000
        text_to_analyze = text[:max_len]
    except Exception as e:
        await send_long_message(update.message, f"Failed to fetch or parse the webpage: {e}")
        return
    await send_long_message(update.message, "Analyzing the web page content with AI...")
    model_key = context.user_data.get('model_key')
    model = MODELS.get(model_key, DEFAULT_MODEL)
    tone = context.user_data.get('tone', "default")
    tone_prompt = context.user_data.get('tone_prompt')
    models_with_system = {"deepseek", "mistral", "nvidia"}
    history = []
    if model_key in models_with_system:
        if tone_prompt:
            history.append({"role": "system", "content": tone_prompt})
        else:
            personality = MODEL_PERSONALITIES.get(model_key, SYSTEM_PROMPT)
            history.append({"role": "system", "content": personality})
    history.append({"role": "user", "content": f"Analyze the following web page and provide a summary, key points, and any insights or recommendations.\n\n{text_to_analyze}"})
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=history,
            temperature=0.5,
            top_p=0.95
        )
        ai_reply = completion.choices[0].message.content or "(No response)"
    except Exception as e:
        ai_reply = "Sorry, I encountered an error analyzing the web page."
    await send_long_message(update.message, ai_reply)
