from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    pass


def _make_engine():
    return create_async_engine(
        settings.DATABASE_URL,
        echo=settings.APP_DEBUG,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )


# Lazy engine — not created at import time
_engine = None
_session_factory = None


def get_engine():
    global _engine, _session_factory
    if _engine is None:
        _engine = _make_engine()
        _session_factory = async_sessionmaker(
            bind=_engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _engine, _session_factory


def get_session_factory():
    """Return the session factory (used by background tasks)."""
    _, factory = get_engine()
    return factory


async def init_db():
    """Create all tables if they don't exist yet (dev / test convenience)."""
    engine, _ = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    _, factory = get_engine()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
