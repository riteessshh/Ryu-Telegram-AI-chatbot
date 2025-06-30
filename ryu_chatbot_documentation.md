# Ryu Telegram Chatbot — Documentation

## Overview

Ryu is a Telegram chatbot that allows users to interact with multiple AI models (via OpenRouter API) through a conversational interface. This bot is implemented in Python using the `python-telegram-bot` library and integrates multiple LLMs (e.g., Deepseek, Gemma, Mistral, Nvidia Llama) with persistent user history and model preferences.

---

## Features

- ✅ Supports multiple models with on-the-fly switching
- 📦 Uses OpenRouter API to access free AI models
- 💬 Maintains session-wise conversation history
- 📁 Stores user model preferences
- 🔐 Uses .env file to securely store API keys
- 🧠 Returns model-specific intelligent responses based on prompts

---

## Dependencies

- `python-telegram-bot`
- `openai` (for OpenRouter)
- `python-dotenv`

Install them using pip:

```bash
pip install python-telegram-bot openai python-dotenv
```

---

## Environment Setup

Create a `.env` file:

```env
TELEGRAM_TOKEN=your_telegram_bot_token
OPENROUTER_API_KEY=your_openrouter_api_key
```

---

## How It Works

### Startup & Configuration

- Loads Telegram bot token and OpenRouter key from `.env`
- Defines available models and their descriptions
- Sets up persistent user model preferences in `model_prefs.json`
- Initializes conversation history in `chat_histories/`

### Bot Commands

- `/start` — Shows welcome message and current model
- `/model` — Displays current selected model
- `/setmodel <model>` — Switches to a selected model
- `/clear` — Clears chat history
- `/stop` — Ends conversation politely

### Chat Handling

- Appends user messages to the chat history
- Sends message + history to selected OpenRouter model
- Displays AI response tagged with model name (e.g., Ryu (deepseek): ...)
- Stores updated history for session persistence

### Available Models (via OpenRouter)

| Key        | Model ID                                        | Description                   |
| ---------- | ----------------------------------------------- | ----------------------------- |
| `gemma`    | `google/gemma-3n-e4b-it:free`                   | Google Gemma: general purpose |
| `deepseek` | `deepseek/deepseek-chat-v3-0324:free`           | Fast & balanced               |
| `mistral`  | `mistralai/mistral-small-3.2-24b-instruct:free` | Good for creativity           |
| `nvidia`   | `nvidia/llama-3.3-nemotron-super-49b-v1:free`   | Large and powerful            |

---

## File Structure

```
project/
├── hello.py                 # Main bot logic
├── .env                     # API keys
├── model_prefs.json         # Stores model preferences
├── chat_histories/          # Conversation histories
```

---

## Limitations

- No RASA NLU/intent handling included despite earlier plans
- Depends entirely on OpenRouter API availability
- No fallback logic for unavailable models

---

## Future Enhancements

- RASA integration for intent/entity recognition
- Admin control over model usage
- Voice or image input support

---

## How to Use the Bot (as a user)

1. Start by messaging `/start` to the bot on Telegram.
2. Type your prompt and receive responses.
3. Use `/setmodel <model>` to switch between available models.
4. Use `/clear` to wipe the conversation.
5. Use `/model` anytime to check your current AI model.

---

## Running the Bot

```bash
python hello.py
```

---

## Contact & License

MIT Licensed. Developed for exploration of LLM integrations via OpenRouter.

---

> ⚠️ **Note**: Despite early references, RASA is *not* integrated into this code. It purely works as an OpenRouter client using `openai.ChatCompletion` interface.

