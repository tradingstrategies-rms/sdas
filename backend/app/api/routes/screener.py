"""Screener route — trigger a manual run."""

from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.services.screener import screener_service
from app.services.email_service import email_service
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/run")
async def run_screener(background_tasks: BackgroundTasks, send_email: bool = True):
    try:
        result = screener_service.run()
        if send_email:
            background_tasks.add_task(email_service.send_daily_signals, result)
        return {
            "success": True,
            "date": result["date"],
            "signalsGenerated": result["signalsGenerated"],
            "buyNow": result["buyNow"],
            "watchlist": result["watchlist"],
            "overvalued": result["overvalued"],
            "emailQueued": send_email,
            "results": result["results"],
        }
    except Exception as e:
        logger.error("Screener run failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-email")
async def test_email():
    """Send a test email with fake data to verify the email template."""
    fake_result = {
        "date": "2026-07-07",
        "buyNow": 2,
        "watchlist": 2,
        "overvalued": 2,
        "stiCorrection": 6.5,
        "results": [
            {
                "ticker": "A17U.SI",
                "companyName": "Ascendas REIT",
                "signal": "BUY_NOW",
                "score": 14,
                "yield": 5.8,
                "amount": 750,
                "category": "REIT",
                "market": "SGX",
                "notes": "Trend+4 | Pullback+3 | Dividend+2 | Valuation+0 | RSI+2 | MktCorrection+3",
            },
            {
                "ticker": "D05.SI",
                "companyName": "DBS Group Holdings",
                "signal": "BUY_NOW",
                "score": 13,
                "yield": 5.2,
                "amount": 750,
                "category": "Bank",
                "market": "SGX",
                "notes": "Trend+4 | Pullback+2 | Dividend+2 | Valuation+1 | RSI+1 | MktCorrection+3",
            },
            {
                "ticker": "C38U.SI",
                "companyName": "CapitaLand Integrated Commercial Trust",
                "signal": "WATCHLIST",
                "score": 11,
                "yield": 5.5,
                "amount": 500,
                "category": "REIT",
                "market": "SGX",
                "notes": "Trend+3 | Pullback+2 | Dividend+2 | Valuation+1 | RSI+1 | MktCorrection+2",
            },
            {
                "ticker": "JPM",
                "companyName": "JPMorgan Chase",
                "signal": "WATCHLIST",
                "score": 10,
                "yield": 2.8,
                "amount": 500,
                "category": "Bank",
                "market": "US",
                "notes": "Trend+4 | Pullback+2 | Dividend+1 | Valuation+1 | RSI+1 | MktCorrection+1",
            },
            {
                "ticker": "Z74.SI",
                "companyName": "Singapore Telecommunications",
                "signal": "OVERVALUED",
                "score": 7,
                "yield": 5.1,
                "amount": 0,
                "category": "Equity",
                "market": "SGX",
                "notes": "Score 7 < 9 threshold",
            },
            {
                "ticker": "TSLA",
                "companyName": "Tesla Inc",
                "signal": "OVERVALUED",
                "score": 4,
                "yield": 0.0,
                "amount": 0,
                "category": "Equity",
                "market": "US",
                "notes": "Yield 0.0% < 4.0% minimum",
            },
        ],
    }

    sent = email_service.send_daily_signals(fake_result)
    if sent:
        return {"success": True, "message": "Test email sent — check your inbox"}
    else:
        raise HTTPException(status_code=500, detail="Email failed to send — check SendGrid credentials")