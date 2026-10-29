"""Product search and detail endpoints (backed by Mercado Livre + ORM)."""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user_optional, get_current_user
from app.integrations.mercadolivre import MercadoLivreService, MeliOffer
from app.repositories.product_repository import ProductRepository
from app.repositories.user_repository import UserRepository
from app.schemas.schemas import ProductOut, OfferOut, FavoriteOut, PaginatedResponse
from app.models.models import User

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/search", response_model=PaginatedResponse)
async def search_products(
    q: str = Query(..., min_length=2, description="Search query"),
    category_id: Optional[UUID] = Query(None),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    condition: Optional[str] = Query(None, pattern="^(new|used|not_specified)$"),
    sort: str = Query("relevance", pattern="^(relevance|price_asc|price_desc|newest)$"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Search products in our database (populated from Mercado Livre)."""
    from decimal import Decimal

    repo = ProductRepository(db)
    offset = (page - 1) * limit
    products, total = await repo.search(
        query=q,
        category_id=category_id,
        min_price=Decimal(str(min_price)) if min_price is not None else None,
        max_price=Decimal(str(max_price)) if max_price is not None else None,
        condition=condition,
        sort=sort,
        offset=offset,
        limit=limit,
    )

    import math
    return PaginatedResponse(
        items=[ProductOut.model_validate(p) for p in products],
        total=total,
        page=page,
        limit=limit,
        pages=math.ceil(total / limit) if total else 0,
    )


@router.get("/search/live", response_model=dict)
async def search_live(
    q: str = Query(..., min_length=2),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    condition: Optional[str] = Query(None),
    sort: str = Query("relevance"),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    Fetch products live from Mercado Livre, persist them, and return raw results.
    Use this endpoint for real-time discovery; use /search for local results.
    """
    ml = MercadoLivreService()
    results = await ml.search_products(
        query=q,
        min_price=min_price,
        max_price=max_price,
        condition=condition,
        sort=sort,
        offset=offset,
        limit=limit,
    )

    # Persist new items in the background so /search gets richer over time.
    repo = ProductRepository(db)
    for raw in results.get("results", []):
        offer = MeliOffer.from_raw(raw)
        try:
            await repo.upsert_from_meli(offer)
        except Exception:
            pass  # Don't fail the request if persistence fails.

    return {
        "query": q,
        "total": results.get("paging", {}).get("total", 0),
        "offset": offset,
        "limit": limit,
        "results": results.get("results", []),
    }


@router.get("/{product_id}", response_model=ProductOut)
async def get_product(product_id: UUID, db: AsyncSession = Depends(get_db)):
    repo = ProductRepository(db)
    product = await repo.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")
    return product


@router.get("/{product_id}/offers", response_model=list[OfferOut])
async def get_product_offers(product_id: UUID, db: AsyncSession = Depends(get_db)):
    repo = ProductRepository(db)
    product = await repo.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")
    offers = await repo.get_offers_for_product(product_id)
    return [OfferOut.model_validate(o) for o in offers]


@router.post("/{product_id}/favorite", response_model=FavoriteOut, status_code=status.HTTP_201_CREATED)
async def add_favorite(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = UserRepository(db)
    existing = await repo.get_favorite(current_user.id, product_id)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already in favorites.")
    fav = await repo.add_favorite(current_user.id, product_id)
    return FavoriteOut.model_validate(fav)


@router.delete("/{product_id}/favorite", status_code=status.HTTP_204_NO_CONTENT)
async def remove_favorite(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = UserRepository(db)
    removed = await repo.remove_favorite(current_user.id, product_id)
    if not removed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Favorite not found.")


@router.get("/favorites/me", response_model=list[FavoriteOut])
async def list_my_favorites(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = UserRepository(db)
    favorites = await repo.get_favorites(current_user.id)
    return [FavoriteOut.model_validate(f) for f in favorites]
