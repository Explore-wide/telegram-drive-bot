import os
import io
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# Telegram bot token
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Google Drive service setup
SERVICE_ACCOUNT_FILE = 'drive-key.json'
DRIVE_FOLDER_ID = '1AkG8phkFnXoa1bsziMZaUBADjJhh-0Vw'

SCOPES = ['https://www.googleapis.com/auth/drive']
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=credentials)

# Create the Application
tg_app = ApplicationBuilder().token(BOT_TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! فایل رو بفرست تا آپلودش کنم.")

async def upload_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.document:
        await update.message.reply_text("فایل ارسال نشده!")
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
    link = f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"
    await update.message.reply_text(f"✅ آپلود شد:\n{link}")

# Adding handlers
tg_app.add_handler(CommandHandler("start", start))
tg_app.add_handler(MessageHandler(filters.Document.ALL, upload_file))

# Polling the bot (instead of app.run)
tg_app.run_polling()
