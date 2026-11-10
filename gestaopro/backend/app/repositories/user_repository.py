"""
GestãoPro — UserRepository
Portado de: backend/app/repositories/user_repository.py (TechDeals AI)
Adaptado para SQLAlchemy síncrono + MySQL INT PKs
"""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from app.models.models import User, RefreshToken
from app.services.security import hash_token


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.scalar(select(User).where(User.email == email.lower()))

    def create(self, name: str, email: str, password_hash: str, role: str = "user") -> User:
        user = User(name=name, email=email.lower(), password_hash=password_hash, role=role)
        self.db.add(user)
        self.db.flush()
        return user

    def list_users(self, page: int = 1, limit: int = 20, search: str = "") -> tuple:
        q = select(User)
        if search:
            q = q.where(User.name.ilike(f"%{search}%") | User.email.ilike(f"%{search}%"))
        total = self.db.scalar(select(User).with_only_columns(
            __import__('sqlalchemy').func.count()
        ).order_by(None).where(
            (User.name.ilike(f"%{search}%") | User.email.ilike(f"%{search}%")) if search else __import__('sqlalchemy').true()
        )) or 0
        users = self.db.scalars(q.offset((page - 1) * limit).limit(limit)).all()
        return users, total

    def save_refresh_token(self, user_id: int, token: str, expires_at: datetime):
        rt = RefreshToken(user_id=user_id, token_hash=hash_token(token), expires_at=expires_at)
        self.db.add(rt)

    def get_refresh_token(self, token: str) -> Optional[RefreshToken]:
        h = hash_token(token)
        return self.db.scalar(
            select(RefreshToken).where(
                and_(
                    RefreshToken.token_hash == h,
                    RefreshToken.revoked == False,
                    RefreshToken.expires_at > datetime.now(timezone.utc),
                )
            )
        )

    def revoke_refresh_token(self, token: str):
        rt = self.get_refresh_token(token)
        if rt:
            rt.revoked = True
