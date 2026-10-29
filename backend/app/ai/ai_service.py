"""
AIService — pluggable AI integration.
Providers: openai | watsonx | disabled
Set AI_PROVIDER in .env. App works fully without AI configured.
"""

import json
import logging
from typing import Any, Dict, List, Optional

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """You are TechDeals AI, an intelligent assistant for finding technology deals in Brazil.

CRITICAL RULES:
1. NEVER invent products, prices, URLs, specifications, discounts, or availability.
2. All answers must be grounded exclusively in the product data provided.
3. If no data is available, say so — do not speculate.
4. Respond in Brazilian Portuguese unless the user writes in another language.
5. When extracting search filters, return valid JSON only.
6. Be objective, concise and helpful.
"""


class AIServiceUnavailable(Exception):
    pass


class AIService:
    def __init__(self):
        self.provider = settings.AI_PROVIDER.lower()
        self._available = self.provider != "disabled"

    @property
    def is_available(self) -> bool:
        return self._available

    async def interpret_search(self, user_query: str) -> Dict[str, Any]:
        if not self.is_available:
            return self._fallback_filters(user_query)
        prompt = f"""Extract structured search filters from this query.

Query: "{user_query}"

Return ONLY valid JSON with this exact schema:
{{
  "search_term": "main product keywords",
  "category": "category name or null",
  "min_price": number_or_null,
  "max_price": number_or_null,
  "condition": "new" or "used" or null,
  "sort": "relevance" or "price_asc" or "price_desc",
  "intent_summary": "brief description of what the user wants"
}}

Prices are in Brazilian Reais (BRL). Do not invent information."""
        try:
            response = await self._complete(prompt, temperature=0.1, max_tokens=400)
            return self._parse_json(response, self._fallback_filters(user_query))
        except AIServiceUnavailable:
            return self._fallback_filters(user_query)

    async def recommend(self, user_context: str, products_data: List[Dict]) -> Dict[str, Any]:
        if not self.is_available:
            return {
                "ai_available": False,
                "message": "AI recommendations not configured. Set AI_PROVIDER in environment.",
                "recommendations": [],
            }
        sanitised = self._sanitise_products(products_data)
        context_json = json.dumps(sanitised, ensure_ascii=False, indent=2)
        prompt = f"""User is looking for: "{user_context}"

Available products (real data from Mercado Livre):
{context_json}

Provide:
1. Top 3 recommendations with reasons (reference names from the list)
2. Brief comparison of best options
3. Important considerations for the buyer

IMPORTANT: Only reference products from the list. Do not invent prices, specs or URLs."""
        try:
            response = await self._complete(prompt, temperature=0.3, max_tokens=1000)
            return {"ai_available": True, "analysis": response, "products_analyzed": len(sanitised)}
        except AIServiceUnavailable as exc:
            return {"ai_available": False, "message": str(exc)}

    async def analyze_deal(self, offer_data: Dict, history_data: List[Dict], deal_analysis: Dict) -> Dict[str, Any]:
        if not self.is_available:
            return {"ai_available": False, "message": "AI analysis not configured."}
        prompt = f"""Analyze this product deal and give a buying recommendation.

PRODUCT OFFER:
{json.dumps(offer_data, ensure_ascii=False, indent=2)}

PRICE HISTORY (most recent first):
{json.dumps(history_data[:10], ensure_ascii=False, indent=2)}

SYSTEM ANALYSIS:
{json.dumps(deal_analysis, ensure_ascii=False, indent=2)}

Based ONLY on the data above:
1. Is this a good time to buy? (yes/no/maybe with reason)
2. Price assessment based on history?
3. One sentence buying recommendation

Do not invent data. If history is insufficient, say so."""
        try:
            response = await self._complete(prompt, temperature=0.2, max_tokens=500)
            return {"ai_available": True, "analysis": response}
        except AIServiceUnavailable as exc:
            return {"ai_available": False, "message": str(exc)}

    async def _complete(self, prompt: str, temperature: float = 0.2, max_tokens: int = 500) -> str:
        if self.provider == "openai":
            return await self._openai_complete(prompt, temperature, max_tokens)
        if self.provider == "watsonx":
            return await self._watsonx_complete(prompt, temperature, max_tokens)
        raise AIServiceUnavailable("AI provider not configured")

    async def _openai_complete(self, prompt: str, temperature: float, max_tokens: int) -> str:
        try:
            import openai
            client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=20,
            )
            return response.choices[0].message.content or ""
        except Exception as exc:
            logger.error("OpenAI error: %s", exc)
            raise AIServiceUnavailable(str(exc)) from exc

    async def _watsonx_complete(self, prompt: str, temperature: float, max_tokens: int) -> str:
        if not settings.WATSONX_API_KEY or not settings.WATSONX_PROJECT_ID:
            raise AIServiceUnavailable("watsonx credentials not configured")
        iam_token = await self._watsonx_iam_token()
        full_prompt = f"{_SYSTEM_PROMPT}\n\nUser: {prompt}\n\nAssistant:"
        url = f"{settings.WATSONX_URL}/ml/v1/text/generation"
        payload = {
            "model_id": settings.WATSONX_MODEL_ID,
            "input": full_prompt,
            "parameters": {
                "decoding_method": "sample",
                "temperature": temperature,
                "max_new_tokens": max_tokens,
                "repetition_penalty": 1.1,
            },
            "project_id": settings.WATSONX_PROJECT_ID,
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                url, json=payload,
                headers={"Authorization": f"Bearer {iam_token}", "Content-Type": "application/json"},
                params={"version": "2023-05-29"},
            )
        resp.raise_for_status()
        return resp.json()["results"][0]["generated_text"].strip()

    async def _watsonx_iam_token(self) -> str:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                "https://iam.cloud.ibm.com/identity/token",
                data={"grant_type": "urn:ibm:params:oauth:grant-type:apikey", "apikey": settings.WATSONX_API_KEY},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
        resp.raise_for_status()
        return resp.json()["access_token"]

    @staticmethod
    def _fallback_filters(query: str) -> Dict:
        import re
        filters: Dict = {
            "search_term": query, "category": None, "min_price": None,
            "max_price": None, "condition": None, "sort": "relevance", "intent_summary": query,
        }
        price_match = re.search(r"[Rr]\$\s*([\d.,]+)", query)
        if price_match:
            raw = price_match.group(1).replace(".", "").replace(",", ".")
            try:
                filters["max_price"] = float(raw)
            except ValueError:
                pass
        return filters

    @staticmethod
    def _sanitise_products(products: List[Dict]) -> List[Dict]:
        safe_fields = {
            "name", "brand", "model", "current_price", "original_price",
            "currency", "condition", "deal_classification", "discount_percent",
            "min_price_observed", "free_shipping", "availability_status",
        }
        return [{k: v for k, v in p.items() if k in safe_fields} for p in products]

    @staticmethod
    def _parse_json(text: str, fallback: Dict) -> Dict:
        import re
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        return fallback
