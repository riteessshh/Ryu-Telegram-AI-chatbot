# Telegram AI Chatbot (Modular, Feature-Based)

This project is a modular, feature-rich Telegram AI chatbot built with Python. It supports multiple AI models, tone switching, document/web analysis, and personalized tasks like sending mail and scheduling events.

## Features

- **Multi-model AI chat**: Switch between Gemma, Deepseek, Mistral, Nvidia Llama, Qwen models.
- **Tone switching**: `/settone <tone>` (sarcastic, friendly, professional, concise, motivational, humorous, default)
- **Discussion mode**: `/discussion` — get a combined answer from all models.
- **Document analysis**: Send a PDF or DOCX and get an AI summary.
- **Web analysis**: `/scrape <url>` — summarize and analyze web pages.
- **Personalized tasks**:
  - **Send mail**: `/sendmail <recipient> <subject> <body>`
  - **Natural language mail**: Say `mail it to someone@example.com` after an AI response to send that response as an email.
  - **Schedule events**: `/schedule <date> <time> <event>` (with calendar invite)
- **HTML formatting** and long message support.
- **Robust error handling** and user feedback.

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
  - `schedule.py` — Scheduling (with calendar invite)

## Supported AI Models

- **Gemma (Google)**: General-purpose, high-quality model
- **Deepseek**: Fast, balanced, and reliable for most tasks
- **Mistral**: Good for creative and open-ended responses
- **Nvidia Llama**: Large, advanced, and powerful model
- **Qwen**: Large, advanced, and multilingual model from Alibaba

## Email Feature Setup

To enable the mail feature, set these environment variables:

```
BOT_EMAIL_ADDRESS=yourbot@gmail.com
BOT_EMAIL_PASSWORD=your_app_password
```

- The bot uses Gmail SMTP by default. For other providers, update the SMTP settings in `features/mail.py`.
- The `/sendmail` command requires: `/sendmail recipient@example.com Subject Body text here`
- To send the last AI response as an email, say: `mail it to recipient@example.com`

## Getting Started

1. Clone the repo and install dependencies.
2. Set up your `.env` file with Telegram and OpenRouter API keys, and email credentials.
3. Run `python hello.py`.

## Extending

Add new features by creating a new module in `features/` and registering its handler in `hello.py`.

---

For more details, see comments in each module.

