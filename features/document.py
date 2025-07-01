import os
import tempfile
import docx
from PyPDF2 import PdfReader
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes
from core.helpers import send_long_message
from core.models import MODELS, DEFAULT_MODEL, MODEL_PERSONALITIES, SYSTEM_PROMPT
from core.openai_client import client

async def analyze_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_long_message(update.message, "Please send a PDF or DOCX file for analysis.")

async def document_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.document:
        return
    file = update.message.document
    file_name = file.file_name.lower()
    if not (file_name.endswith('.pdf') or file_name.endswith('.docx')):
        await send_long_message(update.message, "Unsupported file type. Please send a PDF or DOCX file.")
        return
    await update.message.chat.send_action(action=ChatAction.UPLOAD_DOCUMENT)
    file_obj = await file.get_file()
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file_name)[1]) as tmp:
        await file_obj.download_to_drive(tmp.name)
        tmp_path = tmp.name
    # Extract text
    if file_name.endswith('.pdf'):
        try:
            reader = PdfReader(tmp_path)
            text = "\n".join(page.extract_text() or '' for page in reader.pages)
        except Exception as e:
            await send_long_message(update.message, f"Failed to extract PDF text: {e}")
            os.remove(tmp_path)
            return
    elif file_name.endswith('.docx'):
        try:
            doc = docx.Document(tmp_path)
            text = "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            await send_long_message(update.message, f"Failed to extract DOCX text: {e}")
            os.remove(tmp_path)
            return
    os.remove(tmp_path)
    if not text.strip():
        await send_long_message(update.message, "No extractable text found in the document.")
        return
    # Truncate if too long for model
    max_len = 4000
    text_to_analyze = text[:max_len]
    await send_long_message(update.message, "Analyzing your document with AI...")
    # Use current model for analysis
    chat_id = update.effective_chat.id if update.effective_chat else None
    model_key = context.user_data.get('model_key')
    model = MODELS.get(model_key, DEFAULT_MODEL)
    models_with_system = {"deepseek", "mistral", "nvidia"}
    personality = MODEL_PERSONALITIES.get(model_key, SYSTEM_PROMPT)
    history = []
    if model_key in models_with_system:
        history.append({"role": "system", "content": personality})
    history.append({"role": "user", "content": f"Analyze the following document and provide a summary, key points, and any insights or recommendations.\n\n{text_to_analyze}"})
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=history,
            temperature=0.5,
            top_p=0.95
        )
        ai_reply = completion.choices[0].message.content or "(No response)"
    except Exception as e:
        ai_reply = "Sorry, I encountered an error analyzing the document."
    await send_long_message(update.message, ai_reply)
