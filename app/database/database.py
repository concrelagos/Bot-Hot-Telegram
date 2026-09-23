from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


class Base(DeclarativeBase):
    pass


database_url = settings.database_url or "sqlite+aiosqlite:///./bot.db"

engine = create_async_engine(
    database_url,
    echo=False,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session():
    async with AsyncSessionLocal() as session:
        yield session


async def init_db() -> None:
    from app.database.models import BaseModel

    async with engine.begin() as connection:
        await connection.run_sync(BaseModel.metadata.create_all)