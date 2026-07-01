"""Firestore repositories for daily_prices and signals."""

from app.db.firebase import get_db
from typing import List, Dict, Optional
from datetime import datetime


class PriceRepository:
    COLLECTION = "daily_prices"

    def upsert(self, data: Dict) -> None:
        db = get_db()
        doc_id = f"{data['date']}_{data['ticker']}"
        db.collection(self.COLLECTION).document(doc_id).set(data, merge=True)

    def get_latest(self, ticker: str) -> Optional[Dict]:
        db = get_db()
        docs = (
            db.collection(self.COLLECTION)
            .where("ticker", "==", ticker)
            .order_by("date", direction="DESCENDING")
            .limit(1)
            .stream()
        )
        for doc in docs:
            return doc.to_dict()
        return None

    def get_history(self, ticker: str, limit: int = 60) -> List[Dict]:
        db = get_db()
        docs = (
            db.collection(self.COLLECTION)
            .where("ticker", "==", ticker)
            .order_by("date", direction="DESCENDING")
            .limit(limit)
            .stream()
        )
        return [d.to_dict() for d in docs]

    def get_by_date(self, date: str) -> List[Dict]:
        db = get_db()
        docs = db.collection(self.COLLECTION).where("date", "==", date).stream()
        return [d.to_dict() for d in docs]


class SignalRepository:
    COLLECTION = "signals"

    def upsert(self, signal: Dict) -> None:
        db = get_db()
        doc_id = f"{signal['date']}_{signal['ticker']}"
        db.collection(self.COLLECTION).document(doc_id).set(signal, merge=True)

    def get_latest(self) -> List[Dict]:
        """Most recent date's signals for all tickers."""
        db = get_db()
        docs = (
            db.collection(self.COLLECTION)
            .order_by("date", direction="DESCENDING")
            .limit(50)
            .stream()
        )
        all_docs = [d.to_dict() for d in docs]
        if not all_docs:
            return []
        latest_date = all_docs[0]["date"]
        return [d for d in all_docs if d["date"] == latest_date]

    def get_by_date(self, date: str) -> List[Dict]:
        db = get_db()
        docs = db.collection(self.COLLECTION).where("date", "==", date).stream()
        return [d.to_dict() for d in docs]

    def get_history(self, ticker: str, limit: int = 30) -> List[Dict]:
        db = get_db()
        docs = (
            db.collection(self.COLLECTION)
            .where("ticker", "==", ticker)
            .order_by("date", direction="DESCENDING")
            .limit(limit)
            .stream()
        )
        return [d.to_dict() for d in docs]


class PortfolioRepository:
    COLLECTION = "portfolio"
    DOC_ID = "current"

    def get(self) -> Dict:
        db = get_db()
        doc = db.collection(self.COLLECTION).document(self.DOC_ID).get()
        return doc.to_dict() if doc.exists else {
            "totalInvested": 0, "marketValue": 0, "annualDividend": 0,
            "monthlyDividend": 0, "yieldOnCost": 0, "cashReserve": 0,
        }

    def update(self, data: Dict) -> None:
        db = get_db()
        db.collection(self.COLLECTION).document(self.DOC_ID).set(data, merge=True)


price_repo = PriceRepository()
signal_repo = SignalRepository()
portfolio_repo = PortfolioRepository()
