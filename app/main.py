import os
import sqlite3

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import FileResponse

from .telegram_bot import application


# ==========================
# LIFESPAN
# ==========================

@asynccontextmanager
async def lifespan(app: FastAPI):

    # buang webhook/polling lama
    await application.bot.delete_webhook(
        drop_pending_updates=True
    )


    # hidupkan telegram bot
    await application.initialize()

    await application.start()

    await application.updater.start_polling(
        drop_pending_updates=True
    )


    print("Telegram Bot Started")


    yield


    # tutup bot dengan betul
    await application.updater.stop()

    await application.stop()

    await application.shutdown()



# ==========================
# FASTAPI
# ==========================

app = FastAPI(
    title="Rizal Subtitle Addon",
    lifespan=lifespan
)



@app.get("/")
async def home():

    return {
        "status": "online",
        "service": "Rizal Subtitle Addon"
    }
