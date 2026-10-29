import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey, Integer, Numeric,
    String, Text, UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


def now_utc():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="user")
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=now_utc)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=now_utc, onupdate=now_utc)

    favorites = relationship("Favorite", back_populates="user", lazy="dynamic")
    price_alerts = relationship("PriceAlert", back_populates="user", lazy="dynamic")
    notifications = relationship("Notification", back_populates="user", lazy="dynamic")
    refresh_tokens = relationship("RefreshToken", back_populates="user", lazy="dynamic")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(255), nullable=False, unique=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=now_utc)

    user = relationship("User", back_populates="refresh_tokens")


class Category(Base):
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=now_utc)

    parent = relationship("Category", remote_side="Category.id")
    products = relationship("Product", back_populates="category", lazy="dynamic")


class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(512), nullable=False, index=True)
    brand = Column(String(255), nullable=True)
    model = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)
    image_url = Column(String(1024), nullable=True)
    specifications = Column(Text, nullable=True)
    normalized_name = Column(String(512), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=now_utc)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=now_utc, onupdate=now_utc)

    category = relationship("Category", back_populates="products")
    offers = relationship("Offer", back_populates="product", lazy="dynamic")
    favorites = relationship("Favorite", back_populates="product", lazy="dynamic")
    price_alerts = relationship("PriceAlert", back_populates="product", lazy="dynamic")
    notifications = relationship("Notification", back_populates="related_product", lazy="dynamic")


class Store(Base):
    __tablename__ = "stores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    external_id = Column(String(255), nullable=True)
    source_type = Column(String(50), nullable=False, default="mercadolivre")
    url = Column(String(1024), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=now_utc)

    offers = relationship("Offer", back_populates="store", lazy="dynamic")


class Offer(Base):
    __tablename__ = "offers"
    __table_args__ = (
        UniqueConstraint("source", "external_id", name="uq_offer_source_external"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False, index=True)
    store_id = Column(UUID(as_uuid=True), ForeignKey("stores.id"), nullable=True, index=True)
    source = Column(String(50), nullable=False, default="mercadolivre")
    external_id = Column(String(255), nullable=False, index=True)
    product_url = Column(String(1024), nullable=False)
    current_price = Column(Numeric(12, 2), nullable=False)
    original_price = Column(Numeric(12, 2), nullable=True)
    currency = Column(String(10), nullable=False, default="BRL")
    availability_status = Column(String(50), nullable=False, default="active")
    condition = Column(String(50), nullable=False, default="new")
    free_shipping = Column(Boolean, nullable=False, default=False)
    seller_name = Column(String(255), nullable=True)
    seller_reputation = Column(String(50), nullable=True)
    last_checked_at = Column(DateTime(timezone=True), nullable=False, default=now_utc)
    created_at = Column(DateTime(timezone=True), nullable=False, default=now_utc)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=now_utc, onupdate=now_utc)

    product = relationship("Product", back_populates="offers")
    store = relationship("Store", back_populates="offers")
    price_history = relationship("PriceHistory", back_populates="offer", lazy="dynamic")


class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    offer_id = Column(UUID(as_uuid=True), ForeignKey("offers.id", ondelete="CASCADE"), nullable=False, index=True)
    price = Column(Numeric(12, 2), nullable=False)
    recorded_at = Column(DateTime(timezone=True), nullable=False, default=now_utc, index=True)
    observation_type = Column(String(50), nullable=False, default="scheduled")

    offer = relationship("Offer", back_populates="price_history")


class Favorite(Base):
    __tablename__ = "favorites"
    __table_args__ = (
        UniqueConstraint("user_id", "product_id", name="uq_favorite_user_product"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=now_utc)

    user = relationship("User", back_populates="favorites")
    product = relationship("Product", back_populates="favorites")


class PriceAlert(Base):
    __tablename__ = "price_alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    target_price = Column(Numeric(12, 2), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=now_utc)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=now_utc, onupdate=now_utc)

    user = relationship("User", back_populates="price_alerts")
    product = relationship("Product", back_populates="price_alerts")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(50), nullable=False)
    title = Column(String(512), nullable=False)
    message = Column(Text, nullable=False)
    related_product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=now_utc)

    user = relationship("User", back_populates="notifications")
    related_product = relationship("Product", back_populates="notifications")


class CollectionSource(Base):
    __tablename__ = "collection_sources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    source_type = Column(String(50), nullable=False, default="mercadolivre")
    is_active = Column(Boolean, nullable=False, default=True)
    last_run_at = Column(DateTime(timezone=True), nullable=True)
    last_status = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=now_utc)

    runs = relationship("CollectionRun", back_populates="source", lazy="dynamic")


class CollectionRun(Base):
    __tablename__ = "collection_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id = Column(UUID(as_uuid=True), ForeignKey("collection_sources.id"), nullable=False, index=True)
    status = Column(String(50), nullable=False, default="running")
    started_at = Column(DateTime(timezone=True), nullable=False, default=now_utc)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    products_processed = Column(Integer, nullable=False, default=0)
    offers_updated = Column(Integer, nullable=False, default=0)
    error_summary = Column(Text, nullable=True)

    source = relationship("CollectionSource", back_populates="runs")
