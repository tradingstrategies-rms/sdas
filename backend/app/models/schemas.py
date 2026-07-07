"""Pydantic models for SDAS entities."""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import date, datetime


# ── Stock ──────────────────────────────────────────────────────────────────────

class Stock(BaseModel):
    ticker: str
    companyName: str
    sector: str
    category: Literal["Bank", "REIT", "Infrastructure", "Equity"]
    market: str = "SGX"
    currency: str = "SGD"
    targetYield: float
    minYield: float = 4.0
    active: bool = True


class StockCreate(Stock):
    pass


# ── Daily Price ────────────────────────────────────────────────────────────────

class DailyPrice(BaseModel):
    date: str                       # YYYY-MM-DD
    ticker: str
    price: float
    high52: float
    low52: float
    sma50: float
    sma200: float
    rsi14: float
    dividendYield: float            # %
    pbRatio: Optional[float] = None
    peRatio: Optional[float] = None
    drawdownPercent: float          # %
    volume: Optional[int] = None


# ── Signal ─────────────────────────────────────────────────────────────────────

class Signal(BaseModel):
    date: str
    ticker: str
    score: int
    signal: Literal["BUY_NOW", "WATCHLIST", "OVERVALUED"]
    amount: float
    yieldPct: float = Field(alias="yield")
    notes: str = ""

    class Config:
        populate_by_name = True


class SignalOut(Signal):
    companyName: Optional[str] = None
    sector: Optional[str] = None
    category: Optional[str] = None


# ── Portfolio ──────────────────────────────────────────────────────────────────

class Portfolio(BaseModel):
    totalInvested: float = 0.0
    marketValue: float = 0.0
    annualDividend: float = 0.0
    monthlyDividend: float = 0.0
    yieldOnCost: float = 0.0
    cashReserve: float = 0.0


# ── Backtest ───────────────────────────────────────────────────────────────────

class BacktestRequest(BaseModel):
    startDate: str          # YYYY-MM-DD
    endDate: str            # YYYY-MM-DD
    monthlyContribution: float = 1000.0
    buyNowAmount: float = 750.0
    watchlistAmount: float = 500.0
    initialCash: float = 10000.0


class BacktestResult(BaseModel):
    cagr: float
    portfolioValue: float
    totalInvested: float
    annualDividends: float
    monthlyDividends: float
    yieldOnCost: float
    maxDrawdown: float
    dividendReinvestmentValue: float
    trades: list


# ── Screener Run ───────────────────────────────────────────────────────────────

class ScreenerRunResponse(BaseModel):
    date: str
    signalsGenerated: int
    buyNow: int
    watchlist: int
    overvalued: int
    emailSent: bool
