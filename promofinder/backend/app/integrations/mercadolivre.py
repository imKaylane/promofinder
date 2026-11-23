"""
MercadoLivreService — centralised integration with the official MELI API (MLB).
All HTTP calls to api.mercadolibre.com go through this module only.
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import httpx
from redis.exceptions import RedisError
from tenacity import (
    retry, stop_after_attempt, wait_exponential,
    retry_if_exception, before_sleep_log,
)

from app.core.config import settings
from app.integrations.mercadolivre_oauth import MercadoLivreOAuth
from app.services.product_relevance import is_relevant_product

logger = logging.getLogger(__name__)

MELI_BASE = "https://api.mercadolibre.com"
MELI_OAUTH = "https://api.mercadolibre.com/oauth/token"


class MeliOffer:
    __slots__ = (
        "external_id", "title", "brand", "model",
        "price", "original_price", "currency",
        "url", "thumbnail", "category_id",
        "condition", "available_quantity",
        "free_shipping", "seller_id", "seller_nickname", "seller_reputation",
    )

    def __init__(self, **kwargs):
        for key in self.__slots__:
            setattr(self, key, kwargs.get(key))


class _TokenCache:
    def __init__(self):
        self._access_token: Optional[str] = None
        self._expires_at: Optional[datetime] = None

    def set(self, token: str, expires_in: int):
        self._access_token = token
        self._expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in - 60)

    def get(self) -> Optional[str]:
        if self._access_token and datetime.now(timezone.utc) < self._expires_at:
            return self._access_token
        return None

    def clear(self):
        self._access_token = None
        self._expires_at = None


_token_cache = _TokenCache()


class MercadoLivreService:
    def __init__(self):
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient(
            base_url=MELI_BASE,
            timeout=httpx.Timeout(15.0),
            headers={"User-Agent": "TechDealsAI/1.0"},
        )
        return self

    async def __aexit__(self, *_):
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _get_app_token(self) -> Optional[str]:
        if not settings.MELI_CLIENT_ID or not settings.MELI_CLIENT_SECRET:
            return None
        cached = _token_cache.get()
        if cached:
            return cached
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                MELI_OAUTH,
                data={
                    "grant_type": "client_credentials",
                    "client_id": settings.MELI_CLIENT_ID,
                    "client_secret": settings.MELI_CLIENT_SECRET,
                },
            )
        if resp.status_code == 200:
            data = resp.json()
            _token_cache.set(data["access_token"], data.get("expires_in", 21600))
            return _token_cache.get()
        logger.warning("MELI: failed to obtain app token: %s", resp.status_code)
        return None

    def _auth_headers(self, token: Optional[str]) -> dict:
        return {"Authorization": f"Bearer {token}"} if token else {}

    @retry(
        retry=retry_if_exception(
            lambda exc: isinstance(exc, httpx.RequestError)
            or (
                isinstance(exc, httpx.HTTPStatusError)
                and exc.response.status_code == 429
            )
        ),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    async def _get(self, path: str, params: Optional[dict] = None, token: Optional[str] = None) -> dict:
        assert self._client, "Use MercadoLivreService as async context manager"
        headers = self._auth_headers(token)
        resp = await self._client.get(path, params=params, headers=headers)
        if resp.status_code == 401:
            _token_cache.clear()
            raise httpx.HTTPStatusError("401", request=resp.request, response=resp)
        if resp.status_code == 403:
            raise PermissionError(f"MELI 403 on {path}")
        if resp.status_code == 429:
            retry_after = int(resp.headers.get("Retry-After", "5"))
            await asyncio.sleep(retry_after)
            raise httpx.HTTPStatusError("429", request=resp.request, response=resp)
        resp.raise_for_status()
        return resp.json()

    async def search(
        self,
        query: str,
        *,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        condition: Optional[str] = None,
        sort: Optional[str] = None,
        offset: int = 0,
        limit: int = 50,
    ) -> Dict[str, Any]:
        # Use the connected seller token when available; the public search must
        # remain usable when Redis is unavailable or no account is connected.
        try:
            token = await MercadoLivreOAuth().get_access_token()
        except RedisError:
            logger.warning("Mercado Livre OAuth token unavailable because Redis could not be reached")
            token = None
        try:
            token = token or await self._get_app_token()
        except httpx.HTTPError:
            logger.warning("Could not obtain an optional Mercado Livre app token; trying public search")
            token = None
        requested_limit = min(max(limit, 1), 50)
        target_count = offset + requested_limit
        max_products_to_scan = min(250, max(100, target_count * 4))
        page_size = 50
        product_offset = 0
        scanned_products = 0
        seen_product_ids = set()
        offers_by_id: Dict[str, Dict[str, Any]] = {}
        semaphore = asyncio.Semaphore(5)

        async def fetch_listings(product: Dict[str, Any]):
            product_id = product.get("id")
            if not product_id:
                logger.warning("MELI product search result did not include an id")
                return product, []
            async with semaphore:
                try:
                    response = await self._get(
                        f"/products/{product_id}/items",
                        params={
                            "site_id": settings.MELI_SITE_ID,
                            "limit": requested_limit,
                        },
                        token=token,
                    )
                except httpx.HTTPStatusError as exc:
                    if exc.response.status_code == 404:
                        logger.info("MELI product %s has no accessible listings", product_id)
                        return product, []
                    raise
            return product, response.get("results", [])

        logger.info("MELI search: q=%r offset=%d limit=%d", query, offset, requested_limit)
        while (
            scanned_products < max_products_to_scan
            and len(offers_by_id) < target_count
        ):
            products = await self._get(
                "/products/search",
                params={
                    "site_id": settings.MELI_SITE_ID,
                    "q": query,
                    "offset": product_offset,
                    "limit": min(page_size, max_products_to_scan - scanned_products),
                    "status": "active",
                },
                token=token,
            )
            page_products = products.get("results", [])
            if not page_products:
                break

            page_ids = {
                product.get("id")
                for product in page_products
                if product.get("id")
            }
            if page_ids and page_ids.issubset(seen_product_ids):
                logger.warning("MELI product search repeated a page at offset %d", product_offset)
                break
            new_products = [
                product
                for product in page_products
                if (not product.get("id") or product.get("id") not in seen_product_ids)
                and is_relevant_product(product.get("name"))
            ]
            seen_product_ids.update(page_ids)

            product_listings = await asyncio.gather(
                *(fetch_listings(product) for product in new_products)
            )
            for product, listings in product_listings:
                pictures = product.get("pictures") or []
                picture = next(
                    (image for image in pictures if image.get("url")),
                    {},
                )
                product_id = product.get("id")
                for listing in listings:
                    item_id = listing.get("item_id")
                    price = listing.get("price")
                    if not item_id or price is None:
                        continue
                    if category and listing.get("category_id") != category:
                        continue
                    if min_price is not None and price < min_price:
                        continue
                    if max_price is not None and price > max_price:
                        continue
                    if condition in ("new", "used") and listing.get("condition") != condition:
                        continue

                    offers_by_id[item_id] = {
                        **listing,
                        "id": item_id,
                        "title": product.get("name"),
                        "permalink": f"https://www.mercadolivre.com.br/p/{product_id}",
                        "thumbnail": picture.get("url", ""),
                        "seller": {"id": listing.get("seller_id")},
                        "attributes": product.get("attributes") or [],
                    }

            scanned_products += len(page_products)
            product_offset += len(page_products)
            product_total = (products.get("paging") or {}).get("total")
            if product_total is not None and product_offset >= product_total:
                break

        offers = list(offers_by_id.values())
        if sort == "price_asc":
            offers.sort(key=lambda offer: offer["price"])
        elif sort == "price_desc":
            offers.sort(key=lambda offer: offer["price"], reverse=True)

        return {
            "results": offers[offset:target_count],
            "paging": {
                "total": len(offers),
                "offset": offset,
                "limit": requested_limit,
            },
        }

    async def get_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        try:
            return await self._get(f"/items/{item_id}")
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                return None
            raise

    async def get_items_batch(self, item_ids: List[str]) -> List[Dict[str, Any]]:
        if not item_ids:
            return []
        results = []
        for chunk in [item_ids[i:i + 20] for i in range(0, len(item_ids), 20)]:
            token = await self._get_app_token()
            data = await self._get("/items", params={"ids": ",".join(chunk)}, token=token)
            if isinstance(data, list):
                for item in data:
                    if item.get("code") == 200 and item.get("body"):
                        results.append(item["body"])
        return results

    async def get_categories(self) -> List[Dict[str, Any]]:
        data = await self._get(f"/sites/{settings.MELI_SITE_ID}/categories")
        return data if isinstance(data, list) else []

    @staticmethod
    def normalise_result(raw: Dict[str, Any]) -> MeliOffer:
        shipping = raw.get("shipping") or {}
        seller = raw.get("seller") or {}
        seller_rep = (seller.get("seller_reputation") or {}).get("level_id")
        brand = None
        model = None
        for attr in raw.get("attributes") or []:
            aid = attr.get("id", "")
            val = attr.get("value_name")
            if aid == "BRAND" and val:
                brand = val
            elif aid in ("MODEL", "ALPHANUMERIC_MODEL") and val:
                model = val
        return MeliOffer(
            external_id=raw.get("id"),
            title=raw.get("title"),
            brand=brand,
            model=model,
            price=raw.get("price"),
            original_price=raw.get("original_price"),
            currency=raw.get("currency_id", "BRL"),
            url=raw.get("permalink"),
            thumbnail=raw.get("thumbnail"),
            category_id=raw.get("category_id"),
            condition=raw.get("condition", "new"),
            available_quantity=raw.get("available_quantity"),
            free_shipping=shipping.get("free_shipping", False),
            seller_id=str(seller.get("id")) if seller.get("id") else None,
            seller_nickname=seller.get("nickname"),
            seller_reputation=seller_rep,
        )

    @classmethod
    def normalise_results(cls, raw_results: List[Dict[str, Any]]) -> List[MeliOffer]:
        return [cls.normalise_result(r) for r in raw_results]
