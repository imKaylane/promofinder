"""Admin endpoints — user management and system stats (admin-only)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.api.deps import get_db, require_admin
from app.models.models import User, Product, PriceAlert, CollectionSource, CollectionRun
from app.repositories.user_repository import UserRepository
from app.schemas.schemas import UserOut, CollectionSourceOut, CollectionRunOut

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats")
async def get_stats(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    user_count = (await db.execute(select(func.count()).select_from(User))).scalar()
    product_count = (await db.execute(select(func.count()).select_from(Product))).scalar()
    alert_count = (await db.execute(select(func.count()).select_from(PriceAlert))).scalar()

    return {
        "users": user_count,
        "products": product_count,
        "alerts": alert_count,
    }


@router.get("/users", response_model=list[UserOut])
async def list_users(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    return [UserOut.model_validate(u) for u in result.scalars().all()]


@router.patch("/users/{user_id}/deactivate", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    from uuid import UUID
    try:
        uid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID.")
    if uid == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot deactivate yourself.")
    repo = UserRepository(db)
    user = await repo.get_by_id(uid)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    user.is_active = False
    await db.flush()


@router.patch("/users/{user_id}/activate", status_code=status.HTTP_204_NO_CONTENT)
async def activate_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    from uuid import UUID
    try:
        uid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID.")
    repo = UserRepository(db)
    user = await repo.get_by_id(uid)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    user.is_active = True
    await db.flush()


@router.get("/collection-sources", response_model=list[CollectionSourceOut])
async def list_collection_sources(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    result = await db.execute(select(CollectionSource).order_by(CollectionSource.name))
    return [CollectionSourceOut.model_validate(s) for s in result.scalars().all()]


@router.get("/collection-runs", response_model=list[CollectionRunOut])
async def list_collection_runs(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    result = await db.execute(
        select(CollectionRun).order_by(CollectionRun.started_at.desc()).limit(100)
    )
    return [CollectionRunOut.model_validate(r) for r in result.scalars().all()]
