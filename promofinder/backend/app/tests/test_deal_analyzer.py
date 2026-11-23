"""Tests for DealAnalyzer — pure logic, no DB required."""
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from app.services.deal_analyzer import DealAnalyzer, DealClassification


def _make_offer(current_price, original_price=None, hours_ago=1):
    offer = MagicMock()
    offer.current_price = Decimal(str(current_price))
    offer.original_price = Decimal(str(original_price)) if original_price else None
    offer.last_checked_at = datetime.now(timezone.utc) - timedelta(hours=hours_ago)
    return offer


def _make_history(prices):
    entries = []
    base = datetime.now(timezone.utc) - timedelta(days=len(prices))
    for i, price in enumerate(prices):
        h = MagicMock()
        h.price = Decimal(str(price))
        h.recorded_at = base + timedelta(days=i)
        entries.append(h)
    return entries


def test_insufficient_history_no_discount():
    analyzer = DealAnalyzer()
    offer = _make_offer(100.0)
    history = _make_history([100.0, 105.0])  # only 2 points
    result = analyzer.analyze(offer, history)
    assert result["deal_classification"] == DealClassification.INSUFFICIENT_HISTORY


def test_insufficient_history_with_seller_discount():
    analyzer = DealAnalyzer()
    offer = _make_offer(90.0, original_price=100.0)
    history = _make_history([95.0])  # only 1 point
    result = analyzer.analyze(offer, history)
    assert result["deal_classification"] == DealClassification.POTENTIAL_DEAL


def test_price_below_history():
    analyzer = DealAnalyzer()
    offer = _make_offer(80.0)
    # 5 points, all above current price
    history = _make_history([100.0, 105.0, 110.0, 100.0, 108.0])
    result = analyzer.analyze(offer, history)
    assert result["deal_classification"] == DealClassification.PRICE_BELOW_HISTORY
    assert result["discount_percent"] is not None
    assert result["discount_percent"] > 0


def test_price_drop_detected():
    analyzer = DealAnalyzer()
    # current=80, history has values both above and below 80,
    # but median (~92) is >5% above current, and current is NOT below all history points
    offer = _make_offer(80.0)
    history = _make_history([70.0, 90.0, 95.0, 100.0, 90.0])
    result = analyzer.analyze(offer, history)
    # historical_min = min(70, 90, 95, 100) = 70; current=80 > 70, so NOT price_below_history
    # median of [70,90,90,95,100] = 90; drop = (90-80)/90 = 11.1% >= 5%, so PRICE_DROP_DETECTED
    assert result["deal_classification"] == DealClassification.PRICE_DROP_DETECTED


def test_regular_price():
    analyzer = DealAnalyzer()
    offer = _make_offer(100.0)
    history = _make_history([99.0, 101.0, 100.0, 98.0, 102.0])
    result = analyzer.analyze(offer, history)
    assert result["deal_classification"] == DealClassification.REGULAR_PRICE


def test_outdated_data():
    analyzer = DealAnalyzer()
    offer = _make_offer(100.0, hours_ago=73)  # > 72 hours
    history = _make_history([100.0, 101.0, 99.0])
    result = analyzer.analyze(offer, history)
    assert result["deal_classification"] == DealClassification.OUTDATED_DATA


def test_result_keys():
    analyzer = DealAnalyzer()
    offer = _make_offer(100.0)
    history = _make_history([105.0, 110.0, 108.0])
    result = analyzer.analyze(offer, history)
    required_keys = {"deal_classification", "discount_percent", "min_price_observed", "history_points", "price_trend"}
    assert required_keys.issubset(result.keys())


def test_price_trend_down():
    analyzer = DealAnalyzer()
    offer = _make_offer(90.0)
    history = _make_history([110.0, 105.0, 100.0, 95.0, 90.0])
    result = analyzer.analyze(offer, history)
    assert result["price_trend"] == "down"


def test_price_trend_up():
    analyzer = DealAnalyzer()
    offer = _make_offer(110.0)
    history = _make_history([90.0, 95.0, 100.0, 105.0, 110.0])
    result = analyzer.analyze(offer, history)
    assert result["price_trend"] == "up"
