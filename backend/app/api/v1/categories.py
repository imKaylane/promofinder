"""Category listing — pass-through from local DB (populated by ML ingestion)."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.repositories.product_repository import ProductRepository
from app.schemas.schemas import CategoryOut

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryOut])
async def list_categories(db: AsyncSession = Depends(get_db)):
    """Return all categories stored in the local database."""
    repo = ProductRepository(db)
    categories = await repo.get_all_categories()
    return [CategoryOut.model_validate(c) for c in categories]
