from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from .config import BOT_TOKEN


application = Application.builder().token(BOT_TOKEN).build()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ Bot aktif.\n\n"
        "Hantar fail subtitle .srt kepada saya."
    )


async def receive_srt(update: Update, context: ContextTypes.DEFAULT_TYPE):

    document = update.message.document

    if not document.file_name.lower().endswith(".srt"):
        await update.message.reply_text(
            "❌ Sila hantar fail .srt sahaja."
        )
        return


    context.user_data["subtitle_file"] = document.file_name


    keyboard = [
        [
            InlineKeyboardButton(
                "🎬 Movie",
                callback_data="movie"
            ),
            InlineKeyboardButton(
                "📺 Series",
                callback_data="series"
            )
        ]
    ]


    await update.message.reply_text(
        f"📄 Subtitle diterima\n\n"
        f"Nama fail:\n{document.file_name}\n\n"
        "Pilih jenis:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


application.add_handler(
    CommandHandler("start", start)
)


application.add_handler(
    MessageHandler(
        filters.Document.ALL,
        receive_srt
    )
)
