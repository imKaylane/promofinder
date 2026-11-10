from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# ─── Auth ────────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserOut(BaseModel):
    id: UUID
    name: str
    email: str
    role: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Categories ──────────────────────────────────────────────────────────────

class CategoryOut(BaseModel):
    id: UUID
    name: str
    slug: str
    description: Optional[str] = None
    parent_id: Optional[UUID] = None

    model_config = {"from_attributes": True}


# ─── Products ────────────────────────────────────────────────────────────────

class ProductOut(BaseModel):
    id: UUID
    name: str
    brand: Optional[str] = None
    model: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[UUID] = None
    image_url: Optional[str] = None
    specifications: Optional[str] = None
    normalized_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ─── Offers ──────────────────────────────────────────────────────────────────

class OfferOut(BaseModel):
    id: UUID
    product_id: UUID
    source: str
    external_id: str
    product_url: str
    current_price: Decimal
    original_price: Optional[Decimal] = None
    currency: str
    availability_status: str
    condition: str
    free_shipping: bool
    seller_name: Optional[str] = None
    seller_reputation: Optional[str] = None
    last_checked_at: datetime

    model_config = {"from_attributes": True}


class OfferWithDealOut(OfferOut):
    discount_percent: Optional[Decimal] = None
    deal_classification: str = "insufficient_history"
    history_points: int = 0
    min_price_observed: Optional[Decimal] = None
    price_trend: Optional[str] = None


# ─── Price History ────────────────────────────────────────────────────────────

class PriceHistoryOut(BaseModel):
    id: UUID
    offer_id: UUID
    price: Decimal
    recorded_at: datetime
    observation_type: str

    model_config = {"from_attributes": True}


# ─── Favorites ────────────────────────────────────────────────────────────────

class FavoriteCreate(BaseModel):
    product_id: UUID


class FavoriteOut(BaseModel):
    id: UUID
    product_id: UUID
    created_at: datetime
    product: Optional[ProductOut] = None

    model_config = {"from_attributes": True}


# ─── Price Alerts ────────────────────────────────────────────────────────────

class PriceAlertCreate(BaseModel):
    product_id: UUID
    target_price: Decimal = Field(..., gt=0)


class PriceAlertUpdate(BaseModel):
    target_price: Optional[Decimal] = Field(None, gt=0)
    is_active: Optional[bool] = None


class PriceAlertOut(BaseModel):
    id: UUID
    product_id: UUID
    target_price: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime
    product: Optional[ProductOut] = None

    model_config = {"from_attributes": True}


# ─── Notifications ───────────────────────────────────────────────────────────

class NotificationOut(BaseModel):
    id: UUID
    type: str
    title: str
    message: str
    related_product_id: Optional[UUID] = None
    read_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Search ──────────────────────────────────────────────────────────────────

class SearchRequest(BaseModel):
    """Parameters for a Mercado Livre live search."""
    query: str = Field(..., min_length=1, max_length=512)
    category: Optional[str] = None
    min_price: Optional[float] = Field(None, gt=0)
    max_price: Optional[float] = Field(None, gt=0)
    condition: Optional[str] = Field(None, pattern="^(new|used)$")
    sort: Optional[str] = Field(None, pattern="^(price_asc|price_desc|relevance)$")
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=50)


class SearchResultItem(BaseModel):
    """A single normalised item returned by the live search."""
    external_id: str
    title: str
    brand: Optional[str] = None
    model: Optional[str] = None
    price: float
    original_price: Optional[float] = None
    currency: str
    url: str
    thumbnail: Optional[str] = None
    condition: str
    free_shipping: bool
    seller_name: Optional[str] = None
    seller_reputation: Optional[str] = None
    # Deterministic deal fields computed from seller data
    discount_percent: Optional[float] = None
    is_deal: bool = False


class SearchResponse(BaseModel):
    query: str
    total: int
    page: int
    limit: int
    items: List[SearchResultItem]


# ─── Deals ───────────────────────────────────────────────────────────────────

class DealOut(OfferWithDealOut):
    product: Optional[ProductOut] = None


# ─── Pagination ──────────────────────────────────────────────────────────────

class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    limit: int
    pages: int


# ─── Admin ───────────────────────────────────────────────────────────────────

class CollectionSourceOut(BaseModel):
    id: UUID
    name: str
    source_type: str
    is_active: bool
    last_run_at: Optional[datetime] = None
    last_status: Optional[str] = None

    model_config = {"from_attributes": True}


class CollectionRunOut(BaseModel):
    id: UUID
    source_id: UUID
    status: str
    started_at: datetime
    finished_at: Optional[datetime] = None
    products_processed: int
    offers_updated: int
    error_summary: Optional[str] = None

    model_config = {"from_attributes": True}
