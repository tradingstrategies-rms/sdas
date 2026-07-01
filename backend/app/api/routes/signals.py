"""Signals API routes."""
from fastapi import APIRouter
from app.repositories.price_repo import signal_repo

router = APIRouter()


@router.get("/latest")
def get_latest_signals():
    return signal_repo.get_latest()


@router.get("/date/{date}")
def get_signals_by_date(date: str):
    return signal_repo.get_by_date(date)


@router.get("/{ticker}/history")
def get_signal_history(ticker: str, limit: int = 30):
    return signal_repo.get_history(ticker, limit)
