"""AI-powered natural language search and deal analysis endpoints."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.ai.ai_service import AIService
from app.integrations.mercadolivre import MercadoLivreService
from app.repositories.product_repository import ProductRepository
from app.services.deal_analyzer import DealAnalyzer
from app.schemas.schemas import AISearchRequest, AISearchResponse
from app.models.models import User

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/search", response_model=AISearchResponse)
async def ai_search(
    payload: AISearchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Parse a natural language query (e.g. "processador Ryzen 7 até R$1500")
    into structured ML search parameters, execute the live search, and return
    AI-generated insights alongside the results.
    """
    ai = AIService()

    # 1. Let AI extract structured params from natural language.
    structured = await ai.interpret_search(payload.query)

    # 2. Execute live ML search with extracted params.
    async with MercadoLivreService() as ml:
        results = await ml.search(
            query=structured.get("search_term", payload.query),
            min_price=structured.get("min_price"),
            max_price=structured.get("max_price"),
            condition=structured.get("condition"),
            sort=structured.get("sort", "relevance"),
            limit=payload.limit,
            offset=(payload.page - 1) * payload.limit,
        )

    raw_items = results.get("results", [])

    # 3. Persist items to local DB in best-effort fashion.
    repo = ProductRepository(db)
    for raw in raw_items:
        offer_obj = MercadoLivreService.normalise_result(raw)
        try:
            await repo.upsert_from_meli(offer_obj)
        except Exception:
            pass

    # 4. Ask AI to write a recommendation summary.
    products_data = [
        {
            "name": r.get("title"),
            "current_price": r.get("price"),
            "original_price": r.get("original_price"),
            "condition": r.get("condition"),
            "free_shipping": (r.get("shipping") or {}).get("free_shipping"),
        }
        for r in raw_items[:10]
    ]
    ai_result = await ai.recommend(payload.query, products_data)

    return AISearchResponse(
        interpreted_query=structured.get("search_term", payload.query),
        filters_extracted=structured,
        products=raw_items,
        ai_summary=ai_result.get("analysis"),
        ai_available=ai_result.get("ai_available", False),
    )


@router.get("/analyze/{offer_id}")
async def analyze_offer(
    offer_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Given an offer ID from our database, run both rule-based and AI analysis
    and return a buy/wait recommendation with justification.
    """
    repo = ProductRepository(db)
    offer = (await repo.get_offers_for_product(offer_id))  # reuse method for now
    # Actually fetch by offer id directly:
    from sqlalchemy import select
    from app.models.models import Offer
    result = await db.execute(select(Offer).where(Offer.id == offer_id))
    offer = result.scalar_one_or_none()
    if not offer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Offer not found.")

    history = await repo.get_price_history(offer.id, limit=30)
    analyzer = DealAnalyzer()
    analysis = analyzer.analyze(offer, history)

    offer_data = {
        "title": offer.product.name if offer.product else "Unknown",
        "current_price": float(offer.current_price),
        "original_price": float(offer.original_price) if offer.original_price else None,
        "condition": offer.condition,
        "seller": offer.seller_name,
        "free_shipping": offer.free_shipping,
    }
    history_data = [
        {"price": float(h.price), "recorded_at": h.recorded_at.isoformat(), "type": h.observation_type}
        for h in history
    ]

    ai = AIService()
    ai_result = await ai.analyze_deal(offer_data, history_data, analysis)

    return {
        "offer_id": str(offer_id),
        "rule_based_analysis": analysis,
        "ai_analysis": ai_result,
    }
