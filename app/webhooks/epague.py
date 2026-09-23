import hashlib
import hmac
import time
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

from fastapi import APIRouter, Request
from sqlalchemy import select

from app.config import settings
from app.database.database import AsyncSessionLocal
from app.database.models import Order


router = APIRouter()


def verify_signature(raw_body: bytes, signature: str) -> bool:
    if not settings.epague_webhook_secret:
        return False

    try:
        parts = dict(
            item.split("=", 1)
            for item in signature.split(",")
            if "=" in item
        )

        timestamp = parts.get("t")
        received_signature = parts.get("v1")

        if not timestamp or not received_signature:
            return False

        timestamp_int = int(timestamp)

        if abs(time.time() - timestamp_int) > 300:
            return False

        signed_payload = f"{timestamp}.{raw_body.decode('utf-8')}".encode()

        expected_signature = hmac.new(
            settings.epague_webhook_secret.encode(),
            signed_payload,
            hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(
            expected_signature,
            received_signature,
        )

    except (ValueError, UnicodeDecodeError):
        return False


@router.post("/webhooks/epague")
async def epague_webhook(request: Request) -> dict:
    raw_body = await request.body()

    signature = request.headers.get("X-Webhook-Signature")

    if settings.epague_webhook_secret:
        if not signature:
            return {"status": "ignored", "reason": "missing_signature"}

        if not verify_signature(raw_body, signature):
            return {"status": "ignored", "reason": "invalid_signature"}

    event = request.headers.get("X-Webhook-Event")

    if event != "payment.confirmed":
        return {"status": "ignored", "reason": "unsupported_event"}

    try:
        payload = await request.json()
    except Exception:
        return {"status": "ignored", "reason": "invalid_json"}

    external_id = payload.get("external_id")
    transaction_id = payload.get("transaction_id")
    txid = payload.get("txid")
    status = payload.get("status")
    amount = payload.get("amount")
    paid_at = payload.get("paid_at")

    if not external_id:
        return {"status": "ignored", "reason": "missing_external_id"}

    if status != "paid":
        return {"status": "ignored", "reason": "payment_not_paid"}

    if amount is None:
        return {"status": "ignored", "reason": "missing_amount"}

    try:
        webhook_amount = Decimal(str(amount))
    except InvalidOperation:
        return {"status": "ignored", "reason": "invalid_amount"}

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Order).where(Order.external_id == external_id)
        )
        order = result.scalar_one_or_none()

        if order is None:
            return {"status": "ignored", "reason": "order_not_found"}

        # Idempotência:
        # se o mesmo webhook chegar novamente, não processamos de novo.
        if order.status == "PAID":
            return {
                "status": "ok",
                "message": "order_already_paid",
            }

        try:
            order_amount = Decimal(str(order.amount))
        except InvalidOperation:
            return {"status": "ignored", "reason": "invalid_order_amount"}

        # Segurança: o valor pago precisa ser exatamente o valor do pedido.
        if webhook_amount != order_amount:
            return {
                "status": "ignored",
                "reason": "amount_mismatch",
            }

        order.status = "PAID"
        order.payment_id = transaction_id
        order.payment_txid = txid

        if paid_at:
            try:
                order.paid_at = datetime.fromisoformat(
                    paid_at.replace("Z", "+00:00")
                )
            except ValueError:
                order.paid_at = datetime.now(timezone.utc)
        else:
            order.paid_at = datetime.now(timezone.utc)

        await session.commit()

    return {
        "status": "ok",
        "message": "payment_confirmed",
    }