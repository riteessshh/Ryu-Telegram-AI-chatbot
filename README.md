# Telegram AI Chatbot (Modular, Feature-Based)

This project is a modular, feature-rich Telegram AI chatbot built with Python. It supports multiple AI models, tone switching, document/web analysis, and personalized tasks like sending mail and scheduling events with .ics calendar invites (no Google Calendar API required).

## Features

- **Multi-model AI chat**: Switch between Gemma, Deepseek, Mistral, Nvidia Llama, Qwen models. Use `/setmodel` to see and select available models interactively.
- **Tone switching**: `/settone <tone>` (sarcastic, friendly, professional, concise, motivational, humorous, default)
- **Discussion mode**: `/discussion` — get a combined answer from all models.
- **Document analysis**: Send a PDF or DOCX and get an AI summary.
- **Web analysis**: `/scrape <url>` — summarize and analyze web pages.
- **Personalized tasks**:
  - **Send mail**: `/sendmail <recipient> <subject> <body>`
  - **Natural language mail**: Say `mail it to someone@example.com` after an AI response to send that response as an email (supports attachments).
  - **Schedule events**: `/schedule <date> <time> <event>` (sends .ics calendar invite via email)
  - **Set your email**: Use `/setemail <your@email.com>` or say `my email is ...` or `set my email to ...` (multiple natural language patterns supported)
- **HTML formatting** and long message support.
- **Robust error handling** and user feedback.
- **Extensible modular design**: Add new features easily in `features/`.

## Modular Code Structure

- `hello.py` — Main entry point, only wires up the bot and handlers.
- `core/` — Shared logic (config, helpers, persistence, OpenAI client, logging)
- `features/` — Each feature in its own module:
  - `model_management.py` — Model switching, preferences
  - `tone.py` — Tone switching
  - `discussion.py` — Discussion mode
  - `document.py` — PDF/DOCX analysis
  - `web.py` — Web scraping/analysis
  - `chat.py` — Main chat handler
  - `commands.py` — Start, clear, stop, error handler
  - `mail.py` — Email sending (command and natural language)
  - `schedule.py` — Scheduling (with .ics calendar invite)

## Supported AI Models

- **Gemma (Google)**: General-purpose, high-quality model
- **Deepseek**: Fast, balanced, and reliable for most tasks
- **Mistral**: Good for creative and open-ended responses
- **Nvidia Llama**: Large, advanced, and powerful model
- **Qwen**: Large, advanced, and multilingual model from Alibaba

## Email & Scheduling Feature Setup

To enable the mail and scheduling features, set these environment variables:

```
BOT_EMAIL_ADDRESS=yourbot@gmail.com
BOT_EMAIL_PASSWORD=your_app_password
```

- The bot uses Gmail SMTP by default. For other providers, update the SMTP settings in `features/mail.py`.
- The `/sendmail` command requires: `/sendmail recipient@example.com Subject Body text here`
- To send the last AI response as an email, say: `mail it to recipient@example.com`
- To schedule an event and send a calendar invite, use: `/schedule 2025-07-01 15:00 Meeting with team`
- You can set your email using `/setemail you@example.com` or natural language ("my email is ...").
- User emails are currently stored in memory (not persistent across restarts).

## Getting Started

1. Clone the repo and install dependencies (`pip install -r requirements.txt`).
2. Set up your `.env` file with Telegram and OpenRouter API keys, and email credentials.
3. Run `python hello.py`.

## Extending

Add new features by creating a new module in `features/` and registering its handler in `hello.py`.

---

For more details, see comments in each module.

## Model selection prompt

- When you use `/setmodel` without arguments, the bot will show a list of available models and ask you to choose.

