
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

if settings.database_url is None:
    raise RuntimeError(
        "DATABASE_URL is required to start the database layer."
    )

engine = create_async_engine(
    settings.database_url.get_secret_value(),
    pool_pre_ping=True,
    echo=False,
)

AsyncSessionFactory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionFactory() as session:
        yield session
