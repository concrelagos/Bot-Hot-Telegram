from aiogram import F, Router
from aiogram.types import Message

from app.config import settings


router = Router()


def is_admin(message: Message) -> bool:
    return (
        message.from_user is not None
        and message.from_user.id == settings.admin_telegram_id
    )


@router.message(F.photo)
async def receive_photo(message: Message) -> None:
    if not is_admin(message):
        return

    await message.answer(
        "ℹ️ Para cadastrar uma foto, use /cadastrar."
    )


@router.message(F.video)
async def receive_video(message: Message) -> None:
    if not is_admin(message):
        return

    await message.answer(
        "ℹ️ Para cadastrar um vídeo, use /cadastrar."
    )