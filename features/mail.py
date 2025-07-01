import os
import re
import smtplib
import tempfile
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
    # Support multiple natural language triggers
    match = re.search(r"(?i)(mail|email|send)\s+(it|this)?\s*to\s+([\w\.-]+@[\w\.-]+)", update.message.text)
    if not match:
        return
    recipient = match.group(3)
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

async def mail_document_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        await send_long_message(update.message, "❌ Email credentials are not set. Please configure BOT_EMAIL_ADDRESS and BOT_EMAIL_PASSWORD in your environment.")
        return
    if not update.message or not update.message.document or not update.message.caption:
        return
    match = re.search(r"(?i)(mail|email|send)\s+(it|this)?\s*to\s+([\w\.-]+@[\w\.-]+)", update.message.caption)
    if not match:
        return
    recipient = match.group(3)
    file = update.message.document
    file_obj = await file.get_file()
    with tempfile.NamedTemporaryFile(delete=False, suffix="." + file.file_name.split(".")[-1]) as tmp:
        await file_obj.download_to_drive(tmp.name)
        tmp_path = tmp.name
    subject = f"Document from Telegram Bot: {file.file_name}"
    body = f"Please find the attached document: {file.file_name}"
    msg = EmailMessage()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.set_content(body)
    with open(tmp_path, "rb") as f:
        msg.add_attachment(f.read(), maintype="application", subtype="octet-stream", filename=file.file_name)
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        await send_long_message(update.message, f"✅ Document '{file.file_name}' sent to {recipient}!")
    except Exception as e:
        await send_long_message(update.message, f"❌ Failed to send document: {e}")
    finally:
        os.remove(tmp_path)
