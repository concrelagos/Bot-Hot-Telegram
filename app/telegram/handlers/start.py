from datetime import datetime, timezone

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy import select

from app.database.database import AsyncSessionLocal
from app.database.models import User
from app.telegram.services.funnel import send_funnel_media
from app.telegram.services.funnel_config import get_funnel_message
from app.telegram.services.offers import build_offers_keyboard

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message) -> None:
    if message.from_user is None:
        return

    telegram_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )

        user = result.scalar_one_or_none()
        now = datetime.now(timezone.utc)

        if user is None:
            user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                status="NEW",
                created_at=now,
                last_interaction_at=now,
            )
            session.add(user)
        else:
            user.username = username
            user.first_name = first_name
            user.last_interaction_at = now

        await session.commit()

    await message.answer(
        get_funnel_message(
            stage="START",
            first_name=first_name,
        )
    )

    await send_funnel_media(
        bot=message.bot,
        chat_id=message.chat.id,
        stage="START",
    )

    await message.answer(
        "💎🔥 ESCOLHA SEU PLANO VIP:",
        reply_markup=await build_offers_keyboard(),
    )