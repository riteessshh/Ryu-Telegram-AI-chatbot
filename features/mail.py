import os
import re
import smtplib
from email.message import EmailMessage
from telegram import Update
from telegram.ext import ContextTypes
from core.helpers import send_long_message

EMAIL_ADDRESS = os.getenv("BOT_EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("BOT_EMAIL_PASSWORD")

# In-memory storage for last AI response per chat
last_ai_response = {}

def set_last_ai_response(chat_id, text):
    last_ai_response[str(chat_id)] = text

def get_last_ai_response(chat_id):
    return last_ai_response.get(str(chat_id), None)

async def sendmail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        await send_long_message(update.message, "❌ Email credentials are not set. Please configure BOT_EMAIL_ADDRESS and BOT_EMAIL_PASSWORD in your environment.")
        return
    if not context.args or len(context.args) < 3:
        await send_long_message(update.message, "Usage: /sendmail <recipient> <subject> <body>")
        return
    recipient = context.args[0]
    subject = context.args[1]
    body = " ".join(context.args[2:])
    msg = EmailMessage()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.set_content(body)
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        await send_long_message(update.message, f"✅ Email sent to {recipient}!")
    except Exception as e:
        await send_long_message(update.message, f"❌ Failed to send email: {e}")

async def mail_natural_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        await send_long_message(update.message, "❌ Email credentials are not set. Please configure BOT_EMAIL_ADDRESS and BOT_EMAIL_PASSWORD in your environment.")
        return
    if not update.message or not update.message.text:
        return
    match = re.search(r"mail it to ([\w\.-]+@[\w\.-]+)", update.message.text, re.IGNORECASE)
    if not match:
        return
    recipient = match.group(1)
    chat_id = update.effective_chat.id if update.effective_chat else None
    body = get_last_ai_response(chat_id)
    if not body:
        await send_long_message(update.message, "No recent AI response to mail.")
        return
    subject = "AI Assistant Response"
    msg = EmailMessage()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.set_content(body)
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        await send_long_message(update.message, f"✅ Last AI response mailed to {recipient}!")
    except Exception as e:
        await send_long_message(update.message, f"❌ Failed to send email: {e}")
