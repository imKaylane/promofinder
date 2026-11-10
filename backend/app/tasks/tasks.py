"""
Celery background tasks — price alert checks and deal cache refresh.
Uses only the Mercado Livre API and the deterministic DealAnalyzer.
No AI dependencies.
"""
import asyncio
import logging

from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.tasks.check_price_alerts", bind=True, max_retries=3)
def check_price_alerts(self):
    """
    For every active price alert, compare the cheapest current offer against
    the user's target price.  When reached, deactivate the alert and create
    an in-app notification.
    """
    try:
        asyncio.run(_check_price_alerts_async())
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(name="app.tasks.tasks.refresh_deals_cache", bind=True, max_retries=3)
def refresh_deals_cache(self):
    """
    Score all active offers with the DealAnalyzer and log the best deal found.
    This pre-warms any future caching layer so the /deals endpoint responds
    without a cold-start penalty.
    """
    try:
        asyncio.run(_refresh_deals_cache_async())
    except Exception as exc:
        raise self.retry(exc=exc, countdown=120)


# ---------------------------------------------------------------------------
# Async helpers — Celery workers are synchronous; we bridge with asyncio.run.
# ---------------------------------------------------------------------------

async def _check_price_alerts_async() -> None:
    from sqlalchemy import select

    from app.core.database import get_session_factory
    from app.models.models import Offer, PriceAlert
    from app.repositories.user_repository import UserRepository

    async with get_session_factory()() as session:
        result = await session.execute(
            select(PriceAlert).where(PriceAlert.is_active == True)  # noqa: E712
        )
        alerts = result.scalars().all()
        if not alerts:
            logger.debug("check_price_alerts: no active alerts found")
            return

        for alert in alerts:
            try:
                # Find the cheapest active offer for this product.
                offer_result = await session.execute(
                    select(Offer)
                    .where(
                        Offer.product_id == alert.product_id,
                        Offer.availability_status == "active",
                    )
                    .order_by(Offer.current_price.asc())
                    .limit(1)
                )
                offer = offer_result.scalar_one_or_none()
                if not offer:
                    continue

                current_price = offer.current_price
                if current_price is not None and current_price <= alert.target_price:
                    logger.info(
                        "Alert triggered — user=%s product=%s price=%.2f target=%.2f",
                        alert.user_id,
                        alert.product_id,
                        current_price,
                        alert.target_price,
                    )
                    alert.is_active = False

                    user_repo = UserRepository(session)
                    await user_repo.create_notification(
                        user_id=alert.user_id,
                        ntype="price_alert",
                        title="Alerta de preço atingido!",
                        message=(
                            f"O produto está por R$ {current_price:.2f} "
                            f"(sua meta: R$ {alert.target_price:.2f})"
                        ),
                        related_product_id=alert.product_id,
                    )
            except Exception as exc:  # noqa: BLE001
                logger.warning("Failed to process alert %s: %s", alert.id, exc)

        await session.commit()


async def _refresh_deals_cache_async() -> None:
    from app.core.database import get_session_factory
    from app.repositories.product_repository import ProductRepository
    from app.services.deal_analyzer import DealAnalyzer

    # Score weight map — mirrors the ranking logic in the /deals endpoint.
    SCORE_MAP = {
        "price_below_history": 4,
        "price_drop_detected": 3,
        "potential_deal": 2,
        "regular_price": 1,
        "insufficient_history": 0,
        "outdated_data": -1,
    }

    analyzer = DealAnalyzer()
    best_score = 0
    best_offer_id = None

    async with get_session_factory()() as session:
        repo = ProductRepository(session)
        offers = await repo.get_active_offers(limit=200)

        for offer in offers:
            try:
                history = await repo.get_price_history(offer.id, limit=20)
                analysis = analyzer.analyze(offer, history)
                score = SCORE_MAP.get(str(analysis.get("deal_classification", "")), 0)
                if score > best_score:
                    best_score = score
                    best_offer_id = offer.id
            except Exception as exc:  # noqa: BLE001
                logger.warning("Failed to score offer %s: %s", offer.id, exc)

    logger.info(
        "Deals cache refreshed — best_offer_id=%s score=%d total_offers=%d",
        best_offer_id,
        best_score,
        len(offers),
    )
