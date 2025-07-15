import os
import io
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# ✅ توکن رباتت
BOT_TOKEN = '7765218657:AAFoqWQHdb60mDlyXfHi7_6EevAbbCKr39w'

# ✅ نام فایل کلید گوگل
SERVICE_ACCOUNT_FILE = 'telegramdrivebot-466008-a4719bd7b9e8.json'

# ✅ آیدی پوشه درایو
DRIVE_FOLDER_ID = '1AkG8phkFnXoa1bsziMZaUBADjJhh-0Vw'

# اتصال به گوگل درایو
SCOPES = ['https://www.googleapis.com/auth/drive']
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=credentials)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! فایل بفرست تا برات روی Google Drive آپلود کنم.")

async def upload_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    share_link = f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"
    await update.message.reply_text(f"✅ فایل آپلود شد:\n{share_link}")

# اجرای ربات
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.Document.ALL, upload_file))
app.run_polling()