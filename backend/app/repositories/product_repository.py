"""ProductRepository — all DB queries for products, offers and price history."""

import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import select, func, and_, or_, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Category, Offer, PriceHistory, Product, Store
from app.integrations.mercadolivre import MeliOffer

logger = logging.getLogger(__name__)


class ProductRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, product_id: UUID) -> Optional[Product]:
        result = await self.db.execute(select(Product).where(Product.id == product_id))
        return result.scalar_one_or_none()

    async def search(
        self,
        query: str,
        category_id: Optional[UUID] = None,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None,
        condition: Optional[str] = None,
        sort: str = "relevance",
        offset: int = 0,
        limit: int = 20,
    ) -> Tuple[List[Product], int]:
        base_q = select(Product).join(Offer, Offer.product_id == Product.id, isouter=True)
        filters = []
        if query:
            like = f"%{query.lower()}%"
            filters.append(or_(
                func.lower(Product.name).like(like),
                func.lower(Product.brand).like(like),
                func.lower(Product.model).like(like),
                func.lower(Product.normalized_name).like(like),
            ))
        if category_id:
            filters.append(Product.category_id == category_id)
        if min_price is not None:
            filters.append(Offer.current_price >= min_price)
        if max_price is not None:
            filters.append(Offer.current_price <= max_price)
        if condition:
            filters.append(Offer.condition == condition)
        if filters:
            base_q = base_q.where(and_(*filters))

        count_q = select(func.count()).select_from(base_q.subquery())
        total = (await self.db.execute(count_q)).scalar_one()

        if sort == "price_asc":
            base_q = base_q.order_by(asc(Offer.current_price))
        elif sort == "price_desc":
            base_q = base_q.order_by(desc(Offer.current_price))
        else:
            base_q = base_q.order_by(desc(Product.updated_at))

        base_q = base_q.distinct(Product.id).offset(offset).limit(limit)
        result = await self.db.execute(base_q)
        return result.scalars().all(), total

    async def upsert_from_meli(self, offer: MeliOffer, category_id: Optional[UUID] = None) -> Tuple[Product, Offer]:
        store = await self._get_or_create_meli_store(offer.seller_id, offer.seller_nickname)
        existing_offer = await self._get_offer_by_external_id("mercadolivre", offer.external_id)

        if existing_offer:
            product = await self.get_by_id(existing_offer.product_id)
            old_price = existing_offer.current_price
            existing_offer.current_price = Decimal(str(offer.price)) if offer.price else existing_offer.current_price
            existing_offer.original_price = Decimal(str(offer.original_price)) if offer.original_price else None
            existing_offer.availability_status = "active" if (offer.available_quantity or 0) > 0 else "unavailable"
            existing_offer.free_shipping = offer.free_shipping or False
            existing_offer.seller_name = offer.seller_nickname
            existing_offer.seller_reputation = offer.seller_reputation
            existing_offer.last_checked_at = datetime.now(timezone.utc)
            if existing_offer.current_price != old_price:
                await self._record_price(existing_offer.id, existing_offer.current_price, "scheduled")
            return product, existing_offer

        product = Product(
            name=offer.title or "Unknown",
            brand=offer.brand,
            model=offer.model,
            category_id=category_id,
            image_url=offer.thumbnail,
            normalized_name=(offer.title or "").lower().strip(),
        )
        self.db.add(product)
        await self.db.flush()

        new_offer = Offer(
            product_id=product.id,
            store_id=store.id if store else None,
            source="mercadolivre",
            external_id=offer.external_id,
            product_url=offer.url or "",
            current_price=Decimal(str(offer.price)) if offer.price else Decimal("0"),
            original_price=Decimal(str(offer.original_price)) if offer.original_price else None,
            currency=offer.currency or "BRL",
            availability_status="active",
            condition=offer.condition or "new",
            free_shipping=offer.free_shipping or False,
            seller_name=offer.seller_nickname,
            seller_reputation=offer.seller_reputation,
        )
        self.db.add(new_offer)
        await self.db.flush()
        await self._record_price(new_offer.id, new_offer.current_price, "initial")
        return product, new_offer

    async def get_offers_for_product(self, product_id: UUID) -> List[Offer]:
        result = await self.db.execute(
            select(Offer).where(Offer.product_id == product_id).order_by(asc(Offer.current_price))
        )
        return result.scalars().all()

    async def get_price_history(self, offer_id: UUID, limit: int = 90) -> List[PriceHistory]:
        result = await self.db.execute(
            select(PriceHistory)
            .where(PriceHistory.offer_id == offer_id)
            .order_by(desc(PriceHistory.recorded_at))
            .limit(limit)
        )
        return result.scalars().all()

    async def get_all_categories(self) -> List[Category]:
        result = await self.db.execute(select(Category).order_by(Category.name))
        return result.scalars().all()

    async def get_active_offers(self, limit: int = 200) -> List[Offer]:
        result = await self.db.execute(
            select(Offer)
            .where(Offer.availability_status == "active")
            .order_by(Offer.last_checked_at.asc())
            .limit(limit)
        )
        return result.scalars().all()

    async def _get_offer_by_external_id(self, source: str, external_id: str) -> Optional[Offer]:
        result = await self.db.execute(
            select(Offer).where(and_(Offer.source == source, Offer.external_id == external_id))
        )
        return result.scalar_one_or_none()

    async def _get_or_create_meli_store(self, seller_id: Optional[str], seller_nickname: Optional[str]) -> Optional[Store]:
        if not seller_id:
            return None
        result = await self.db.execute(
            select(Store).where(and_(Store.external_id == seller_id, Store.source_type == "mercadolivre"))
        )
        store = result.scalar_one_or_none()
        if store:
            return store
        store = Store(
            name=seller_nickname or f"MELI:{seller_id}",
            external_id=seller_id,
            source_type="mercadolivre",
            url=f"https://www.mercadolivre.com.br/perfil/{seller_nickname}" if seller_nickname else None,
        )
        self.db.add(store)
        await self.db.flush()
        return store

    async def _record_price(self, offer_id: UUID, price: Decimal, obs_type: str):
        ph = PriceHistory(offer_id=offer_id, price=price, observation_type=obs_type)
        self.db.add(ph)
