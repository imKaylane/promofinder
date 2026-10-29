"""Tests for MercadoLivreService — mock httpx to avoid real API calls."""
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from app.integrations.mercadolivre import MercadoLivreService, MeliOffer


def test_normalise_result_basic():
    raw = {
        "id": "MLB123",
        "title": "Notebook Gamer",
        "price": 3999.90,
        "original_price": 4499.00,
        "currency_id": "BRL",
        "permalink": "https://www.mercadolivre.com.br/p/MLB123",
        "thumbnail": "https://img.mlstatic.com/thumb.jpg",
        "category_id": "MLB1652",
        "condition": "new",
        "available_quantity": 10,
        "shipping": {"free_shipping": True},
        "seller": {"id": 456, "nickname": "BestStore"},
        "attributes": [
            {"id": "BRAND", "value_name": "Dell"},
            {"id": "MODEL", "value_name": "G15"},
        ],
    }
    offer = MercadoLivreService.normalise_result(raw)
    assert offer.external_id == "MLB123"
    assert offer.title == "Notebook Gamer"
    assert offer.price == 3999.90
    assert offer.original_price == 4499.00
    assert offer.brand == "Dell"
    assert offer.model == "G15"
    assert offer.free_shipping is True
    assert offer.seller_nickname == "BestStore"


def test_normalise_result_missing_fields():
    raw = {"id": "MLB999", "price": 100.0}
    offer = MercadoLivreService.normalise_result(raw)
    assert offer.external_id == "MLB999"
    assert offer.title is None
    assert offer.brand is None
    assert offer.free_shipping is False


def test_normalise_results_list():
    raws = [
        {"id": "MLB1", "price": 100.0},
        {"id": "MLB2", "price": 200.0},
    ]
    offers = MercadoLivreService.normalise_results(raws)
    assert len(offers) == 2
    assert all(isinstance(o, MeliOffer) for o in offers)


@pytest.mark.asyncio
async def test_search_calls_get():
    service = MercadoLivreService()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"results": [], "paging": {"total": 0}}
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    service._client = mock_client

    # Patch _get_app_token to return None (no auth needed for public endpoints)
    with patch.object(service, "_get_app_token", return_value=None):
        result = await service.search("ryzen 7", limit=10)

    assert "results" in result
    mock_client.get.assert_called_once()
    call_kwargs = mock_client.get.call_args
    assert "q" in call_kwargs.kwargs.get("params", call_kwargs.args[1] if len(call_kwargs.args) > 1 else {})


@pytest.mark.asyncio
async def test_get_item_returns_none_on_404():
    service = MercadoLivreService()

    mock_response = MagicMock()
    mock_response.status_code = 404

    import httpx
    mock_client = AsyncMock()
    mock_client.get.side_effect = httpx.HTTPStatusError(
        "404", request=MagicMock(), response=mock_response
    )
    service._client = mock_client

    with patch.object(service, "_get_app_token", return_value=None):
        result = await service.get_item("MLB_NONEXISTENT")
    assert result is None
