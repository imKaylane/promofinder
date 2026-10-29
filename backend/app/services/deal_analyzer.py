"""
DealAnalyzer — evaluates an offer + its price history and returns a classification.
Pure logic, no DB calls. Pass data in, get classification dict out.
"""

from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from typing import List, Optional


class DealClassification(str, Enum):
    PRICE_BELOW_HISTORY = "price_below_history"
    POTENTIAL_DEAL = "potential_deal"
    PRICE_DROP_DETECTED = "price_drop_detected"
    REGULAR_PRICE = "regular_price"
    INSUFFICIENT_HISTORY = "insufficient_history"
    OUTDATED_DATA = "outdated_data"


MIN_HISTORY_POINTS = 3
OUTDATED_HOURS = 72


class DealAnalyzer:

    def analyze(self, offer, history: list) -> dict:
        from datetime import datetime, timezone, timedelta

        current = Decimal(str(offer.current_price))
        original = Decimal(str(offer.original_price)) if offer.original_price else None
        now = datetime.now(timezone.utc)
        last_checked = offer.last_checked_at
        if last_checked.tzinfo is None:
            last_checked = last_checked.replace(tzinfo=timezone.utc)

        hours_ago = (now - last_checked).total_seconds() / 3600
        if hours_ago > OUTDATED_HOURS:
            return self._result(DealClassification.OUTDATED_DATA, None, None, len(history), None)

        prices = sorted([Decimal(str(h.price)) for h in history], key=float)
        history_points = len(prices)

        seller_discount = None
        if original and original > current and original > 0:
            seller_discount = ((original - current) / original * 100).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )

        min_price = min(prices) if prices else None
        trend = self._compute_trend(history)

        if history_points < MIN_HISTORY_POINTS:
            classification = DealClassification.INSUFFICIENT_HISTORY
            if seller_discount and seller_discount >= Decimal("5"):
                classification = DealClassification.POTENTIAL_DEAL
            return self._result(classification, seller_discount, min_price, history_points, trend)

        history_excluding_last = prices[:-1] if len(prices) > 1 else prices
        historical_min = min(history_excluding_last) if history_excluding_last else None

        if historical_min and current < historical_min:
            discount = ((historical_min - current) / historical_min * 100).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            return self._result(DealClassification.PRICE_BELOW_HISTORY, discount, min_price, history_points, trend)

        median = self._median(prices)
        if median and median > 0:
            drop_pct = ((median - current) / median * 100).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            if drop_pct >= Decimal("5"):
                return self._result(DealClassification.PRICE_DROP_DETECTED, drop_pct, min_price, history_points, trend)

        if seller_discount and seller_discount >= Decimal("10"):
            return self._result(DealClassification.POTENTIAL_DEAL, seller_discount, min_price, history_points, trend)

        return self._result(DealClassification.REGULAR_PRICE, seller_discount, min_price, history_points, trend)

    @staticmethod
    def _result(classification, discount_percent, min_price, history_points, trend) -> dict:
        return {
            "deal_classification": classification,
            "discount_percent": discount_percent,
            "min_price_observed": min_price,
            "history_points": history_points,
            "price_trend": trend,
        }

    @staticmethod
    def _median(prices: List[Decimal]) -> Optional[Decimal]:
        if not prices:
            return None
        s = sorted(prices)
        n = len(s)
        mid = n // 2
        return (s[mid - 1] + s[mid]) / 2 if n % 2 == 0 else s[mid]

    @staticmethod
    def _compute_trend(history: list) -> Optional[str]:
        if len(history) < 2:
            return None
        sorted_h = sorted(history, key=lambda h: h.recorded_at)
        last = Decimal(str(sorted_h[-1].price))
        prev = Decimal(str(sorted_h[-2].price))
        if last < prev:
            return "down"
        if last > prev:
            return "up"
        return "stable"
