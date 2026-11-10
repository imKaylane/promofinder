"""
GestãoPro — Conexão com MySQL via SQLAlchemy (síncrono)
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import config


class Base(DeclarativeBase):
    pass


_engine = None
_SessionLocal = None


def get_engine():
    global _engine, _SessionLocal
    if _engine is None:
        _engine = create_engine(
            config.SQLALCHEMY_DATABASE_URI,
            echo=config.DEBUG,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
            pool_recycle=3600,
        )
        _SessionLocal = sessionmaker(bind=_engine, autocommit=False, autoflush=False)
    return _engine, _SessionLocal


def get_db():
    """Flask dependency: returns a session, commits on success, rolls back on error."""
    _, SessionLocal = get_engine()
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db():
    """Create all tables if they don't exist."""
    engine, _ = get_engine()
    Base.metadata.create_all(bind=engine)


def check_connection() -> bool:
    """Return True if MySQL is reachable."""
    try:
        engine, _ = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
