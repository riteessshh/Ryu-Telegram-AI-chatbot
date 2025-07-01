import os
import json
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from core.helpers import send_long_message
import smtplib
from email.message import EmailMessage
from telegram.ext import MessageHandler, filters
import re

SCHEDULE_DIR = "user_schedules"
os.makedirs(SCHEDULE_DIR, exist_ok=True)

EMAIL_ADDRESS = os.getenv("BOT_EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("BOT_EMAIL_PASSWORD")

user_emails = {}

def get_schedule_path(chat_id):
    return os.path.join(SCHEDULE_DIR, f"{chat_id}.json")

def load_schedule(chat_id):
    path = get_schedule_path(chat_id)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_schedule(chat_id, events):
    path = get_schedule_path(chat_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=2)

def create_ics_file(summary, start_dt, end_dt, description=None):
    dtstamp = start_dt.strftime('%Y%m%dT%H%M%SZ')
    dtstart = start_dt.strftime('%Y%m%dT%H%M%SZ')
    dtend = end_dt.strftime('%Y%m%dT%H%M%SZ')
    ics = f"""BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//YourBot//EN\nBEGIN:VEVENT\nUID:{dtstamp}@yourbot\nDTSTAMP:{dtstamp}\nDTSTART:{dtstart}\nDTEND:{dtend}\nSUMMARY:{summary}\nDESCRIPTION:{description or ''}\nEND:VEVENT\nEND:VCALENDAR\n"""
    return ics

def set_user_email(chat_id, email):
    user_emails[str(chat_id)] = email

def get_user_email(chat_id):
    return user_emails.get(str(chat_id))

async def schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id if update.effective_chat else None
    if not context.args or len(context.args) < 3:
        await send_long_message(update.message, "Usage: /schedule <date> <time> <event>\nExample: /schedule 2025-07-01 15:00 Doctor appointment")
        return
    date_str = context.args[0]
    time_str = context.args[1]
    event = " ".join(context.args[2:])
    try:
        dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    except ValueError:
        await send_long_message(update.message, "Invalid date/time format. Use YYYY-MM-DD HH:MM (24h). Example: /schedule 2025-07-01 15:00 Doctor appointment")
        return
    events = load_schedule(chat_id)
    events.append({"datetime": dt.isoformat(), "event": event})
    save_schedule(chat_id, events)
    # Ask for email if not known
    user_email = get_user_email(chat_id)
    if not user_email:
        await send_long_message(update.message, "Please provide your email address to receive calendar invites. Reply with: my email is youremail@example.com")
        return
    # Send .ics calendar invite to user via email
    if EMAIL_ADDRESS and EMAIL_PASSWORD:
        recipient = user_email
        end_dt = dt + timedelta(hours=1)
        ics_content = create_ics_file(event, dt, end_dt)
        msg = EmailMessage()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = recipient
        msg["Subject"] = f"Calendar Event: {event}"
        msg.set_content(f"You scheduled: {event} at {dt.strftime('%Y-%m-%d %H:%M')}.\nSee attached to add to your calendar.")
        msg.add_attachment(ics_content, maintype="text", subtype="calendar", filename="event.ics")
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                smtp.send_message(msg)
            mail_msg = f"\n📧 Calendar invite sent to {recipient}."
        except Exception as e:
            mail_msg = f"\n⚠️ Could not send calendar invite: {e}"
    else:
        mail_msg = ""
    await send_long_message(update.message, f"✅ Scheduled: {event} at {dt.strftime('%Y-%m-%d %H:%M')}{mail_msg}")
    # List upcoming events
    upcoming = [f"{datetime.fromisoformat(e['datetime']).strftime('%Y-%m-%d %H:%M')}: {e['event']}" for e in events if datetime.fromisoformat(e['datetime']) >= datetime.now()]
    if upcoming:
        await send_long_message(update.message, "Your upcoming events:\n" + "\n".join(upcoming))
    else:
        await send_long_message(update.message, "No upcoming events.")

async def set_email_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id if update.effective_chat else None
    if not update.message or not update.message.text:
        return
    # Support multiple ways of saying the same thing
    patterns = [
        r"my email is ([\w\.-]+@[\w\.-]+)",
        r"set my email to ([\w\.-]+@[\w\.-]+)",
        r"email address is ([\w\.-]+@[\w\.-]+)",
        r"use ([\w\.-]+@[\w\.-]+) for calendar",
        r"send invites to ([\w\.-]+@[\w\.-]+)"
    ]
    email = None
    for pat in patterns:
        match = re.search(pat, update.message.text, re.IGNORECASE)
        if match:
            email = match.group(1)
            break
    if email:
        set_user_email(chat_id, email)
        await send_long_message(update.message, f"✅ Your email address has been set to {email}. Now you can use /schedule to receive calendar invites.")
