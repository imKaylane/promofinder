"""UserRepository — all DB queries for users, tokens, favorites, alerts."""

import hashlib
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Favorite, Notification, PriceAlert, RefreshToken, User


class UserRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.email == email.lower()))
        return result.scalar_one_or_none()

    async def create(self, name: str, email: str, password_hash: str, role: str = "user") -> User:
        user = User(name=name, email=email.lower(), password_hash=password_hash, role=role)
        self.db.add(user)
        await self.db.flush()
        return user

    async def save_refresh_token(self, user_id: UUID, token: str, expires_at: datetime):
        h = hashlib.sha256(token.encode()).hexdigest()
        rt = RefreshToken(user_id=user_id, token_hash=h, expires_at=expires_at)
        self.db.add(rt)

    async def get_refresh_token(self, token: str) -> Optional[RefreshToken]:
        h = hashlib.sha256(token.encode()).hexdigest()
        with self.db.no_autoflush:
            result = await self.db.execute(
                select(RefreshToken).where(
                    and_(
                        RefreshToken.token_hash == h,
                        RefreshToken.revoked == False,  # noqa: E712
                        RefreshToken.expires_at > datetime.now(timezone.utc),
                    )
                )
            )
        return result.scalar_one_or_none()

    async def revoke_refresh_token(self, token: str):
        rt = await self.get_refresh_token(token)
        if rt:
            rt.revoked = True

    async def get_favorites(self, user_id: UUID) -> list:
        result = await self.db.execute(select(Favorite).where(Favorite.user_id == user_id))
        return result.scalars().all()

    async def get_favorite(self, user_id: UUID, product_id: UUID) -> Optional[Favorite]:
        result = await self.db.execute(
            select(Favorite).where(and_(Favorite.user_id == user_id, Favorite.product_id == product_id))
        )
        return result.scalar_one_or_none()

    async def add_favorite(self, user_id: UUID, product_id: UUID) -> Favorite:
        fav = Favorite(user_id=user_id, product_id=product_id)
        self.db.add(fav)
        await self.db.flush()
        return fav

    async def remove_favorite(self, user_id: UUID, product_id: UUID) -> bool:
        fav = await self.get_favorite(user_id, product_id)
        if fav:
            await self.db.delete(fav)
            return True
        return False

    async def get_alerts(self, user_id: UUID) -> list:
        result = await self.db.execute(select(PriceAlert).where(PriceAlert.user_id == user_id))
        return result.scalars().all()

    async def get_alert_by_id(self, alert_id: UUID, user_id: UUID) -> Optional[PriceAlert]:
        result = await self.db.execute(
            select(PriceAlert).where(and_(PriceAlert.id == alert_id, PriceAlert.user_id == user_id))
        )
        return result.scalar_one_or_none()

    async def create_alert(self, user_id: UUID, product_id: UUID, target_price) -> PriceAlert:
        alert = PriceAlert(user_id=user_id, product_id=product_id, target_price=target_price)
        self.db.add(alert)
        await self.db.flush()
        return alert

    async def get_all_active_alerts(self) -> list:
        result = await self.db.execute(
            select(PriceAlert).where(PriceAlert.is_active == True)  # noqa: E712
        )
        return result.scalars().all()

    async def get_notifications(self, user_id: UUID, limit: int = 50) -> list:
        result = await self.db.execute(
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(desc(Notification.created_at))
            .limit(limit)
        )
        return result.scalars().all()

    async def create_notification(
        self, user_id: UUID, ntype: str, title: str, message: str,
        related_product_id: Optional[UUID] = None,
    ) -> Notification:
        n = Notification(
            user_id=user_id, type=ntype, title=title,
            message=message, related_product_id=related_product_id,
        )
        self.db.add(n)
        await self.db.flush()
        return n
