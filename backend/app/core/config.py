"""
Core configuration — reads from environment variables.
Copy .env.example to .env and fill in your values.
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # App
    APP_NAME: str = "SDAS"
    DEBUG: bool = False
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]

    # Firebase
    FIREBASE_PROJECT_ID: str
    FIREBASE_PRIVATE_KEY: str = ""
    FIREBASE_PRIVATE_KEY: str
    FIREBASE_CLIENT_EMAIL: str
    FIREBASE_CLIENT_ID: str
    FIREBASE_CLIENT_CERT_URL: str

    # SendGrid
    SENDGRID_API_KEY: str = ""
    EMAIL_FROM: str = "noreply@yourdomain.com"
    EMAIL_TO: str = ""

    # Scheduler
    SCHEDULER_SECRET: str = "change-me-in-production"

    # STI index ticker
    STI_TICKER: str = "^STI"

    # Screener defaults
    MIN_DIVIDEND_YIELD: float = 4.0
    BUY_NOW_SCORE: int = 13
    WATCHLIST_SCORE: int = 9
    BUY_NOW_AMOUNT: float = 750.0
    WATCHLIST_AMOUNT: float = 500.0
    MAX_POSITION_PCT: float = 15.0
    CASH_RESERVE_PCT: float = 20.0

    # Screener schedule (SGT = UTC+8)
    SCREENER_HOUR_SGT: int = 19
    SCREENER_MINUTE_SGT: int = 15
    EMAIL_HOUR_SGT: int = 19
    EMAIL_MINUTE_SGT: int = 30

    # Watchlist tickers
    WATCHLIST_TICKERS: List[str] = [
        "D05.SI", "U11.SI", "Z74.SI", "S58.SI", "C07.SI", "9CI.SI",
        "A17U.SI", "C38U.SI", "AJBU.SI", "HMN.SI", "M44U.SI",
        "C2PU.SI", "J69U.SI", "A7RU.SI",
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()