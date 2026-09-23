from aiogram import Bot, Dispatcher
from app.config import settings
from app.telegram.handlers.start import router as start_router
from app.telegram.handlers.admin import router as admin_router
from app.telegram.handlers.media import router as media_router
from app.telegram.handlers.offers import router as offers_router

bot = Bot(token=settings.telegram_bot_token)
dp = Dispatcher()

dp.include_router(start_router)
dp.include_router(admin_router)
dp.include_router(media_router)
dp.include_router(offers_router)