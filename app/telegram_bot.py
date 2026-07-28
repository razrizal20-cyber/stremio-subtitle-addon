from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from .config import BOT_TOKEN

application = Application.builder().token(BOT_TOKEN).build()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ Bot aktif.\n\nHantar fail .srt kepada saya."
    )


application.add_handler(
    CommandHandler("start", start)
)
