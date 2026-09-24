from sqlalchemy import select

from app.database.database import AsyncSessionLocal
from app.database.models import Media, Offer


MEDIA_SEED = [
    {
        "name": "foto_1",
        "media_type": "photo",
        "file_id": "AgACAgEAAxkBAANuarLci_A0ouMnYJbouclTgYPXWesAAscMaxssE5hF6J1Ilq3oODEBAAMCAAN4AAM9BA",
        "position": 0,
        "stage": "START",
        "sort_order": 1,
        "active": True,
    },
    {
        "name": "video_1",
        "media_type": "video",
        "file_id": "BAACAgEAAxkBAANOarK0EAmQh6r51khmESGcS-fzRJoAAksJAAIsE5BFGZiA5q7M0EM9BA",
        "position": 0,
        "stage": "START",
        "sort_order": 2,
        "active": True,
    },
    {
        "name": "foto_2",
        "media_type": "photo",
        "file_id": "AgACAgEAAxkBAAN6arLc5Rd2N0prmWY40KHmn_xbiq4AAsgMaxssE5hFoOA12Mf_QgoBAAMCAAN4AAM9BA",
        "position": 0,
        "stage": "FOLLOWUP_5MIN",
        "sort_order": 1,
        "active": True,
    },
    {
        "name": "video_3",
        "media_type": "video",
        "file_id": "BAACAgEAAxkBAANearK24EGC2XQ2DB2Ezn640uMsdWAAAlEJAAIsE5BFx6Ul7RQ8jEw9BA",
        "position": 0,
        "stage": "FOLLOWUP_5MIN",
        "sort_order": 2,
        "active": True,
    },
    {
        "name": "video_4",
        "media_type": "video",
        "file_id": "BAACAgEAAxkBAANmarK3CTXRxjr_GUYaAAHAz9lSGTV_AAJSCQACLBOQRSwNlwypJgGwPQQ",
        "position": 0,
        "stage": "FOLLOWUP_10MIN",
        "sort_order": 1,
        "active": True,
    },
    {
        "name": "video_2",
        "media_type": "video",
        "file_id": "BAACAgEAAxkBAANWarK1rXW_JmA72OttK4RDiYsCFdwAAlAJAAIsE5BFSGqzX2C7MsY9BA",
        "position": 0,
        "stage": "INACTIVE",
        "sort_order": 3,
        "active": False,
    },
    {
        "name": "foto_3",
        "media_type": "photo",
        "file_id": "AgACAgEAAxkBAAMharKaBJFa5ZX_L5dnvDJik1L2AdIAAmkMaxssE5BFp_V756C9300BAAMCAAN4AAM9BA",
        "position": 0,
        "stage": "INACTIVE",
        "sort_order": 1,
        "active": False,
    },
]


OFFERS_SEED = [
    {
        "name": "1 mês de VIP",
        "description": "Acesso VIP por 1 mês",
        "price": "19.90",
        "duration_days": 30,
        "active": True,
        "sort_order": 1,
    },
    {
        "name": "3 meses de VIP",
        "description": "Acesso VIP por 3 meses",
        "price": "50.00",
        "duration_days": 90,
        "active": True,
        "sort_order": 2,
    },
    {
        "name": "3 meses VIP + videochamada",
        "description": "Acesso VIP por 3 meses + videochamada",
        "price": "100.00",
        "duration_days": 90,
        "active": True,
        "sort_order": 3,
    },
]


async def seed_content() -> None:
    inserted_media = 0
    inserted_offers = 0

    async with AsyncSessionLocal() as session:

        # =========================
        # MEDIA
        # =========================
        for data in MEDIA_SEED:
            result = await session.execute(
                select(Media).where(Media.name == data["name"])
            )

            existing = result.scalar_one_or_none()

            if existing is None:
                session.add(Media(**data))
                inserted_media += 1

        # =========================
        # OFFERS
        # =========================
        for data in OFFERS_SEED:
            result = await session.execute(
                select(Offer).where(Offer.name == data["name"])
            )

            existing = result.scalar_one_or_none()

            if existing is None:
                session.add(Offer(**data))
                inserted_offers += 1

        await session.commit()

    print(
        f"=== SEED CONCLUIDO | MEDIA INSERIDA: {inserted_media} | "
        f"OFERTAS INSERIDAS: {inserted_offers} ===",
        flush=True,
    )