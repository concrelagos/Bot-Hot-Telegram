from datetime import datetime, timezone

from aiogram import F, Router
from aiogram.types import BufferedInputFile, CallbackQuery
from sqlalchemy import select

from app.database.database import AsyncSessionLocal
from app.database.models import Offer, Order, User
from app.payments.epague import create_pix

import base64
import uuid


router = Router()


@router.callback_query(F.data.startswith("offer:"))
async def select_offer(callback: CallbackQuery) -> None:
    if callback.data is None:
        return

    if callback.from_user is None:
        await callback.answer("Usuário inválido.", show_alert=True)
        return

    try:
        offer_id = int(callback.data.split(":", 1)[1])
    except (ValueError, IndexError):
        await callback.answer("Plano inválido.", show_alert=True)
        return

    async with AsyncSessionLocal() as session:
        # Busca o usuário
        user_result = await session.execute(
            select(User).where(
                User.telegram_id == callback.from_user.id
            )
        )
        user = user_result.scalar_one_or_none()

        if user is None:
            await callback.answer(
                "Usuário não encontrado. Envie /start novamente.",
                show_alert=True,
            )
            return

        # Busca o plano
        offer_result = await session.execute(
            select(Offer).where(
                Offer.id == offer_id,
                Offer.active.is_(True),
            )
        )
        offer = offer_result.scalar_one_or_none()

        if offer is None:
            await callback.answer(
                "Esse plano não está disponível.",
                show_alert=True,
            )
            return

        # Verifica se já existe um PIX pendente para esse plano
        pending_result = await session.execute(
            select(Order)
            .where(
                Order.user_id == user.id,
                Order.offer_id == offer.id,
                Order.status == "PENDING",
            )
            .order_by(Order.id.desc())
        )

        existing_order = pending_result.scalars().first()

        if existing_order is not None:
            await callback.answer("Você já tem um pagamento pendente.")

            if existing_order.pix_copia_cola:
                await callback.message.answer(
                    "💳 Você já possui um pagamento pendente para este plano.\n\n"
                    f"💰 Valor: R$ {offer.price.replace('.', ',')}\n\n"
                    "📋 PIX copia e cola:\n\n"
                    f"`{existing_order.pix_copia_cola}`",
                    parse_mode="Markdown",
                )

            return

        # Gera identificador único do pedido
        external_id = f"pedido-{uuid.uuid4().hex}"

        # Cria pedido local
        order = Order(
            user_id=user.id,
            offer_id=offer.id,
            external_id=external_id,
            amount=offer.price,
            status="PENDING",
            created_at=datetime.now(timezone.utc),
        )

        session.add(order)
        await session.commit()
        await session.refresh(order)
        
        print("=== INICIANDO GERACAO DO PIX ===", flush=True)

        try:
            transaction = await create_pix(
                amount=float(offer.price),
                description=offer.name,
                external_id=external_id,
            )

        except Exception as exc:
            print(f"ERRO AO GERAR PIX: {exc!r}", flush=True)

            order.status = "CANCELLED"
            await session.commit()

            erro = str(exc)

            await callback.answer(
                "Não foi possível gerar o PIX.",
                show_alert=True,
            )

            await callback.message.answer(
                "❌ Erro ao gerar o PIX.\n\n"
                f"🔎 Detalhe técnico:\n{erro[:3500]}"
            )

            return

        # Dados retornados pela ePague
        order.payment_id = transaction.get("id")
        order.payment_txid = transaction.get("txid")
        order.pix_copia_cola = transaction.get("pix_copia_cola")
        order.qr_code_base64 = transaction.get("qr_code_base64")

        expires_at = transaction.get("expires_at")

        if expires_at:
            try:
                order.expires_at = datetime.fromisoformat(
                    expires_at.replace("Z", "+00:00")
                )
            except ValueError:
                order.expires_at = None

        await session.commit()

    await callback.answer("PIX gerado com sucesso! 💚")

    await callback.message.answer(
        "💳 *PAGAMENTO PIX*\n\n"
        f"🔥 {offer.name}\n"
        f"💰 *R$ {offer.price.replace('.', ',')}*\n\n"
        "⏳ Seu PIX foi gerado.\n"
        "Faça o pagamento para liberar seu acesso.\n\n"
        "📋 *PIX copia e cola:*\n\n"
        f"`{transaction.get('pix_copia_cola')}`",
        parse_mode="Markdown",
    )

    # Envia QR Code
    qr_code_base64 = transaction.get("qr_code_base64")

    if qr_code_base64:
        try:
            image_base64 = qr_code_base64

            if "," in image_base64:
                image_base64 = image_base64.split(",", 1)[1]

            image_bytes = base64.b64decode(image_base64)

            qr_file = BufferedInputFile(
                image_bytes,
                filename="pix.png",
            )

            await callback.message.answer_photo(
                photo=qr_file,
                caption="📱 Escaneie o QR Code para pagar."
            )

        except Exception:
            pass