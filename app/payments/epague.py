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
        "Accept": "application/json",
    }

    print("=== EPAGUE: INICIANDO CREATE PIX ===", flush=True)
    print(
        f"=== EPAGUE: amount={amount} external_id={external_id} ===",
        flush=True,
    )
    print(
        f"=== EPAGUE: webhook_url={settings.epague_webhook_url} ===",
        flush=True,
    )
    print(
        f"=== EPAGUE: shop_id={'CONFIGURADO' if settings.epague_shop_id else 'NAO CONFIGURADO'} ===",
        flush=True,
    )

    try:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(
                connect=10.0,
                read=30.0,
                write=10.0,
                pool=10.0,
            )
        ) as client:
            response = await client.post(
                f"{EPAGUE_BASE_URL}/api/pix/create",
                headers=headers,
                json=payload,
            )

    except httpx.TimeoutException as exc:
        print(
            f"=== EPAGUE: TIMEOUT === {exc!r}",
            flush=True,
        )
        raise RuntimeError(
            "A ePague demorou demais para responder."
        ) from exc

    except httpx.RequestError as exc:
        print(
            f"=== EPAGUE: ERRO DE CONEXAO === {exc!r}",
            flush=True,
        )
        raise RuntimeError(
            f"Não foi possível conectar à ePague: {exc}"
        ) from exc

    print(
        f"=== EPAGUE: STATUS HTTP {response.status_code} ===",
        flush=True,
    )

    print(
        f"=== EPAGUE: CONTENT-TYPE {response.headers.get('content-type')} ===",
        flush=True,
    )

    print(
        f"=== EPAGUE: SERVER {response.headers.get('server')} ===",
        flush=True,
    )

    if response.is_error:
        body = response.text[:5000]

        print(
            f"=== EPAGUE: RESPOSTA DE ERRO ===\n{body}",
            flush=True,
        )

        raise RuntimeError(
            f"ePague HTTP {response.status_code}: {body}"
        )

    try:
        data = response.json()
    except ValueError as exc:
        raise RuntimeError(
            f"ePague retornou resposta que não é JSON: "
            f"{response.text[:2000]}"
        ) from exc

    print(
        f"=== EPAGUE: JSON RECEBIDO === {data}",
        flush=True,
    )

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