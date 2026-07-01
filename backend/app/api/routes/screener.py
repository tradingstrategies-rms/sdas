"""Screener route — trigger a manual run."""

from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.services.screener import screener_service
from app.services.email_service import email_service
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/run")
async def run_screener(background_tasks: BackgroundTasks, send_email: bool = True):
    """
    Trigger an immediate screening run.
    send_email=true (default) also dispatches the daily email.
    """
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
        }
    except Exception as e:
        logger.error("Screener run failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
