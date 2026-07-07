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

        # Get STI correction for market bonus
        try:
            sti_correction = market_data_service.get_sti_correction(settings.STI_TICKER)
            logger.info("STI correction: %.1f%%", sti_correction)
        except Exception as e:
            logger.warning("STI fetch failed: %s — using 0", e)
            sti_correction = 0.0

        # Load stocks from Firestore
        try:
            all_stocks = stock_repo.get_all_active()
            stocks_meta = {s["ticker"]: s for s in all_stocks}
            tickers = [s["ticker"] for s in all_stocks]
            logger.info("Found %d stocks in Firestore", len(tickers))
        except Exception as e:
            logger.error("Failed to load stocks from Firestore: %s", e)
            tickers = settings.WATCHLIST_TICKERS
            stocks_meta = {}

        if not tickers:
            logger.warning("No tickers found — nothing to screen")
            return {
                "date": today,
                "signalsGenerated": 0,
                "buyNow": 0,
                "watchlist": 0,
                "overvalued": 0,
                "results": [],
                "stiCorrection": sti_correction,
            }

        results: List[Dict] = []
        skipped = 0

        for ticker in tickers:
            logger.info("Processing %s...", ticker)
            try:
                data = market_data_service.get_stock_data(ticker)
                if not data:
                    logger.warning("No data for %s — skipping", ticker)
                    skipped += 1
                    continue

                meta = stocks_meta.get(ticker, {})
                category = meta.get("category", "Equity")
                company_name = meta.get("companyName", ticker)
                min_yield = float(meta.get("minYield", settings.MIN_DIVIDEND_YIELD))

                score, signal, amount, notes, _ = scoring_engine.score_stock(
                    data=data,
                    category=category,
                    sti_correction_pct=sti_correction,
                    min_yield=min_yield,
                )

                try:
                    price_repo.upsert(data)
                except Exception as e:
                    logger.warning("Failed to save price for %s: %s", ticker, e)

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

                try:
                    signal_repo.upsert(signal_doc)
                except Exception as e:
                    logger.warning("Failed to save signal for %s: %s", ticker, e)

                results.append(signal_doc)
                logger.info(
                    "%s → score=%d signal=%s yield=%.1f%%",
                    ticker, score, signal, data["dividendYield"]
                )

            except Exception as e:
                logger.error("Error processing %s: %s", ticker, e)
                skipped += 1
                continue

        logger.info(
            "Screening complete: %d processed, %d skipped",
            len(results), skipped
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