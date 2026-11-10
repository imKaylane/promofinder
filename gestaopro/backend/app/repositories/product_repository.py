"""
GestãoPro — ProductRepository (EX3)
CRUD completo com busca, filtros e paginação.
Usa prepared statements via SQLAlchemy parametrizado (seguro contra SQL injection).
"""
import math
from decimal import Decimal
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.models import Product


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, product_id: int) -> Optional[Product]:
        return self.db.get(Product, product_id)

    def get_by_sku(self, sku: str) -> Optional[Product]:
        return self.db.scalar(select(Product).where(Product.sku == sku))

    def list(
        self,
        page: int = 1,
        limit: int = 20,
        search: str = "",
        status: str = "",
        category_id: Optional[int] = None,
    ) -> tuple:
        """Returns (items, total, pages)."""
        q = select(Product)
        count_q = select(func.count()).select_from(Product)

        filters = []
        if search:
            like = f"%{search}%"
            filters.append(Product.name.ilike(like) | Product.sku.ilike(like))
        if status:
            filters.append(Product.status == status)
        if category_id:
            filters.append(Product.category_id == category_id)

        if filters:
            from sqlalchemy import and_
            combined = and_(*filters)
            q = q.where(combined)
            count_q = count_q.where(combined)

        total = self.db.scalar(count_q) or 0
        items = self.db.scalars(
            q.order_by(Product.name).offset((page - 1) * limit).limit(limit)
        ).all()
        pages = math.ceil(total / limit) if total else 0
        return items, total, pages

    def create(self, data: dict) -> Product:
        product = Product(**data)
        self.db.add(product)
        self.db.flush()
        return product

    def update(self, product: Product, data: dict) -> Product:
        for key, value in data.items():
            if hasattr(product, key):
                setattr(product, key, value)
        self.db.flush()
        return product

    def delete(self, product: Product):
        self.db.delete(product)
        self.db.flush()
