import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.tasks.tasks import _collect_meli_products_async


@pytest.mark.asyncio
async def test_collection_searches_configured_terms_and_persists_offers():
    session = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)

    offer = object()
    meli = AsyncMock()
    meli.__aenter__ = AsyncMock(return_value=meli)
    meli.__aexit__ = AsyncMock(return_value=None)
    meli.search.side_effect = [
        {"results": [{"id": "MLB1"}]},
        {"results": [{"id": "MLB2"}]},
    ]
    meli.normalise_results = MagicMock(return_value=[offer])

    repository = MagicMock()
    repository.upsert_from_meli = AsyncMock()

    with patch("app.core.config.settings.MELI_COLLECTION_QUERIES", "notebook, ssd"), \
            patch("app.core.database.get_session_factory", return_value=lambda: session), \
            patch("app.integrations.mercadolivre.MercadoLivreService", return_value=meli), \
            patch("app.repositories.product_repository.ProductRepository", return_value=repository):
        await _collect_meli_products_async()

    assert [call.args[0] for call in meli.search.await_args_list] == ["notebook", "ssd"]
    assert all(call.kwargs["limit"] == 24 for call in meli.search.await_args_list)
    assert repository.upsert_from_meli.await_count == 2
    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_collection_can_process_one_selected_focus_query():
    session = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)

    meli = AsyncMock()
    meli.__aenter__ = AsyncMock(return_value=meli)
    meli.__aexit__ = AsyncMock(return_value=None)
    meli.search.return_value = {"results": []}
    meli.normalise_results = MagicMock(return_value=[])

    repository = MagicMock()
    repository.upsert_from_meli = AsyncMock()

    with patch("app.core.config.settings.MELI_COLLECTION_QUERIES", "pc parts,peripherals,music"), \
            patch("app.core.database.get_session_factory", return_value=lambda: session), \
            patch("app.integrations.mercadolivre.MercadoLivreService", return_value=meli), \
            patch("app.repositories.product_repository.ProductRepository", return_value=repository):
        await _collect_meli_products_async(query_index=2)

    meli.search.assert_awaited_once_with("music", limit=24)
    session.commit.assert_awaited_once()


def test_collection_task_rotates_after_successful_collection():
    from app.tasks import tasks

    redis_client = MagicMock()
    redis_client.get.return_value = "1"

    with patch("redis.Redis.from_url", return_value=redis_client), \
            patch("app.tasks.tasks._get_meli_collection_queries", return_value=["pc", "peripherals", "music"]), \
            patch("app.tasks.tasks._collect_meli_products_async", new_callable=AsyncMock) as collect_async, \
            patch("app.tasks.tasks._run_async_task", side_effect=asyncio.run) as run_async:
        tasks.collect_meli_products.run()

    collect_async.assert_awaited_once_with(query_index=1)
    run_async.assert_called_once()
    redis_client.set.assert_called_once_with("meli:collection:query-index", 2)
    redis_client.close.assert_called_once()


def test_async_task_disposes_database_engine_when_coroutine_fails():
    from app.tasks.tasks import _run_async_task

    dispose_engine = AsyncMock()

    async def fail():
        raise RuntimeError("collection failed")

    with patch("app.core.database.dispose_engine", dispose_engine):
        with pytest.raises(RuntimeError, match="collection failed"):
            _run_async_task(fail())

    dispose_engine.assert_awaited_once()
