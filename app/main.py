from contextlib import asynccontextmanager

from fastapi import FastAPI

from .telegram_bot import application


@asynccontextmanager
async def lifespan(app: FastAPI):
    await application.initialize()
    await application.start()
    await application.updater.start_polling()

    yield

    await application.updater.stop()
    await application.stop()
    await application.shutdown()


app = FastAPI(
    title="Rizal Subtitle Addon",
    lifespan=lifespan
)


@app.get("/")
async def home():
    return {
        "status": "online"
    }
