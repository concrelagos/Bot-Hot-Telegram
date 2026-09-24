import httpx

from app.config import settings


EPAGUE_BASE_URL = "https://epague.net"


async def create_pix(
    *,
    amount: float,
    description: str,
    external_id: str,
) -> dict:
    payload = {
        "amount": amount,
        "description": description,
        "external_id": external_id,
        "webhook_url": settings.epague_webhook_url,
        "expiration": 1800,
    }

    if settings.epague_shop_id:
        payload["shop_id"] = settings.epague_shop_id

    headers = {
        "x-api-key": settings.epague_api_key,
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{EPAGUE_BASE_URL}/api/pix/create",
            headers=headers,
            json=payload,
        )

    if response.is_error:
        raise RuntimeError(
            f"ePague HTTP {response.status_code}: {response.text}"
        )

    data = response.json()

    if not data.get("success"):
        raise RuntimeError(
            "A ePague não confirmou a criação do PIX."
        )

    transaction = data.get("transaction")

    if not transaction:
        raise RuntimeError(
            "Resposta da ePague sem transaction."
        )

    return transaction