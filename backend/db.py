from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from .config import get_settings
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession


settings = get_settings()

engine: AsyncEngine = create_async_engine(settings.database_url, future=True, echo=False)
AsyncSessionMaker = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionMaker() as session:
        yield session


__all__ = ["engine", "AsyncSession", "AsyncSessionMaker", "get_session"]
