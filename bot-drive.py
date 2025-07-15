import os
import io
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
SERVICE_ACCOUNT_FILE = 'drive-key.json'
DRIVE_FOLDER_ID = '1AkG8phkFnXoa1bsziMZaUBADjJhh-0Vw'
SCOPES = ['https://www.googleapis.com/auth/drive']
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=credentials)

app = ApplicationBuilder().token(BOT_TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! فایل رو بفرست تا آپلود کنم.")

async def upload_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.document:
        await update.message.reply_text("لطفاً فایل ارسال کن!")
        return

    file = await update.message.document.get_file()
    file_name = update.message.document.file_name

    file_bytes = io.BytesIO()
    await file.download_to_memory(out=file_bytes)
    file_bytes.seek(0)

    media = MediaIoBaseUpload(file_bytes, mimetype='application/octet-stream')
    file_metadata = {
        'name': file_name,
        'parents': [DRIVE_FOLDER_ID]
    }

    uploaded_file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    drive_service.permissions().create(
        fileId=uploaded_file.get('id'),
        body={'type': 'anyone', 'role': 'reader'},
    ).execute()

    file_id = uploaded_file.get('id')
    link = f"https://drive.google.com/file/d/{file_id}/view"
    await update.message.reply_text(f"✅ فایل آپلود شد:\n{link}")

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.Document.ALL, upload_file))

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
