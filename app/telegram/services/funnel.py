from aiogram import Bot
from sqlalchemy import select

from app.database.database import AsyncSessionLocal
from app.database.models import Media


async def get_funnel_media(stage: str) -> list[Media]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Media)
            .where(
                Media.stage == stage,
                Media.active.is_(True),
            )
            .order_by(Media.sort_order.asc())
        )

        return list(result.scalars().all())


async def send_funnel_media(
    bot: Bot,
    chat_id: int,
    stage: str,
) -> None:
    media_items = await get_funnel_media(stage)

    for media in media_items:
        if media.media_type == "photo":
            await bot.send_photo(
                chat_id=chat_id,
                photo=media.file_id,
            )

        elif media.media_type == "video":
            await bot.send_video(
                chat_id=chat_id,
                video=media.file_id,
            )