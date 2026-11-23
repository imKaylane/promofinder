"""Background tasks — price alert checks, deal cache refresh."""
import asyncio
import logging
from datetime import datetime, timezone

from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


def _run_async_task(coroutine):
    async def run():
        try:
            return await coroutine
        finally:
            from app.core.database import dispose_engine

            await dispose_engine()

    return asyncio.run(run())


@celery_app.task(name="app.tasks.tasks.check_price_alerts", bind=True, max_retries=3)
def check_price_alerts(self):
    """
    Fetch current prices for all active alerts and notify users whose
    target price has been reached.
    """
    try:
        _run_async_task(_check_price_alerts_async())
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(name="app.tasks.tasks.refresh_deals_cache", bind=True, max_retries=3)
def refresh_deals_cache(self):
    """Pre-warm the deals cache so the /deals endpoint responds instantly."""
    try:
        _run_async_task(_refresh_deals_cache_async())
    except Exception as exc:
        raise self.retry(exc=exc, countdown=120)


@celery_app.task(name="app.tasks.tasks.collect_meli_products", bind=True, max_retries=3)
def collect_meli_products(self):
    """Collect one configured Mercado Livre search and rotate through the list."""
    from app.core.config import settings
    from redis import Redis

    try:
        queries = _get_meli_collection_queries()
        if not queries:
            _run_async_task(_collect_meli_products_async())
            return

        redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)
        try:
            cursor_key = "meli:collection:query-index"
            query_index = int(redis_client.get(cursor_key) or 0) % len(queries)
            _run_async_task(_collect_meli_products_async(query_index=query_index))
            redis_client.set(cursor_key, (query_index + 1) % len(queries))
        finally:
            redis_client.close()
    except Exception as exc:
        raise self.retry(exc=exc, countdown=120)


# ---------------------------------------------------------------------------
# Async helpers (Celery workers are sync; we bridge with asyncio.run)
# ---------------------------------------------------------------------------

async def _check_price_alerts_async():
    from app.core.database import get_session_factory
    from app.models.models import PriceAlert, Offer
    from app.integrations.mercadolivre import MercadoLivreService
    from app.repositories.user_repository import UserRepository
    from app.repositories.product_repository import ProductRepository
    from sqlalchemy import select

    async with get_session_factory()() as session:
        result = await session.execute(
            select(PriceAlert).where(PriceAlert.is_active == True)  # noqa: E712
        )
        alerts = result.scalars().all()
        if not alerts:
            return

        async with MercadoLivreService() as ml:
            for alert in alerts:
                try:
                    # Find the best current price for the product via its offers.
                    offer_result = await session.execute(
                        select(Offer)
                        .where(Offer.product_id == alert.product_id)
                        .order_by(Offer.current_price.asc())
                        .limit(1)
                    )
                    offer = offer_result.scalar_one_or_none()
                    if not offer:
                        continue

                    current_price = offer.current_price
                    if current_price and current_price <= alert.target_price:
                        logger.info(
                            "Alert triggered for user=%s product=%s price=%.2f target=%.2f",
                            alert.user_id,
                            alert.product_id,
                            current_price,
                            alert.target_price,
                        )
                        alert.is_active = False

                        # Create a notification.
                        user_repo = UserRepository(session)
                        await user_repo.create_notification(
                            user_id=alert.user_id,
                            ntype="price_alert",
                            title="Alerta de preço atingido!",
                            message=f"O produto está por R$ {current_price:.2f} (sua meta: R$ {alert.target_price:.2f})",
                            related_product_id=alert.product_id,
                        )
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Failed to check alert %s: %s", alert.id, exc)

        await session.commit()


async def _refresh_deals_cache_async():
    from app.core.database import get_session_factory
    from app.repositories.product_repository import ProductRepository
    from app.services.deal_analyzer import DealAnalyzer

    analyzer = DealAnalyzer()

    async with get_session_factory()() as session:
        repo = ProductRepository(session)
        offers = await repo.get_active_offers(limit=200)
        best_score = 0
        best_id = None
        for offer in offers:
            history = await repo.get_price_history(offer.id, limit=20)
            analysis = analyzer.analyze(offer, history)
            classification = str(analysis.get("deal_classification", ""))
            if classification == "price_below_history":
                score = 4
            elif classification == "price_drop_detected":
                score = 3
            elif classification == "potential_deal":
                score = 2
            else:
                score = 0
            if score > best_score:
                best_score = score
                best_id = offer.id

        logger.info("Deals cache refreshed — best_offer_id=%s score=%d", best_id, best_score)


def _get_meli_collection_queries():
    from app.core.config import settings

    return [
        query.strip()
        for query in settings.MELI_COLLECTION_QUERIES.split(",")
        if query.strip()
    ]


async def _collect_meli_products_async(query_index=None):
    from app.core.database import get_session_factory
    from app.integrations.mercadolivre import MercadoLivreService
    from app.repositories.product_repository import ProductRepository

    queries = _get_meli_collection_queries()
    if not queries:
        logger.warning("No Mercado Livre collection queries are configured")
        return
    if query_index is not None:
        queries = [queries[query_index]]

    async with get_session_factory()() as session:
        repo = ProductRepository(session)
        async with MercadoLivreService() as ml:
            for query in queries:
                response = await ml.search(query, limit=24)
                offers = ml.normalise_results(response.get("results", []))
                for offer in offers:
                    await repo.upsert_from_meli(offer)
                logger.info("Collected %d Mercado Livre offers for %r", len(offers), query)
        await session.commit()
