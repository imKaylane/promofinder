"""
MercadoLivreService — centralised integration with the official MELI API (MLB).
All HTTP calls to api.mercadolibre.com go through this module only.
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import httpx
from tenacity import (
    retry, stop_after_attempt, wait_exponential,
    retry_if_exception_type, before_sleep_log,
)

from app.core.config import settings

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
        retry=retry_if_exception_type(Exception),
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
        token = await self._get_app_token()
        params: Dict[str, Any] = {
            "q": query,
            "offset": offset,
            "limit": min(limit, 50),
        }
        if category:
            params["category"] = category
        if min_price is not None and max_price is not None:
            params["price"] = f"{min_price}-{max_price}"
        elif min_price is not None:
            params["price"] = f"{min_price}-*"
        elif max_price is not None:
            params["price"] = f"*-{max_price}"
        if condition in ("new", "used"):
            params["ITEM_CONDITION"] = "2230284" if condition == "new" else "2230581"
        if sort == "price_asc":
            params["sort"] = "price_asc"
        elif sort == "price_desc":
            params["sort"] = "price_desc"
        logger.info("MELI search: q=%r offset=%d limit=%d", query, offset, limit)
        return await self._get(f"/sites/{settings.MELI_SITE_ID}/search", params=params, token=token)

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
