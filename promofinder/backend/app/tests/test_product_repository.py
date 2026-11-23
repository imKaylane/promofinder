from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.integrations.mercadolivre import MeliOffer
from app.repositories.product_repository import ProductRepository


@pytest.mark.asyncio
async def test_upsert_keeps_active_listing_when_quantity_is_not_returned():
    repository = ProductRepository(AsyncMock())
    existing_offer = SimpleNamespace(
        product_id="product-1",
        current_price=Decimal("100"),
        original_price=None,
        availability_status="unavailable",
        free_shipping=False,
        seller_name=None,
        seller_reputation=None,
    )
    repository._get_or_create_meli_store = AsyncMock(return_value=None)
    repository._get_offer_by_external_id = AsyncMock(return_value=existing_offer)
    repository.get_by_id = AsyncMock(return_value=object())
    repository._record_price = AsyncMock()
    meli_offer = MeliOffer(
        external_id="MLB_ITEM_1",
        price=100,
        original_price=None,
        available_quantity=None,
        free_shipping=False,
    )

    await repository.upsert_from_meli(meli_offer)

    assert existing_offer.availability_status == "active"
