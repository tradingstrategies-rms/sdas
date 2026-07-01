"""Backtest API route."""
from fastapi import APIRouter, HTTPException
from app.models.schemas import BacktestRequest
from app.services.backtest import backtest_engine
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/run")
def run_backtest(req: BacktestRequest):
    try:
        result = backtest_engine.run(
            start_date=req.startDate,
            end_date=req.endDate,
            monthly_contribution=req.monthlyContribution,
            buy_now_amount=req.buyNowAmount,
            watchlist_amount=req.watchlistAmount,
            initial_cash=req.initialCash,
        )
        return result
    except Exception as e:
        logger.error("Backtest failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
