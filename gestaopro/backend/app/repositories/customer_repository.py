"""
GestãoPro — CustomerRepository (EX3 — segunda entidade CRUD)
"""
import math
from typing import Optional

from sqlalchemy import select, func, and_
from sqlalchemy.orm import Session

from app.models.models import Customer


class CustomerRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, customer_id: int) -> Optional[Customer]:
        return self.db.get(Customer, customer_id)

    def list(self, page: int = 1, limit: int = 20, search: str = "", status: str = "") -> tuple:
        q = select(Customer)
        count_q = select(func.count()).select_from(Customer)

        filters = []
        if search:
            like = f"%{search}%"
            filters.append(Customer.name.ilike(like) | Customer.email.ilike(like))
        if status:
            filters.append(Customer.status == status)

        if filters:
            combined = and_(*filters)
            q = q.where(combined)
            count_q = count_q.where(combined)

        total = self.db.scalar(count_q) or 0
        items = self.db.scalars(q.order_by(Customer.name).offset((page - 1) * limit).limit(limit)).all()
        pages = math.ceil(total / limit) if total else 0
        return items, total, pages

    def create(self, data: dict) -> Customer:
        c = Customer(**{k: v for k, v in data.items() if hasattr(Customer, k)})
        self.db.add(c)
        self.db.flush()
        return c

    def update(self, customer: Customer, data: dict) -> Customer:
        for k, v in data.items():
            if hasattr(customer, k):
                setattr(customer, k, v)
        self.db.flush()
        return customer

    def delete(self, customer: Customer):
        self.db.delete(customer)
        self.db.flush()
