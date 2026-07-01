"""
SDAS - Singapore Dividend Accumulation Screener
FastAPI Backend Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.db.firebase import init_firebase
from app.api.routes import stocks, signals, portfolio, screener, backtest, scheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup."""
    logger.info("Initializing Firebase...")
    init_firebase()
    logger.info("SDAS Backend started.")
    yield
    logger.info("SDAS Backend shutting down.")


app = FastAPI(
    title="SDAS - Singapore Dividend Accumulation Screener",
    description="API for screening Singapore dividend stocks",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(stocks.router, prefix="/api/v1/stocks", tags=["stocks"])
app.include_router(signals.router, prefix="/api/v1/signals", tags=["signals"])
app.include_router(portfolio.router, prefix="/api/v1/portfolio", tags=["portfolio"])
app.include_router(screener.router, prefix="/api/v1/screener", tags=["screener"])
app.include_router(backtest.router, prefix="/api/v1/backtest", tags=["backtest"])
app.include_router(scheduler.router, prefix="/api/v1/scheduler", tags=["scheduler"])


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "SDAS Backend"}
