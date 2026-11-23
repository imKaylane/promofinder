from unittest.mock import AsyncMock, MagicMock, patch
from urllib.parse import parse_qs, urlparse

import pytest

from app.integrations.mercadolivre_oauth import MercadoLivreOAuth


class FakeRedis:
    def __init__(self, *, state="1"):
        self.state = state
        self.set = AsyncMock()
        self.getdel = AsyncMock(return_value=state)
        self.exists = AsyncMock(return_value=1)
        self.aclose = AsyncMock()


@pytest.mark.asyncio
async def test_create_authorization_url_stores_one_time_state():
    redis = FakeRedis()
    with patch("app.integrations.mercadolivre_oauth.Redis.from_url", return_value=redis), \
            patch("app.integrations.mercadolivre_oauth.settings.MELI_CLIENT_ID", "client-id"), \
            patch("app.integrations.mercadolivre_oauth.settings.MELI_REDIRECT_URI", "https://promofinder567.app/auth/mercadolivre/callback"):
        url = await MercadoLivreOAuth().create_authorization_url()

    query = parse_qs(urlparse(url).query)
    assert url.startswith("https://auth.mercadolivre.com.br/authorization?")
    assert query["client_id"] == ["client-id"]
    assert query["redirect_uri"] == ["https://promofinder567.app/auth/mercadolivre/callback"]
    assert query["state"][0]
    redis.set.assert_awaited_once()
    assert redis.set.await_args.kwargs["ex"] == 600


@pytest.mark.asyncio
async def test_exchange_code_consumes_state_and_stores_tokens():
    redis = FakeRedis()
    token_response = MagicMock(status_code=200)
    token_response.json.return_value = {
        "access_token": "access-token",
        "refresh_token": "refresh-token",
        "expires_in": 3600,
    }
    http = AsyncMock()
    http.post.return_value = token_response
    http_context = MagicMock()
    http_context.__aenter__ = AsyncMock(return_value=http)
    http_context.__aexit__ = AsyncMock(return_value=None)

    with patch("app.integrations.mercadolivre_oauth.Redis.from_url", return_value=redis), \
            patch("app.integrations.mercadolivre_oauth.httpx.AsyncClient", return_value=http_context), \
            patch("app.integrations.mercadolivre_oauth.settings.MELI_CLIENT_ID", "client-id"), \
            patch("app.integrations.mercadolivre_oauth.settings.MELI_CLIENT_SECRET", "client-secret"), \
            patch("app.integrations.mercadolivre_oauth.settings.MELI_REDIRECT_URI", "https://promofinder567.app/auth/mercadolivre/callback"):
        await MercadoLivreOAuth().exchange_code("auth-code", "state")

    redis.getdel.assert_awaited_once_with("mercadolivre:oauth:state:state")
    redis.set.assert_awaited_once()
    token_request = http.post.await_args.kwargs["data"]
    assert token_request["code"] == "auth-code"
    assert token_request["redirect_uri"] == "https://promofinder567.app/auth/mercadolivre/callback"


@pytest.mark.asyncio
async def test_exchange_rejects_replayed_or_unknown_state():
    redis = FakeRedis(state=None)
    with patch("app.integrations.mercadolivre_oauth.Redis.from_url", return_value=redis), \
            patch("app.integrations.mercadolivre_oauth.settings.MELI_CLIENT_ID", "client-id"), \
            patch("app.integrations.mercadolivre_oauth.settings.MELI_CLIENT_SECRET", "client-secret"):
        with pytest.raises(ValueError, match="invalid or expired"):
            await MercadoLivreOAuth().exchange_code("auth-code", "bad-state")
