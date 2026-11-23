"""Deals endpoint — ranked list of best current promotions from the DB."""
from typing import Literal, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.repositories.product_repository import ProductRepository
from app.services.deal_analyzer import DealAnalyzer, DealClassification
from app.services.product_relevance import (
    is_product_in_deal_category,
    is_relevant_product,
)
from app.schemas.schemas import DealOut

router = APIRouter(prefix="/deals", tags=["deals"])


@router.get("", response_model=list[DealOut])
async def list_deals(
    category_id: Optional[UUID] = Query(None, description="Filter by category UUID"),
    category: Optional[Literal["pc", "peripherals"]] = Query(
        None, description="Filter by product category"
    ),
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """
    Return the top deals ranked by the DealAnalyzer score engine.
    Fetches active offers from our database, runs analysis, and returns
    the best ones sorted by deal quality.
    """
    repo = ProductRepository(db)
    analyzer = DealAnalyzer()

    offers = await repo.get_active_offers(limit=None)
    offers = [
        offer for offer in offers
        if (
            offer.product
            and is_relevant_product(offer.product.name)
            and (category_id is None or offer.product.category_id == category_id)
            and (
                category is None
                or is_product_in_deal_category(offer.product.name, category)
            )
        )
    ][:limit * 4]

    scored: list[tuple[int, dict, object]] = []
    for offer in offers:
        history = await repo.get_price_history(offer.id, limit=30)
        analysis = analyzer.analyze(offer, history)

        # Compute a simple numeric score for sorting:
        # PRICE_BELOW_HISTORY=4, PRICE_DROP=3, POTENTIAL_DEAL=2, REGULAR=1
        raw_classification = analysis.get("deal_classification", "regular_price")
        classification = (
            raw_classification.value
            if isinstance(raw_classification, DealClassification)
            else str(raw_classification)
        )
        weight = {
            "price_below_history": 4,
            "price_drop_detected": 3,
            "potential_deal": 2,
            "regular_price": 1,
            "insufficient_history": 0,
            "outdated_data": -1,
        }.get(classification, 0)

        scored.append((weight, analysis, offer))

    scored.sort(key=lambda t: t[0], reverse=True)

    result = []
    for _weight, analysis, offer in scored[:limit]:
        result.append(
            DealOut(
                id=offer.id,
                product_id=offer.product_id,
                source=offer.source,
                external_id=offer.external_id,
                product_url=offer.product_url,
                current_price=offer.current_price,
                original_price=offer.original_price,
                currency=offer.currency,
                availability_status=offer.availability_status,
                condition=offer.condition,
                free_shipping=offer.free_shipping,
                seller_name=offer.seller_name,
                seller_reputation=offer.seller_reputation,
                last_checked_at=offer.last_checked_at,
                discount_percent=analysis.get("discount_percent"),
                deal_classification=classification,
                history_points=analysis.get("history_points", 0),
                min_price_observed=analysis.get("min_price_observed"),
                price_trend=analysis.get("price_trend"),
                product=offer.product,
            )
        )
    return result
