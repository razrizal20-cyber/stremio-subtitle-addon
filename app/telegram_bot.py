import os
import sqlite3
from datetime import datetime

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


# ==========================
# STORAGE CONFIG
# ==========================

UPLOAD_FOLDER = "uploads"

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


# ==========================
# DATABASE
# ==========================

def init_database():

    conn = sqlite3.connect(
        "subtitles.db"
    )

    cursor = conn.cursor()


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subtitles (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        filename TEXT,

        path TEXT,

        type TEXT,

        imdb TEXT,

        season TEXT,

        episode TEXT,

        created_at TEXT

    )
    """)


    conn.commit()
    conn.close()



init_database()



# ==========================
# SAVE SUBTITLE
# ==========================

async def save_subtitle(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    document = update.message.document


    file = await document.get_file()


    filename = context.user_data["filename"]


    save_path = os.path.join(
        UPLOAD_FOLDER,
        filename
    )


    # Download dari Telegram
    await file.download_to_drive(
        save_path
    )


    # Simpan database
    conn = sqlite3.connect(
        "subtitles.db"
    )

    cursor = conn.cursor()


    cursor.execute(
        """
        INSERT INTO subtitles
        (
            filename,
            path,
            type,
            imdb,
            season,
            episode,
            created_at
        )

        VALUES (?,?,?,?,?,?,?)
        """,

        (

            filename,

            save_path,

            context.user_data.get("type"),

            context.user_data.get("imdb"),

            context.user_data.get("season"),

            context.user_data.get("episode"),

            datetime.now().isoformat()

        )
    )


    conn.commit()
    conn.close()


    return save_path





# ==========================
# START
# ==========================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    context.user_data.clear()


    await update.message.reply_text(
        "✅ Bot aktif.\n\n"
        "Hantar fail subtitle .srt kepada saya."
    )





# ==========================
# RECEIVE SRT
# ==========================

async def receive_srt(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

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
        f"{filename}\n\n"
        "Pilih jenis:",

        reply_markup=InlineKeyboardMarkup(
            keyboard
        )

    )





# ==========================
# BUTTON
# ==========================

async def button_click(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()



    if query.data == "movie":


        context.user_data["type"] = "movie"

        context.user_data["step"] = "movie_imdb"



        await query.message.reply_text(

            "🎬 Masukkan IMDb ID Movie.\n\n"
            "Contoh:\n"
            "tt4154796"

        )



    elif query.data == "series":


        context.user_data["type"] = "series"

        context.user_data["step"] = "series_imdb"



        await query.message.reply_text(

            "📺 Masukkan IMDb ID Series.\n\n"
            "Contoh:\n"
            "tt0103584"

        )






# ==========================
# TEXT FLOW
# ==========================

async def text_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    step = context.user_data.get(
        "step"
    )



    # SERIES IMDb

    if step == "series_imdb":


        context.user_data["imdb"] = (
            update.message.text.strip()
        )


        context.user_data["step"] = (
            "series_season"
        )


        await update.message.reply_text(
            "📀 Season?"
        )

        return





    # SERIES SEASON

    if step == "series_season":


        context.user_data["season"] = (
            update.message.text.strip()
        )


        context.user_data["step"] = (
            "series_episode"
        )


        await update.message.reply_text(
            "🎬 Episode?"
        )

        return





    # SERIES EPISODE

    if step == "series_episode":


        context.user_data["episode"] = (
            update.message.text.strip()
        )


        path = await save_subtitle(
            update,
            context
        )



        await update.message.reply_text(

            f"""✅ Subtitle berjaya disimpan!


📄 File:
{context.user_data['filename']}


🎬 IMDb:
{context.user_data['imdb']}


📀 Season:
{context.user_data['season']}


🎞 Episode:
{context.user_data['episode']}


💾 Lokasi:
{path}
"""

        )



        context.user_data.clear()


        return





    # MOVIE IMDb

    if step == "movie_imdb":


        context.user_data["imdb"] = (
            update.message.text.strip()
        )


        path = await save_subtitle(
            update,
            context
        )



        await update.message.reply_text(

            f"""✅ Subtitle berjaya disimpan!


📄 File:
{context.user_data['filename']}


🎬 IMDb:
{context.user_data['imdb']}


💾 Lokasi:
{path}
"""

        )



        context.user_data.clear()


        return






# ==========================
# HANDLERS
# ==========================

application.add_handler(
    CommandHandler(
        "start",
        start
    )
)


application.add_handler(
    MessageHandler(
        filters.Document.ALL,
        receive_srt
    )
)


application.add_handler(
    CallbackQueryHandler(
        button_click
    )
)


application.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        text_message
    )
)


# ==========================
# RUN BOT
# ==========================

async def run_bot():

    await application.bot.delete_webhook(
        drop_pending_updates=True
    )

    await application.run_polling()
