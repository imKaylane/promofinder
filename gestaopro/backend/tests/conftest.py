"""
GestãoPro — Fixtures de testes
Portado de: backend/app/tests/conftest.py (TechDeals AI)
Mudança: pytest-asyncio + aiosqlite → pytest-flask + SQLite síncrono

Estratégia: patch get_db no db_module ANTES de criar o app Flask,
garantindo que os blueprints capturem a função substituída.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Patch get_db BEFORE creating the Flask app so blueprints import the patched version.
import app.models.database as db_module
from app.models.database import Base

TEST_DB_URL = "sqlite:///:memory:"

_engine = create_engine(TEST_DB_URL, echo=False)
Base.metadata.create_all(bind=_engine)
_Session = sessionmaker(bind=_engine, autocommit=False, autoflush=False)


def _test_get_db():
    """SQLite session generator — replaces MySQL get_db for tests."""
    session = _Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# Patch at module level so blueprints always see the test DB
db_module.get_db = _test_get_db


@pytest.fixture(scope="session")
def app():
    from app import create_app
    flask_app = create_app()
    flask_app.config["TESTING"] = True
    flask_app.config["DEBUG"] = False
    return flask_app


@pytest.fixture(autouse=True)
def rollback_between_tests():
    """Rollback all data between tests for isolation."""
    yield
    # Reset tables between tests by rolling back open transactions
    with _engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())


@pytest.fixture
def client(app):
    return app.test_client()
