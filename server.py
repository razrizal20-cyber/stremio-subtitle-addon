import os

from fastapi import FastAPI
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

app = FastAPI()

telegram_app = Application.builder().token(BOT_TOKEN).build()


@app.get("/")
async def home():
    return {
        "status": "online",
        "project": "Stremio Subtitle Addon"
    }


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ Bot aktif!\n\nSekarang hantar fail .srt kepada saya."
    )


async def receive_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.document:
        await update.message.reply_text(
            f"📄 File diterima:\n{update.message.document.file_name}"
        )


telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(
    MessageHandler(filters.Document.ALL, receive_file)
)


@app.on_event("startup")
async def startup():
    await telegram_app.initialize()
    await telegram_app.start()
    await telegram_app.updater.start_polling()


@app.on_event("shutdown")
async def shutdown():
    await telegram_app.updater.stop()
    await telegram_app.stop()
    await telegram_app.shutdown()
