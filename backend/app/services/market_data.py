"""
Market data service.
Downloads price + fundamentals from Yahoo Finance using yfinance.
Falls back gracefully on data gaps.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def _safe_float(val, default: float = 0.0) -> float:
    """Return float or default if None / NaN."""
    try:
        v = float(val)
        return v if not np.isnan(v) else default
    except (TypeError, ValueError):
        return default


class MarketDataService:
    """Fetch OHLCV + fundamentals for a single ticker."""

    LOOKBACK_DAYS = 260  # ~1 year of trading data for SMA200

    def get_stock_data(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Return a dict with all fields needed for DailyPrice + scoring.
        Returns None if data is unavailable.
        """
        try:
            tk = yf.Ticker(ticker)
            end = datetime.today()
            start = end - timedelta(days=self.LOOKBACK_DAYS + 60)

            hist = tk.history(start=start.strftime("%Y-%m-%d"), end=end.strftime("%Y-%m-%d"))
            if hist.empty or len(hist) < 50:
                logger.warning("Insufficient history for %s", ticker)
                return None

            close = hist["Close"]
            volume = hist["Volume"]
            info = tk.info or {}

            price = _safe_float(close.iloc[-1])
            if price <= 0:
                return None

            # ── Technical indicators ───────────────────────────────────────────
            sma50 = _safe_float(close.rolling(50).mean().iloc[-1])
            sma200 = _safe_float(close.rolling(200).mean().iloc[-1]) if len(close) >= 200 else sma50

            high52 = _safe_float(close.rolling(252).max().iloc[-1]) if len(close) >= 252 else _safe_float(close.max())
            low52 = _safe_float(close.rolling(252).min().iloc[-1]) if len(close) >= 252 else _safe_float(close.min())

            drawdown = ((high52 - price) / high52) * 100 if high52 > 0 else 0.0

            rsi14 = self._calc_rsi(close, 14)

            # ── Fundamentals ───────────────────────────────────────────────────
            div_yield = _safe_float(info.get("dividendYield", 0)) * 100      # convert 0.05 → 5.0
            pb_ratio = _safe_float(info.get("priceToBook", None), default=None)
            pe_ratio = _safe_float(info.get("trailingPE", None), default=None)

            return {
                "date": end.strftime("%Y-%m-%d"),
                "ticker": ticker,
                "price": round(price, 4),
                "high52": round(high52, 4),
                "low52": round(low52, 4),
                "sma50": round(sma50, 4),
                "sma200": round(sma200, 4),
                "rsi14": round(rsi14, 2),
                "dividendYield": round(div_yield, 2),
                "pbRatio": round(pb_ratio, 2) if pb_ratio else None,
                "peRatio": round(pe_ratio, 2) if pe_ratio else None,
                "drawdownPercent": round(drawdown, 2),
                "volume": int(volume.iloc[-1]) if not volume.empty else None,
            }

        except Exception as e:
            logger.error("Error fetching data for %s: %s", ticker, e)
            return None

    def get_sti_correction(self, sti_ticker: str = "^STI") -> float:
        """
        Return the current STI correction % from its 52-week high.
        Used for market correction bonus scoring.
        """
        try:
            tk = yf.Ticker(sti_ticker)
            hist = tk.history(period="1y")
            if hist.empty:
                return 0.0
            close = hist["Close"]
            high52 = close.max()
            current = close.iloc[-1]
            correction = ((high52 - current) / high52) * 100
            return round(correction, 2)
        except Exception as e:
            logger.error("Error fetching STI data: %s", e)
            return 0.0

    @staticmethod
    def _calc_rsi(series: pd.Series, period: int = 14) -> float:
        """Wilder RSI."""
        delta = series.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.ewm(alpha=1 / period, min_periods=period).mean()
        avg_loss = loss.ewm(alpha=1 / period, min_periods=period).mean()
        rs = avg_gain / avg_loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))
        return _safe_float(rsi.iloc[-1], default=50.0)


market_data_service = MarketDataService()
