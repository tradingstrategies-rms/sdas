"""
Integration-style tests for the screener pipeline.
These are offline unit tests — no live API calls.
"""

import pytest
from unittest.mock import patch, MagicMock
from app.services.screener import ScreenerService
from app.services.market_data import MarketDataService


class TestMarketDataService:
    """Test the data service helpers (no network calls)."""

    def test_rsi_calculation_normal(self):
        import pandas as pd
        import numpy as np

        svc = MarketDataService()
        # Create a rising series → RSI should be high
        prices = pd.Series([float(i) for i in range(100, 120)])
        rsi = svc._calc_rsi(prices, 14)
        assert rsi > 60  # rising prices = high RSI

    def test_rsi_calculation_falling(self):
        import pandas as pd

        svc = MarketDataService()
        prices = pd.Series([float(i) for i in range(120, 100, -1)])
        rsi = svc._calc_rsi(prices, 14)
        assert rsi < 40  # falling prices = low RSI

    def test_rsi_returns_float(self):
        import pandas as pd

        svc = MarketDataService()
        prices = pd.Series([3.0, 3.1, 2.9, 3.05, 2.95] * 10)
        rsi = svc._calc_rsi(prices, 14)
        assert isinstance(rsi, float)
        assert 0 <= rsi <= 100


class TestScreenerService:
    """Test the screener orchestration (Firestore + Yahoo Finance mocked)."""

    @patch("app.services.screener.market_data_service")
    @patch("app.services.screener.stock_repo")
    @patch("app.services.screener.price_repo")
    @patch("app.services.screener.signal_repo")
    def test_run_produces_signals(self, mock_signal, mock_price, mock_stock, mock_mds):
        # Setup mocks
        mock_stock.get_all_active.return_value = [
            {"ticker": "D05.SI", "companyName": "DBS Group", "category": "Bank"},
        ]
        mock_mds.get_sti_correction.return_value = 3.0
        mock_mds.get_stock_data.return_value = {
            "date": "2024-01-15",
            "ticker": "D05.SI",
            "price": 34.0,
            "high52": 38.0,
            "low52": 30.0,
            "sma50": 33.5,
            "sma200": 32.0,
            "rsi14": 55.0,
            "dividendYield": 5.2,
            "pbRatio": 1.2,
            "peRatio": 9.5,
            "drawdownPercent": 10.5,
            "volume": 5000000,
        }
        mock_price.upsert.return_value = None
        mock_signal.upsert.return_value = None

        svc = ScreenerService()
        result = svc.run()

        assert result["signalsGenerated"] == 1
        assert result["date"] is not None
        total = result["buyNow"] + result["watchlist"] + result["overvalued"]
        assert total == 1

    @patch("app.services.screener.market_data_service")
    @patch("app.services.screener.stock_repo")
    @patch("app.services.screener.price_repo")
    @patch("app.services.screener.signal_repo")
    def test_run_skips_missing_data(self, mock_signal, mock_price, mock_stock, mock_mds):
        mock_stock.get_all_active.return_value = [
            {"ticker": "FAKE.SI", "companyName": "Fake Co", "category": "REIT"},
        ]
        mock_mds.get_sti_correction.return_value = 0.0
        mock_mds.get_stock_data.return_value = None  # Simulate missing data

        svc = ScreenerService()
        result = svc.run()
        assert result["signalsGenerated"] == 0


class TestEmailService:
    """Test HTML email rendering."""

    def test_render_html_no_signals(self):
        from app.services.email_service import _render_html

        html = _render_html({"date": "2024-01-15", "results": [], "stiCorrection": 0})
        assert "Singapore Dividend Screener" in html
        assert "2024-01-15" in html

    def test_render_html_with_buy_now(self):
        from app.services.email_service import _render_html

        result = {
            "date": "2024-01-15",
            "stiCorrection": 0,
            "results": [{
                "ticker": "D05.SI",
                "companyName": "DBS Group",
                "signal": "BUY_NOW",
                "score": 14,
                "yield": 5.2,
                "amount": 750,
                "category": "Bank",
                "notes": "",
            }]
        }
        html = _render_html(result)
        assert "BUY NOW" in html
        assert "DBS Group" in html
        assert "SGD 750" in html

    def test_render_html_sti_crash_warning(self):
        from app.services.email_service import _render_html

        html = _render_html({"date": "2024-01-15", "results": [], "stiCorrection": 22.5})
        assert "MARKET CRASH" in html
        assert "22.5" in html
