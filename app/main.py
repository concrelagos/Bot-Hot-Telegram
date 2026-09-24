from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from app.database.database import init_db
from app.telegram.bot import bot, dp
from app.webhooks.epague import router as epague_router
from app.config import settings


TELEGRAM_WEBHOOK_PATH = "/webhooks/telegram"


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()

    webhook_url = (
        "https://bot-hot-telegram.onrender.com"
        f"{TELEGRAM_WEBHOOK_PATH}"
    )

    await bot.set_webhook(
        url=webhook_url,
        secret_token=settings.telegram_webhook_secret,
        drop_pending_updates=True,
    )

    yield

    await bot.delete_webhook()
    await bot.session.close()


app = FastAPI(
    title="Bot Hot Telegram",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(epague_router)


@app.get("/health")
async def health() -> dict:
    return {
        "status": "ok",
        "service": "telegram-bot",
    }


@app.post(TELEGRAM_WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")

    if settings.telegram_webhook_secret:
        if secret != settings.telegram_webhook_secret:
            return {"status": "ignored"}

    data = await request.json()

    print(
        f"=== UPDATE TELEGRAM RECEBIDO: {data} ===",
        flush=True,
    )

    from aiogram.types import Update

    update = Update.model_validate(
        data,
        context={"bot": bot},
    )

    await dp.feed_update(bot, update)

    return {"status": "ok"}