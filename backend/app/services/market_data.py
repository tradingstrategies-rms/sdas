"""
Market data service.
Downloads price + fundamentals from Yahoo Finance using yfinance.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def _safe_float(val, default: float = 0.0) -> float:
    try:
        v = float(val)
        return v if not np.isnan(v) else default
    except (TypeError, ValueError):
        return default


class MarketDataService:

    def get_stock_data(self, ticker: str) -> Optional[Dict[str, Any]]:
        try:
            tk = yf.Ticker(ticker)

            # Use period instead of start/end dates — more reliable
            hist = tk.history(period="1y", interval="1d")

            if hist is None or hist.empty:
                logger.warning("Empty history for %s", ticker)
                return None

            if len(hist) < 50:
                logger.warning("Insufficient history for %s — only %d rows", ticker, len(hist))
                return None

            close = hist["Close"]
            volume = hist["Volume"]

            # Try to get fundamentals
            try:
                info = tk.info or {}
            except Exception:
                info = {}

            price = _safe_float(close.iloc[-1])
            if price <= 0:
                logger.warning("Zero price for %s", ticker)
                return None

            # Technical indicators
            sma50 = _safe_float(close.rolling(50).mean().iloc[-1])
            sma200 = _safe_float(
                close.rolling(200).mean().iloc[-1]
            ) if len(close) >= 200 else sma50

            high52 = _safe_float(close.max())
            low52 = _safe_float(close.min())
            drawdown = ((high52 - price) / high52) * 100 if high52 > 0 else 0.0
            rsi14 = self._calc_rsi(close, 14)

            # Fundamentals — try multiple field names
	    # Fundamentals — Yahoo Finance returns dividendYield inconsistently
            # Sometimes it's already a percentage (4.84), sometimes a decimal (0.0484)
            # We detect which format and normalise to percentage
            raw_yield = _safe_float(
                info.get("dividendYield") or
                info.get("trailingAnnualDividendYield") or 0
            )
            # If value is greater than 1, it's already in percent form (e.g. 4.84)
            # If value is less than 1, it's in decimal form (e.g. 0.0484)
            if raw_yield > 1:
                div_yield = raw_yield          # already percent — use as-is
            else:
                div_yield = raw_yield * 100    # convert decimal to percent

            pb_ratio = _safe_float(
                info.get("priceToBook") or info.get("pb"), default=0
            ) or None

            pe_ratio = _safe_float(
                info.get("trailingPE") or info.get("pe"), default=0
            ) or None

            today = datetime.now().strftime("%Y-%m-%d")

            return {
                "date": today,
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
        try:
            tk = yf.Ticker(sti_ticker)
            hist = tk.history(period="1y", interval="1d")
            if hist is None or hist.empty:
                return 0.0
            close = hist["Close"]
            high52 = close.max()
            current = close.iloc[-1]
            correction = ((high52 - current) / high52) * 100
            return round(correction, 2)
        except Exception as e:
            logger.error("Error fetching STI: %s", e)
            return 0.0

    @staticmethod
    def _calc_rsi(series: pd.Series, period: int = 14) -> float:
        delta = series.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.ewm(alpha=1 / period, min_periods=period).mean()
        avg_loss = loss.ewm(alpha=1 / period, min_periods=period).mean()
        rs = avg_gain / avg_loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))
        try:
            return float(rsi.iloc[-1])
        except Exception:
            return 50.0


market_data_service = MarketDataService()