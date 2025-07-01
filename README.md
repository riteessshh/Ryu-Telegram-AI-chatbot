# Ryu Telegram Chatbot

## Overview

Ryu is a powerful, multi-model Telegram chatbot built in Python. It leverages the OpenRouter API to access several leading AI models (Deepseek, Gemma, Mistral, Nvidia Llama) and provides:
- Persistent user chat history
- Per-user model preferences
- A unique "Discussion Mode" where all models collaborate for the best answer

---

## 🚀 Features

- ✅ **Multiple AI Models**: Switch between Deepseek, Gemma, Mistral, and Nvidia Llama on the fly.
- 🤖 **Discussion Mode**: `/discussion` toggles a mode where all four models discuss your question and a top model (Deepseek) synthesizes the best answer.
- ⏳ **Processing Notification**: In Discussion Mode, the bot immediately notifies you that your response is being processed.
- 💬 **Session History**: Maintains per-user conversation history.
- 📁 **Model Preferences**: Remembers your last-used model.
- 🔐 **Secure API Keys**: Uses `.env` for secrets.
- 🧠 **Intelligent Responses**: Each model brings its own strengths.

---

## 📦 Dependencies

- `python-telegram-bot`
- `openai` (for OpenRouter)
- `python-dotenv`

Install with:
```bash
pip install python-telegram-bot openai python-dotenv
```

---

## ⚙️ Environment Setup

Create a `.env` file in your project root:
```env
TELEGRAM_TOKEN=your_telegram_bot_token
OPENROUTER_API_KEY=your_openrouter_api_key
```

---

## 🛠️ How It Works

- Loads API keys from `.env`
- Defines available models and their descriptions
- Stores user model preferences in `model_prefs.json`
- Maintains chat history in `chat_histories/`

---

## 💡 Bot Commands

| Command         | Description                                                        |
|----------------|--------------------------------------------------------------------|
| `/start`       | Welcome message and current model info                              |
| `/model`       | Show your current selected model                                    |
| `/setmodel <model>` | Switch to a different model (see table below)                  |
| `/clear`       | Clear your chat history                                             |
| `/stop`        | End the conversation politely                                       |
| `/discussion`  | Toggle Discussion Mode (all models collaborate for each answer)     |

---

## 🤝 Discussion Mode

When enabled:
- Your message is sent to all four models.
- Each model responds independently.
- Their answers are combined and sent to a synthesizer model (Deepseek) with a prompt to discuss, compare, and provide the best answer.
- You receive the synthesized answer, leveraging the strengths of all models.
- While processing, you see a "please wait" message for better user experience.

---

## 🧠 Available Models

| Key        | Model ID                                        | Description                   |
|------------|-------------------------------------------------|-------------------------------|
| `gemma`    | `google/gemma-3n-e4b-it:free`                   | Google Gemma: general purpose |
| `deepseek` | `deepseek/deepseek-chat-v3-0324:free`           | Fast & balanced               |
| `mistral`  | `mistralai/mistral-small-3.2-24b-instruct:free` | Good for creativity           |
| `nvidia`   | `nvidia/llama-3.3-nemotron-super-49b-v1:free`   | Large and powerful            |

---

## 📂 File Structure

```
project/
├── hello.py                 # Main bot logic
├── .env                     # API keys
├── model_prefs.json         # Stores model preferences
├── chat_histories/          # Conversation histories
```

---

## 🚦 Limitations

- No RASA NLU/intent handling (despite early plans)
- Depends on OpenRouter API availability
- No fallback logic for unavailable models

---

## 🛣️ Future Enhancements

- RASA integration for intent/entity recognition
- Admin control over model usage
- Voice or image input support

---

## 👤 How to Use the Bot

1. Start by messaging `/start` to the bot on Telegram.
2. Type your prompt and receive responses.
3. Use `/setmodel <model>` to switch between available models.
4. Use `/clear` to wipe the conversation.
5. Use `/model` anytime to check your current AI model.
6. Use `/discussion` to enable or disable Discussion Mode.

---

## ▶️ Running the Bot

```bash
python hello.py
```

---

## 📜 License

MIT Licensed. Developed for exploration of LLM integrations via OpenRouter.

---

> ⚠️ **Note**: Despite early references, RASA is *not* integrated into this code. It purely works as an OpenRouter client using `openai.ChatCompletion` interface.

