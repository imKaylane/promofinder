"""User profile, price-alerts, and notification endpoints."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.repositories.user_repository import UserRepository
from app.schemas.schemas import UserOut, PriceAlertCreate, PriceAlertOut, NotificationOut
from app.models.models import User

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserOut.model_validate(current_user)


# ---------------------------------------------------------------------------
# Price Alerts
# ---------------------------------------------------------------------------

@router.get("/me/alerts", response_model=list[PriceAlertOut])
async def list_my_alerts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = UserRepository(db)
    alerts = await repo.get_alerts(current_user.id)
    return [PriceAlertOut.model_validate(a) for a in alerts]


@router.post("/me/alerts", response_model=PriceAlertOut, status_code=status.HTTP_201_CREATED)
async def create_alert(
    payload: PriceAlertCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = UserRepository(db)
    alert = await repo.create_alert(current_user.id, payload.product_id, payload.target_price)
    return PriceAlertOut.model_validate(alert)


@router.delete("/me/alerts/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert(
    alert_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = UserRepository(db)
    alert = await repo.get_alert_by_id(alert_id, current_user.id)
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found.")
    await db.delete(alert)


# ---------------------------------------------------------------------------
# Notifications
# ---------------------------------------------------------------------------

@router.get("/me/notifications", response_model=list[NotificationOut])
async def get_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = UserRepository(db)
    notifications = await repo.get_notifications(current_user.id)
    return [NotificationOut.model_validate(n) for n in notifications]
