"""Tests for MercadoLivreService — mock httpx to avoid real API calls."""
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from redis.exceptions import RedisError

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
    products_response = MagicMock()
    products_response.status_code = 200
    products_response.json.return_value = {
        "results": [
            {
                "id": "MLB_PRODUCT_1",
                "name": "AMD Ryzen 7 5700X",
                "pictures": [{"url": "https://example.com/image.jpg"}],
                "attributes": [],
            }
        ],
        "paging": {"total": 1},
    }
    products_response.raise_for_status = MagicMock()
    listings_response = MagicMock()
    listings_response.status_code = 200
    listings_response.json.return_value = {
        "results": [
            {
                "item_id": "MLB_ITEM_1",
                "price": 100.0,
                "currency_id": "BRL",
                "seller_id": 456,
                "condition": "new",
                "shipping": {"free_shipping": True},
            }
        ]
    }
    listings_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.get.side_effect = [products_response, listings_response]
    service._client = mock_client

    # No account/app token: exercise the public-search fallback.
    with patch(
        "app.integrations.mercadolivre.MercadoLivreOAuth.get_access_token",
        side_effect=RedisError("Redis unavailable"),
    ), \
            patch.object(service, "_get_app_token", return_value=None):
        result = await service.search("ryzen 7", limit=10)

    assert result["paging"]["total"] == 1
    assert result["results"][0]["id"] == "MLB_ITEM_1"
    assert result["results"][0]["title"] == "AMD Ryzen 7 5700X"
    assert result["results"][0]["thumbnail"] == "https://example.com/image.jpg"
    assert mock_client.get.await_count == 2
    search_call = mock_client.get.await_args_list[0]
    assert search_call.args[0] == "/products/search"
    assert search_call.kwargs["params"]["q"] == "ryzen 7"
    assert search_call.kwargs["params"]["status"] == "active"
    assert mock_client.get.await_args_list[1].args[0] == "/products/MLB_PRODUCT_1/items"


@pytest.mark.asyncio
async def test_search_does_not_retry_forbidden_responses():
    service = MercadoLivreService()
    response = MagicMock()
    response.status_code = 403

    mock_client = AsyncMock()
    mock_client.get.return_value = response
    service._client = mock_client

    with pytest.raises(PermissionError):
        await service._get("/products/search")

    mock_client.get.assert_awaited_once()


@pytest.mark.asyncio
async def test_search_skips_products_without_accessible_listings():
    import httpx

    service = MercadoLivreService()
    products_response = httpx.Response(
        200,
        json={
            "results": [
                {"id": "MLB_PRODUCT_MISSING", "name": "SSD NVMe unavailable listing"},
                {"id": "MLB_PRODUCT_1", "name": "SSD NVMe 1TB"},
            ],
            "paging": {"total": 2},
        },
        request=httpx.Request("GET", "https://api.mercadolibre.com/products/search"),
    )
    missing_response = httpx.Response(
        404,
        request=httpx.Request(
            "GET",
            "https://api.mercadolibre.com/products/MLB_PRODUCT_MISSING/items",
        ),
    )
    listings_response = httpx.Response(
        200,
        json={
            "results": [
                {
                    "item_id": "MLB_ITEM_1",
                    "price": 100.0,
                    "seller_id": 456,
                    "condition": "new",
                }
            ]
        },
        request=httpx.Request(
            "GET",
            "https://api.mercadolibre.com/products/MLB_PRODUCT_1/items",
        ),
    )
    mock_client = AsyncMock()
    mock_client.get.side_effect = [
        products_response,
        missing_response,
        listings_response,
    ]
    service._client = mock_client

    with patch(
        "app.integrations.mercadolivre.MercadoLivreOAuth.get_access_token",
        side_effect=RedisError("Redis unavailable"),
    ), patch.object(service, "_get_app_token", return_value=None):
        result = await service.search("ssd nvme", limit=5)

    assert [item["id"] for item in result["results"]] == ["MLB_ITEM_1"]


@pytest.mark.asyncio
async def test_search_continues_to_next_catalog_page_until_offer_limit_is_met():
    import httpx

    service = MercadoLivreService()
    first_page = httpx.Response(
        200,
        json={
            "results": [{"id": "MLB_PRODUCT_MISSING", "name": "Ryzen 7 without listings"}],
            "paging": {"total": 2},
        },
        request=httpx.Request("GET", "https://api.mercadolibre.com/products/search"),
    )
    missing_response = httpx.Response(
        404,
        request=httpx.Request(
            "GET",
            "https://api.mercadolibre.com/products/MLB_PRODUCT_MISSING/items",
        ),
    )
    second_page = httpx.Response(
        200,
        json={
            "results": [
                {
                    "id": "MLB_PRODUCT_1",
                    "name": "AMD Ryzen 7 5700X",
                    "pictures": [{"url": "https://example.com/image.jpg"}],
                }
            ],
            "paging": {"total": 2},
        },
        request=httpx.Request("GET", "https://api.mercadolibre.com/products/search"),
    )
    listings_response = httpx.Response(
        200,
        json={
            "results": [
                {
                    "item_id": "MLB_ITEM_1",
                    "price": 100.0,
                    "seller_id": 456,
                    "condition": "new",
                }
            ]
        },
        request=httpx.Request(
            "GET",
            "https://api.mercadolibre.com/products/MLB_PRODUCT_1/items",
        ),
    )
    mock_client = AsyncMock()
    mock_client.get.side_effect = [
        first_page,
        missing_response,
        second_page,
        listings_response,
    ]
    service._client = mock_client

    with patch(
        "app.integrations.mercadolivre.MercadoLivreOAuth.get_access_token",
        side_effect=RedisError("Redis unavailable"),
    ), patch.object(service, "_get_app_token", return_value=None):
        result = await service.search("ryzen 7", limit=1)

    assert [item["id"] for item in result["results"]] == ["MLB_ITEM_1"]
    search_calls = [
        call for call in mock_client.get.await_args_list
        if call.args[0] == "/products/search"
    ]
    assert [call.kwargs["params"]["offset"] for call in search_calls] == [0, 1]


@pytest.mark.asyncio
async def test_search_rejects_books_even_when_their_title_mentions_pc_parts():
    service = MercadoLivreService()
    service._get = AsyncMock(side_effect=[
        {
            "results": [
                {"id": "MLB_BOOK", "name": "Livro: guia completo de placas de vídeo"},
                {
                    "id": "MLB_GPU",
                    "name": "Placa de Vídeo GeForce RTX 4060",
                    "pictures": [],
                },
            ],
            "paging": {"total": 2},
        },
        {
            "results": [
                {
                    "item_id": "MLB_GPU_ITEM",
                    "price": 1000.0,
                    "seller_id": 456,
                    "condition": "new",
                }
            ]
        },
    ])

    with patch(
        "app.integrations.mercadolivre.MercadoLivreOAuth.get_access_token",
        side_effect=RedisError("Redis unavailable"),
    ), patch.object(service, "_get_app_token", return_value=None):
        result = await service.search("placa de video", limit=5)

    assert [item["id"] for item in result["results"]] == ["MLB_GPU_ITEM"]
    assert service._get.await_count == 2
    assert service._get.await_args_list[1].args[0] == "/products/MLB_GPU/items"


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
