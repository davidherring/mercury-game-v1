from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from collections.abc import AsyncGenerator
from .config import get_settings

settings = get_settings()

_engine: AsyncEngine | None = None
_session_maker: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    """Lazy initialization - engine created on first access."""
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            settings.database_url, 
            future=True, 
            echo=False
        )
    return _engine


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    global _session_maker
    if _session_maker is None:
        _session_maker = async_sessionmaker(
            get_engine(),
            expire_on_commit=False,
            autoflush=False
        )
    async with _session_maker() as session:
        yield session


__all__ = ["get_engine", "get_session", "AsyncSession"]