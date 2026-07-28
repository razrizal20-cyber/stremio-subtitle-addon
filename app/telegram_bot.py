from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

from .config import BOT_TOKEN

application = Application.builder().token(BOT_TOKEN).build()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    await update.message.reply_text(
        "✅ Bot aktif.\n\n"
        "Hantar fail subtitle .srt kepada saya."
    )


async def receive_srt(update: Update, context: ContextTypes.DEFAULT_TYPE):

    document = update.message.document

    if not document:
        return

    filename = document.file_name

    if not filename.lower().endswith(".srt"):
        await update.message.reply_text(
            "❌ Sila hantar fail .srt sahaja."
        )
        return

    context.user_data.clear()
    context.user_data["filename"] = filename

    keyboard = [
        [
            InlineKeyboardButton("🎬 Movie", callback_data="movie"),
            InlineKeyboardButton("📺 Series", callback_data="series")
        ]
    ]

    await update.message.reply_text(
        f"📄 Subtitle diterima\n\n"
        f"{filename}\n\n"
        "Pilih jenis:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    if query.data == "movie":

        context.user_data["type"] = "movie"
        context.user_data["step"] = "movie_imdb"

        await query.message.reply_text(
            "🎬 Masukkan IMDb ID Movie.\n\nContoh:\ntt4154796"
        )

    elif query.data == "series":

        context.user_data["type"] = "series"
        context.user_data["step"] = "series_imdb"

        await query.message.reply_text(
            "📺 Masukkan IMDb ID Series.\n\nContoh:\ntt0103584"
        )


async def text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    step = context.user_data.get("step")

    if step == "series_imdb":

        context.user_data["imdb"] = update.message.text.strip()
        context.user_data["step"] = "series_season"

        await update.message.reply_text(
            "📀 Season?"
        )
        return

    if step == "series_season":

        context.user_data["season"] = update.message.text.strip()
        context.user_data["step"] = "series_episode"

        await update.message.reply_text(
            "🎬 Episode?"
        )
        return

    if step == "series_episode":

        context.user_data["episode"] = update.message.text.strip()
        context.user_data["step"] = None

        await update.message.reply_text(
            f"""✅ Maklumat diterima

File:
{context.user_data['filename']}

IMDb:
{context.user_data['imdb']}

Season:
{context.user_data['season']}

Episode:
{context.user_data['episode']}

(Langkah seterusnya kita akan tambah butang ✅ Ya untuk publish.)
"""
        )
        return

    if step == "movie_imdb":

        context.user_data["imdb"] = update.message.text.strip()
        context.user_data["step"] = None

        await update.message.reply_text(
            f"""✅ Maklumat diterima

File:
{context.user_data['filename']}

IMDb:
{context.user_data['imdb']}

(Langkah seterusnya kita akan semak IMDb dan publish.)
"""
        )


application.add_handler(CommandHandler("start", start))

application.add_handler(
    MessageHandler(filters.Document.ALL, receive_srt)
)

application.add_handler(
    CallbackQueryHandler(button_click)
)

application.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, text_message)
)
