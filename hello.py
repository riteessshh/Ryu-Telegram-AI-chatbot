import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from core.config import TELEGRAM_TOKEN
from features.commands import start, clear, stop, error_handler
from features.model_management import setmodel, model
from features.tone import settone
from features.discussion import discussion
from features.document import analyze_document, document_handler
from features.web import scrape
from features.chat import chat_handler

# ===== Logging =====
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

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
    app.add_handler(CommandHandler("analyze", analyze_document))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("settone", settone))
    app.add_handler(CommandHandler("scrape", scrape))
    app.add_handler(MessageHandler(filters.Document.ALL, document_handler))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), chat_handler))
    app.add_error_handler(error_handler)
    logger.info("Bot started. Listening for messages...")
    app.run_polling()

if __name__ == '__main__':
    main()
