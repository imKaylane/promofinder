"""
DealAnalyzer — classifies an offer based on its price history using only
deterministic, mathematical criteria.  No AI, no external calls.

Pass offer + history objects in, get a classification dict out.

Classification rules (applied in order):
  1. OUTDATED_DATA          — last_checked_at is older than OUTDATED_HOURS
  2. INSUFFICIENT_HISTORY   — fewer than MIN_HISTORY_POINTS records
     (upgraded to POTENTIAL_DEAL when seller discount >= 5 %)
  3. PRICE_BELOW_HISTORY     — current price < minimum of all previous records
  4. PRICE_DROP_DETECTED     — current price >= 5 % below the median of history
  5. POTENTIAL_DEAL          — seller-stated original_price gives >= 10 % discount
  6. REGULAR_PRICE           — none of the above
"""

from datetime import datetime, timezone
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


# Tuning constants
MIN_HISTORY_POINTS: int = 3       # minimum records for full analysis
OUTDATED_HOURS: int = 72          # hours before data is considered stale
MIN_DISCOUNT_PCT: Decimal = Decimal("5")   # minimum seller discount for POTENTIAL_DEAL (low bar)
MIN_SELLER_DISCOUNT_PCT: Decimal = Decimal("10")  # minimum seller discount for POTENTIAL_DEAL (full bar)
MIN_MEDIAN_DROP_PCT: Decimal = Decimal("5")  # minimum drop vs median for PRICE_DROP_DETECTED


class DealAnalyzer:
    """
    Stateless analyzer — call :meth:`analyze` with an offer ORM object and
    its price-history list.  Returns a plain dict.
    """

    def analyze(self, offer, history: list) -> dict:
        """
        Evaluate *offer* against *history* and return a classification dict.

        Parameters
        ----------
        offer:
            ORM Offer object.  Must expose ``current_price``, ``original_price``
            and ``last_checked_at``.
        history:
            List of ORM PriceHistory objects, each with ``price`` and
            ``recorded_at`` attributes.  Order is irrelevant.

        Returns
        -------
        dict with keys:
            deal_classification, discount_percent, min_price_observed,
            history_points, price_trend
        """
        current = Decimal(str(offer.current_price))
        original = Decimal(str(offer.original_price)) if offer.original_price else None
        now = datetime.now(timezone.utc)

        last_checked = offer.last_checked_at
        if last_checked.tzinfo is None:
            last_checked = last_checked.replace(tzinfo=timezone.utc)

        # Rule 1 — stale data
        hours_stale = (now - last_checked).total_seconds() / 3600
        if hours_stale > OUTDATED_HOURS:
            return self._result(DealClassification.OUTDATED_DATA, None, None, len(history), None)

        prices = sorted([Decimal(str(h.price)) for h in history])
        history_points = len(prices)

        # Seller-stated discount (percentage vs original_price)
        seller_discount: Optional[Decimal] = None
        if original and original > current and original > 0:
            seller_discount = _pct((original - current) / original)

        min_price = prices[0] if prices else None
        trend = self._compute_trend(history)

        # Rule 2 — not enough history
        if history_points < MIN_HISTORY_POINTS:
            classification = DealClassification.INSUFFICIENT_HISTORY
            if seller_discount and seller_discount >= MIN_DISCOUNT_PCT:
                classification = DealClassification.POTENTIAL_DEAL
            return self._result(classification, seller_discount, min_price, history_points, trend)

        # Rule 3 — price is the new all-time-low
        # Compare current against the minimum of all *previous* records
        # (exclude the latest price snapshot from the lower bound so we detect
        # a fresh drop rather than just confirming the current price).
        prev_prices = prices[:-1] if len(prices) > 1 else prices
        historical_min = min(prev_prices)
        if current < historical_min:
            discount = _pct((historical_min - current) / historical_min)
            return self._result(DealClassification.PRICE_BELOW_HISTORY, discount, min_price, history_points, trend)

        # Rule 4 — significant drop vs the median of the history window
        median = _median(prices)
        if median and median > 0:
            drop_pct = _pct((median - current) / median)
            if drop_pct >= MIN_MEDIAN_DROP_PCT:
                return self._result(DealClassification.PRICE_DROP_DETECTED, drop_pct, min_price, history_points, trend)

        # Rule 5 — seller-advertised discount is substantial
        if seller_discount and seller_discount >= MIN_SELLER_DISCOUNT_PCT:
            return self._result(DealClassification.POTENTIAL_DEAL, seller_discount, min_price, history_points, trend)

        # Rule 6 — regular price
        return self._result(DealClassification.REGULAR_PRICE, seller_discount, min_price, history_points, trend)

    # ─── Helpers ────────────────────────────────────────────────────────────

    @staticmethod
    def _result(
        classification: DealClassification,
        discount_percent: Optional[Decimal],
        min_price_observed: Optional[Decimal],
        history_points: int,
        price_trend: Optional[str],
    ) -> dict:
        return {
            "deal_classification": classification,
            "discount_percent": discount_percent,
            "min_price_observed": min_price_observed,
            "history_points": history_points,
            "price_trend": price_trend,
        }

    @staticmethod
    def _compute_trend(history: list) -> Optional[str]:
        """
        Return ``"down"``, ``"up"``, or ``"stable"`` by comparing the two most
        recent price-history records.  Returns ``None`` when fewer than 2 exist.
        """
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


# ─── Pure functions (module-level for testability) ───────────────────────────

def _pct(ratio: Decimal) -> Decimal:
    """Convert a ratio (0–1) to a percentage rounded to 2 decimal places."""
    return (ratio * 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _median(prices: List[Decimal]) -> Optional[Decimal]:
    """Return the median of a sorted list of Decimal prices."""
    if not prices:
        return None
    s = sorted(prices)
    n = len(s)
    mid = n // 2
    return (s[mid - 1] + s[mid]) / 2 if n % 2 == 0 else s[mid]
