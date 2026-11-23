"""OAuth authorization and token storage for Mercado Livre."""

import json
import logging
import secrets
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import httpx
from redis.asyncio import Redis

from app.core.config import settings

logger = logging.getLogger(__name__)

MELI_AUTHORIZATION_URL = "https://auth.mercadolivre.com.br/authorization"
MELI_TOKEN_URL = "https://api.mercadolibre.com/oauth/token"
STATE_TTL_SECONDS = 600
TOKEN_KEY = "mercadolivre:oauth:token"
STATE_KEY_PREFIX = "mercadolivre:oauth:state:"


class MercadoLivreOAuth:
    def _redis(self) -> Redis:
        return Redis.from_url(settings.REDIS_URL, decode_responses=True)

    def _require_credentials(self) -> None:
        if not settings.MELI_CLIENT_ID or not settings.MELI_CLIENT_SECRET:
            raise RuntimeError("Mercado Livre application credentials are not configured.")

    async def create_authorization_url(self) -> str:
        self._require_credentials()
        state = secrets.token_urlsafe(32)
        client = self._redis()
        try:
            await client.set(f"{STATE_KEY_PREFIX}{state}", "1", ex=STATE_TTL_SECONDS)
        finally:
            await client.aclose()
        query = urlencode({
            "response_type": "code",
            "client_id": settings.MELI_CLIENT_ID,
            "redirect_uri": settings.MELI_REDIRECT_URI,
            "state": state,
        })
        return f"{MELI_AUTHORIZATION_URL}?{query}"

    async def exchange_code(self, code: str, state: str) -> None:
        self._require_credentials()
        client = self._redis()
        try:
            valid_state = await client.getdel(f"{STATE_KEY_PREFIX}{state}")
        finally:
            await client.aclose()
        if not valid_state:
            raise ValueError("OAuth state is invalid or expired.")

        async with httpx.AsyncClient(timeout=15.0) as http:
            response = await http.post(
                MELI_TOKEN_URL,
                data={
                    "grant_type": "authorization_code",
                    "client_id": settings.MELI_CLIENT_ID,
                    "client_secret": settings.MELI_CLIENT_SECRET,
                    "code": code,
                    "redirect_uri": settings.MELI_REDIRECT_URI,
                },
            )
        if response.status_code != 200:
            logger.warning("Mercado Livre OAuth code exchange failed with status %d", response.status_code)
            raise RuntimeError("Mercado Livre did not accept the authorization code.")
        await self._store_tokens(response.json())

    async def is_connected(self) -> bool:
        client = self._redis()
        try:
            return bool(await client.exists(TOKEN_KEY))
        finally:
            await client.aclose()

    async def get_access_token(self) -> str | None:
        client = self._redis()
        try:
            saved = await client.get(TOKEN_KEY)
        finally:
            await client.aclose()
        if not saved:
            return None

        tokens = json.loads(saved)
        expires_at = datetime.fromtimestamp(tokens["expires_at"], tz=timezone.utc)
        if expires_at > datetime.now(timezone.utc) + timedelta(seconds=60):
            return tokens["access_token"]

        refresh_token = tokens.get("refresh_token")
        if not refresh_token:
            raise RuntimeError("Mercado Livre authorization has expired; reconnect the account.")
        self._require_credentials()
        async with httpx.AsyncClient(timeout=15.0) as http:
            response = await http.post(
                MELI_TOKEN_URL,
                data={
                    "grant_type": "refresh_token",
                    "client_id": settings.MELI_CLIENT_ID,
                    "client_secret": settings.MELI_CLIENT_SECRET,
                    "refresh_token": refresh_token,
                },
            )
        if response.status_code != 200:
            logger.warning("Mercado Livre OAuth token refresh failed with status %d", response.status_code)
            raise RuntimeError("Mercado Livre authorization expired; reconnect the account.")
        refreshed = response.json()
        if not refreshed.get("refresh_token"):
            refreshed["refresh_token"] = refresh_token
        await self._store_tokens(refreshed)
        return refreshed["access_token"]

    async def _store_tokens(self, tokens: dict) -> None:
        access_token = tokens.get("access_token")
        refresh_token = tokens.get("refresh_token")
        expires_in = tokens.get("expires_in")
        if not access_token or not refresh_token or not isinstance(expires_in, int):
            raise RuntimeError("Mercado Livre returned an incomplete OAuth token response.")

        stored = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_at": int(datetime.now(timezone.utc).timestamp()) + expires_in,
        }
        client = self._redis()
        try:
            await client.set(TOKEN_KEY, json.dumps(stored))
        finally:
            await client.aclose()
