"""
Search endpoints — live Mercado Livre search and deterministic offer analysis.
No AI.  Deal scores are computed purely from price history and seller metadata.
"""
import logging
import re
from decimal import Decimal
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.integrations.mercadolivre import MercadoLivreService
from app.repositories.product_repository import ProductRepository
from app.schemas.schemas import (
    SearchRequest, SearchResponse, SearchResultItem,
    OfferWithDealOut,
)
from app.services.deal_analyzer import DealAnalyzer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/search", tags=["search"])

# Minimum seller discount (%) for a live result to be flagged as a deal
_MIN_DEAL_PCT = 5.0


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _extract_max_price_from_query(query: str) -> Optional[float]:
    """
    Parse a price ceiling written in the query string, e.g. "até R$1500"
    or "menos de 2.000,00".  Returns the float value or None.
    """
    match = re.search(r"[Rr]\$\s*([\d.,]+)", query)
    if match:
        raw = match.group(1).replace(".", "").replace(",", ".")
        try:
            return float(raw)
        except ValueError:
            pass
    return None


def _compute_discount(price: Optional[float], original_price: Optional[float]) -> Optional[float]:
    """
    Return the percentage discount between *original_price* and *price*,
    or None when the values are absent or the discount is not positive.
    """
    if not price or not original_price or original_price <= price or original_price <= 0:
        return None
    return round((original_price - price) / original_price * 100, 2)


def _normalise_item(raw: dict) -> SearchResultItem:
    """Convert a raw Mercado Livre result dict to a SearchResultItem."""
    shipping = raw.get("shipping") or {}
    seller = raw.get("seller") or {}
    seller_rep = (seller.get("seller_reputation") or {}).get("level_id")

    brand: Optional[str] = None
    model: Optional[str] = None
    for attr in raw.get("attributes") or []:
        aid = attr.get("id", "")
        val = attr.get("value_name")
        if aid == "BRAND" and val:
            brand = val
        elif aid in ("MODEL", "ALPHANUMERIC_MODEL") and val:
            model = val

    price = raw.get("price") or 0.0
    original_price = raw.get("original_price")
    discount_pct = _compute_discount(price, original_price)
    is_deal = discount_pct is not None and discount_pct >= _MIN_DEAL_PCT

    return SearchResultItem(
        external_id=raw.get("id", ""),
        title=raw.get("title", ""),
        brand=brand,
        model=model,
        price=price,
        original_price=original_price,
        currency=raw.get("currency_id", "BRL"),
        url=raw.get("permalink", ""),
        thumbnail=raw.get("thumbnail"),
        condition=raw.get("condition", "new"),
        free_shipping=shipping.get("free_shipping", False),
        seller_name=seller.get("nickname"),
        seller_reputation=seller_rep,
        discount_percent=discount_pct,
        is_deal=is_deal,
    )


# ─── Endpoints ───────────────────────────────────────────────────────────────

@router.post("", response_model=SearchResponse, summary="Live product search")
async def search_products(
    payload: SearchRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Execute a live search against the Mercado Livre API and return normalised
    results enriched with deterministic discount metadata.

    The results are persisted to the local database in a best-effort manner so
    that the price-history and deal-ranking engine has data to work with.
    """
    # If no explicit max_price, try to parse one from the query string.
    max_price = payload.max_price
    if max_price is None:
        max_price = _extract_max_price_from_query(payload.query)

    async with MercadoLivreService() as ml:
        raw_response = await ml.search(
            query=payload.query,
            category=payload.category,
            min_price=payload.min_price,
            max_price=max_price,
            condition=payload.condition,
            sort=payload.sort if payload.sort != "relevance" else None,
            offset=(payload.page - 1) * payload.limit,
            limit=payload.limit,
        )

    raw_items = raw_response.get("results", [])
    paging = raw_response.get("paging", {})
    total = paging.get("total", len(raw_items))

    # Persist results to the local DB (best-effort — errors are non-fatal).
    repo = ProductRepository(db)
    for raw in raw_items:
        offer_obj = MercadoLivreService.normalise_result(raw)
        try:
            await repo.upsert_from_meli(offer_obj)
        except Exception as exc:  # noqa: BLE001
            logger.debug("upsert_from_meli skipped for %s: %s", offer_obj.external_id, exc)

    items = [_normalise_item(r) for r in raw_items]

    return SearchResponse(
        query=payload.query,
        total=total,
        page=payload.page,
        limit=payload.limit,
        items=items,
    )


@router.get(
    "/analyze/{offer_id}",
    response_model=OfferWithDealOut,
    summary="Deterministic deal analysis for a stored offer",
)
async def analyze_offer(
    offer_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve a stored offer by ID and run the deterministic DealAnalyzer
    against its price history.  Returns the offer enriched with classification
    fields (deal_classification, discount_percent, price_trend, etc.).

    No AI is involved — all scoring is based on historical price data stored
    locally and the seller-stated original price.
    """
    from sqlalchemy import select
    from app.models.models import Offer

    result = await db.execute(select(Offer).where(Offer.id == offer_id))
    offer = result.scalar_one_or_none()
    if not offer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Offer not found.")

    repo = ProductRepository(db)
    history = await repo.get_price_history(offer.id, limit=90)

    analyzer = DealAnalyzer()
    analysis = analyzer.analyze(offer, history)

    return OfferWithDealOut(
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
        deal_classification=str(analysis.get("deal_classification", "regular_price")),
        history_points=analysis.get("history_points", 0),
        min_price_observed=analysis.get("min_price_observed"),
        price_trend=analysis.get("price_trend"),
    )
