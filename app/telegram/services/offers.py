from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy import select

from app.database.database import AsyncSessionLocal
from app.database.models import Offer


async def get_active_offers() -> list[Offer]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Offer)
            .where(Offer.active.is_(True))
            .order_by(Offer.sort_order.asc())
        )
        return list(result.scalars().all())


async def build_offers_keyboard() -> InlineKeyboardMarkup:
    offers = await get_active_offers()

    buttons = []

    emojis = ["💎", "🔥", "👑"]

    for index, offer in enumerate(offers):
        emoji = emojis[index] if index < len(emojis) else "💠"

        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"{emoji} {offer.name} — R$ {offer.price.replace('.', ',')}",
                    callback_data=f"offer:{offer.id}",
                )
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)