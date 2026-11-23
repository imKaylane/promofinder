from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import httpx

from app.ai.ai_service import AIService, AIServiceUnavailable


@pytest.mark.asyncio
async def test_gemini_complete_uses_google_api_key_header():
    response = MagicMock()
    response.raise_for_status = MagicMock()
    response.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": "Resposta"}, {"text": " Gemini"}]}}]
    }
    http = AsyncMock()
    http.post.return_value = response
    http_context = MagicMock()
    http_context.__aenter__ = AsyncMock(return_value=http)
    http_context.__aexit__ = AsyncMock(return_value=None)

    with patch("app.ai.ai_service.settings.AI_PROVIDER", "gemini"), \
            patch("app.ai.ai_service.settings.GEMINI_API_KEY", "test-key"), \
            patch("app.ai.ai_service.settings.GEMINI_MODEL", "gemini-test"), \
            patch("app.ai.ai_service.httpx.AsyncClient", return_value=http_context):
        result = await AIService()._complete("prompt", temperature=0.1, max_tokens=50)

    assert result == "Resposta Gemini"
    http.post.assert_awaited_once()
    args = http.post.await_args
    assert args.args[0].endswith("/models/gemini-test:generateContent")
    assert args.kwargs["headers"] == {"x-goog-api-key": "test-key"}
    assert args.kwargs["json"]["contents"][0]["parts"][0]["text"] == "prompt"


@pytest.mark.asyncio
async def test_gemini_http_errors_are_reported_as_unavailable():
    request = httpx.Request("POST", "https://generativelanguage.googleapis.com")
    response = httpx.Response(429, request=request)
    http = AsyncMock()
    http.post.side_effect = httpx.HTTPStatusError("rate limited", request=request, response=response)
    http_context = MagicMock()
    http_context.__aenter__ = AsyncMock(return_value=http)
    http_context.__aexit__ = AsyncMock(return_value=None)

    with patch("app.ai.ai_service.settings.AI_PROVIDER", "gemini"), \
            patch("app.ai.ai_service.settings.GEMINI_API_KEY", "test-key"), \
            patch("app.ai.ai_service.httpx.AsyncClient", return_value=http_context):
        with pytest.raises(AIServiceUnavailable, match="HTTP 429"):
            await AIService()._complete("prompt")
