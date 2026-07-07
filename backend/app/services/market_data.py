"""
Market data service.
Primary: yfinance (works locally)
Fallback: Alpha Vantage API (works from Cloud Run)
"""

import yfinance as yf
import pandas as pd
import numpy as np
import requests
from typing import Optional, Dict, Any
from datetime import datetime
import logging
import os

logger = logging.getLogger(__name__)


def _safe_float(val, default: float = 0.0) -> float:
    try:
        v = float(val)
        return v if not np.isnan(v) else default
    except (TypeError, ValueError):
        return default


def _fix_yield(raw: float) -> float:
    """Yahoo returns yield inconsistently — normalise to percent."""
    if raw > 1:
        return raw        # already percent e.g. 4.84
    return raw * 100      # decimal e.g. 0.0484


class MarketDataService:

    def get_stock_data(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Try yfinance first, fall back to Alpha Vantage."""
        result = self._fetch_yfinance(ticker)
        if result:
            return result
        logger.warning("%s failed yfinance — trying Alpha Vantage", ticker)
        return self._fetch_alpha_vantage(ticker)

    # ── yfinance ──────────────────────────────────────────────────────────────

    def _fetch_yfinance(self, ticker: str) -> Optional[Dict[str, Any]]:
        try:
            tk = yf.Ticker(ticker)
            hist = tk.history(period="1y", interval="1d")

            if hist is None or hist.empty or len(hist) < 50:
                return None

            close = hist["Close"]
            volume = hist["Volume"]

            try:
                info = tk.info or {}
            except Exception:
                info = {}

            price = _safe_float(close.iloc[-1])
            if price <= 0:
                return None

            sma50 = _safe_float(close.rolling(50).mean().iloc[-1])
            sma200 = _safe_float(close.rolling(200).mean().iloc[-1]) if len(close) >= 200 else sma50
            high52 = _safe_float(close.max())
            low52 = _safe_float(close.min())
            drawdown = ((high52 - price) / high52) * 100 if high52 > 0 else 0.0
            rsi14 = self._calc_rsi(close, 14)

            raw_yield = _safe_float(
                info.get("dividendYield") or
                info.get("trailingAnnualDividendYield") or 0
            )
            div_yield = _fix_yield(raw_yield)

            pb = _safe_float(info.get("priceToBook") or 0) or None
            pe = _safe_float(info.get("trailingPE") or 0) or None

            return {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "ticker": ticker,
                "price": round(price, 4),
                "high52": round(high52, 4),
                "low52": round(low52, 4),
                "sma50": round(sma50, 4),
                "sma200": round(sma200, 4),
                "rsi14": round(rsi14, 2),
                "dividendYield": round(div_yield, 2),
                "pbRatio": round(pb, 2) if pb else None,
                "peRatio": round(pe, 2) if pe else None,
                "drawdownPercent": round(drawdown, 2),
                "volume": int(volume.iloc[-1]) if not volume.empty else None,
                "source": "yfinance",
            }

        except Exception as e:
            logger.error("yfinance error for %s: %s", ticker, e)
            return None

    # ── Alpha Vantage ─────────────────────────────────────────────────────────

    def _fetch_alpha_vantage(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Fetch daily OHLCV from Alpha Vantage.
        Free tier: 25 requests/day — enough for daily screener.
        SGX tickers: D05.SI → use as-is, Alpha Vantage supports them.
        """
        try:
            from app.core.config import settings
            api_key = settings.ALPHA_VANTAGE_KEY
            if not api_key:
                logger.warning("No ALPHA_VANTAGE_KEY set — skipping fallback")
                return None

            # Convert SGX tickers for Alpha Vantage format
            av_ticker = ticker.replace(".SI", ".SES")

            url = (
                f"https://www.alphavantage.co/query"
                f"?function=TIME_SERIES_DAILY_ADJUSTED"
                f"&symbol={av_ticker}"
                f"&outputsize=full"
                f"&apikey={api_key}"
            )

            resp = requests.get(url, timeout=30)
            data = resp.json()

            if "Time Series (Daily)" not in data:
                logger.warning("Alpha Vantage no data for %s: %s", ticker, list(data.keys()))
                return None

            ts = data["Time Series (Daily)"]
            dates = sorted(ts.keys(), reverse=True)

            if len(dates) < 50:
                return None

            closes = pd.Series({d: float(ts[d]["4. close"]) for d in dates}).sort_index()
            volumes = pd.Series({d: float(ts[d]["6. volume"]) for d in dates}).sort_index()

            price = closes.iloc[-1]
            high52 = closes.iloc[-252:].max() if len(closes) >= 252 else closes.max()
            low52 = closes.iloc[-252:].min() if len(closes) >= 252 else closes.min()
            sma50 = closes.iloc[-50:].mean()
            sma200 = closes.iloc[-200:].mean() if len(closes) >= 200 else sma50
            drawdown = ((high52 - price) / high52) * 100 if high52 > 0 else 0.0
            rsi14 = self._calc_rsi(closes, 14)

            # Alpha Vantage OVERVIEW for fundamentals
            div_yield = self._fetch_av_yield(av_ticker, api_key)

            return {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "ticker": ticker,
                "price": round(price, 4),
                "high52": round(high52, 4),
                "low52": round(low52, 4),
                "sma50": round(sma50, 4),
                "sma200": round(sma200, 4),
                "rsi14": round(rsi14, 2),
                "dividendYield": round(div_yield, 2),
                "pbRatio": None,
                "peRatio": None,
                "drawdownPercent": round(drawdown, 2),
                "volume": int(volumes.iloc[-1]),
                "source": "alphavantage",
            }

        except Exception as e:
            logger.error("Alpha Vantage error for %s: %s", ticker, e)
            return None

    def _fetch_av_yield(self, ticker: str, api_key: str) -> float:
        try:
            url = (
                f"https://www.alphavantage.co/query"
                f"?function=OVERVIEW"
                f"&symbol={ticker}"
                f"&apikey={api_key}"
            )
            resp = requests.get(url, timeout=15)
            data = resp.json()
            raw = float(data.get("DividendYield") or 0)
            return _fix_yield(raw)
        except Exception:
            return 0.0

    def get_sti_correction(self, sti_ticker: str = "^STI") -> float:
        try:
            tk = yf.Ticker(sti_ticker)
            hist = tk.history(period="1y")
            if hist is None or hist.empty:
                return 0.0
            close = hist["Close"]
            high52 = close.max()
            current = close.iloc[-1]
            return round(((high52 - current) / high52) * 100, 2)
        except Exception as e:
            logger.error("STI fetch error: %s", e)
            return 0.0

    @staticmethod
    def _calc_rsi(series: pd.Series, period: int = 14) -> float:
        try:
            delta = series.diff()
            gain = delta.clip(lower=0)
            loss = -delta.clip(upper=0)
            avg_gain = gain.ewm(alpha=1 / period, min_periods=period).mean()
            avg_loss = loss.ewm(alpha=1 / period, min_periods=period).mean()
            rs = avg_gain / avg_loss.replace(0, np.nan)
            rsi = 100 - (100 / (1 + rs))
            return float(rsi.iloc[-1])
        except Exception:
            return 50.0


market_data_service = MarketDataService()