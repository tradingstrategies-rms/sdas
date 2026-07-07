"""
Screener Service — orchestrates the daily screening run.
"""

import logging
from datetime import datetime
from typing import List, Dict, Any

from app.core.config import settings
from app.services.market_data import market_data_service
from app.services.scoring import scoring_engine
from app.repositories.price_repo import price_repo
from app.repositories.signal_repo import signal_repo
from app.repositories.stock_repo import stock_repo

logger = logging.getLogger(__name__)


class ScreenerService:

    def run(self) -> Dict[str, Any]:
        today = datetime.now().strftime("%Y-%m-%d")
        logger.info("=== SDAS Screening Run — %s ===", today)

        sti_correction = market_data_service.get_sti_correction(settings.STI_TICKER)
        logger.info("STI correction from 52w high: %.1f%%", sti_correction)

        all_stocks = stock_repo.get_all_active()
        stocks_meta = {s["ticker"]: s for s in all_stocks}
        tickers = [s["ticker"] for s in all_stocks]

        results: List[Dict] = []

        for ticker in tickers:
            logger.info("Processing %s...", ticker)

            data = market_data_service.get_stock_data(ticker)
            if not data:
                logger.warning("Skipping %s — no data", ticker)
                continue

            meta = stocks_meta.get(ticker, {})
            category = meta.get("category", "Equity")
            company_name = meta.get("companyName", ticker)
            min_yield = meta.get("minYield", settings.MIN_DIVIDEND_YIELD)

            score, signal, amount, notes, _ = scoring_engine.score_stock(
                data=data,
                category=category,
                sti_correction_pct=sti_correction,
                min_yield=min_yield,
            )

            price_repo.upsert(data)

            signal_doc = {
                "date": today,
                "ticker": ticker,
                "score": score,
                "signal": signal,
                "amount": amount,
                "yield": data["dividendYield"],
                "notes": notes,
                "companyName": company_name,
                "category": category,
                "market": meta.get("market", "SGX"),
            }
            signal_repo.upsert(signal_doc)

            results.append(signal_doc)
            logger.info(
                "%s → score=%d signal=%s yield=%.1f%%",
                ticker, score, signal, data["dividendYield"]
            )

        buy_now = [r for r in results if r["signal"] == "BUY_NOW"]
        watchlist = [r for r in results if r["signal"] == "WATCHLIST"]
        overvalued = [r for r in results if r["signal"] == "OVERVALUED"]

        return {
            "date": today,
            "signalsGenerated": len(results),
            "buyNow": len(buy_now),
            "watchlist": len(watchlist),
            "overvalued": len(overvalued),
            "results": results,
            "stiCorrection": sti_correction,
        }


screener_service = ScreenerService()