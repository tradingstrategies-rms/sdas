"""
Scheduler route.
Called by Firebase / Google Cloud Scheduler at 7:15 PM SGT on weekdays.
Protect with a shared secret header in production.
"""
from fastapi import APIRouter, Header, HTTPException, BackgroundTasks
from app.services.screener import screener_service
from app.services.email_service import email_service
from app.core.config import settings
import os

router = APIRouter()
_SCHEDULER_SECRET = os.getenv("SCHEDULER_SECRET", "change-me-in-production")


@router.post("/trigger")
async def scheduler_trigger(
    background_tasks: BackgroundTasks,
    x_scheduler_secret: str = Header(default=""),
):
    if x_scheduler_secret != _SCHEDULER_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")

    result = screener_service.run()
    background_tasks.add_task(email_service.send_daily_signals, result)

    return {
        "triggered": True,
        "date": result["date"],
        "buyNow": result["buyNow"],
        "watchlist": result["watchlist"],
    }
