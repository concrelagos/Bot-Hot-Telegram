from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from sqlalchemy import select

from app.config import settings
from app.database.database import AsyncSessionLocal
from app.database.models import Media


router = Router()


class MediaRegistration(StatesGroup):
    waiting_name = State()
    waiting_media = State()
    waiting_position = State()


def is_admin(message: Message) -> bool:
    return (
        message.from_user is not None
        and message.from_user.id == settings.admin_telegram_id
    )


@router.message(F.text == "/cadastrar")
async def start_registration(message: Message, state: FSMContext) -> None:
    if not is_admin(message):
        return

    await state.clear()
    await state.set_state(MediaRegistration.waiting_name)

    await message.answer(
        "🛠️ CADASTRO DE MÍDIA\n\n"
        "Digite um nome para esta mídia.\n\n"
        "Exemplos:\n"
        "foto_1\n"
        "foto_2\n"
        "video_1"
    )


@router.message(MediaRegistration.waiting_name, F.text)
async def receive_name(message: Message, state: FSMContext) -> None:
    if not is_admin(message):
        await state.clear()
        return

    name = message.text.strip().lower()

    if not name or len(name) > 100:
        await message.answer(
            "❌ Nome inválido.\n\n"
            "Use um nome com até 100 caracteres."
        )
        return

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Media).where(Media.name == name)
        )
        existing = result.scalar_one_or_none()

    if existing is not None:
        await message.answer(
            f"❌ Já existe uma mídia chamada `{name}`.\n\n"
            "Escolha outro nome."
        )
        return

    await state.update_data(name=name)
    await state.set_state(MediaRegistration.waiting_media)

    await message.answer(
        f"✅ Nome definido: `{name}`\n\n"
        "Agora envie a FOTO ou o VÍDEO."
    )


@router.message(MediaRegistration.waiting_media, F.photo)
async def receive_photo(
    message: Message,
    state: FSMContext,
) -> None:
    if not is_admin(message):
        await state.clear()
        return

    photo = message.photo[-1]

    await state.update_data(
        media_type="photo",
        file_id=photo.file_id,
    )

    await state.set_state(MediaRegistration.waiting_position)

    await message.answer(
        "📸 Foto recebida!\n\n"
        "Agora informe a posição numérica.\n\n"
        "Exemplo: `1`"
    )


@router.message(MediaRegistration.waiting_media, F.video)
async def receive_video(
    message: Message,
    state: FSMContext,
) -> None:
    if not is_admin(message):
        await state.clear()
        return

    if message.video is None:
        return

    await state.update_data(
        media_type="video",
        file_id=message.video.file_id,
    )

    await state.set_state(MediaRegistration.waiting_position)

    await message.answer(
        "🎥 Vídeo recebido!\n\n"
        "Agora informe a posição numérica.\n\n"
        "Exemplo: `1`"
    )


@router.message(MediaRegistration.waiting_media)
async def invalid_media(message: Message) -> None:
    if not is_admin(message):
        return

    await message.answer(
        "❌ Envie uma FOTO ou um VÍDEO."
    )


@router.message(MediaRegistration.waiting_position, F.text)
async def receive_position(
    message: Message,
    state: FSMContext,
) -> None:
    if not is_admin(message):
        await state.clear()
        return

    try:
        position = int(message.text.strip())
    except ValueError:
        await message.answer(
            "❌ A posição precisa ser um número inteiro.\n\n"
            "Exemplo: `1`"
        )
        return

    if position < 1:
        await message.answer(
            "❌ A posição deve ser maior ou igual a 1."
        )
        return

    data = await state.get_data()

    async with AsyncSessionLocal() as session:
        media = Media(
            name=data["name"],
            media_type=data["media_type"],
            file_id=data["file_id"],
            position=position,
            active=True,
        )

        session.add(media)
        await session.commit()

    await state.clear()

    await message.answer(
        "✅ MÍDIA CADASTRADA COM SUCESSO!\n\n"
        f"Nome: {data['name']}\n"
        f"Tipo: {data['media_type']}\n"
        f"Posição: {position}"
    )