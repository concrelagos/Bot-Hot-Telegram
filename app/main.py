from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database.database import init_db
from app.telegram.bot import bot
from app.webhooks.epague import router as epague_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
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