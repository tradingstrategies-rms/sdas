"""Stock repository — Firestore CRUD."""

from app.db.firebase import get_db
from typing import List, Dict


class StockRepository:
    COLLECTION = "stocks"

    def get_all_active(self) -> List[Dict]:
        db = get_db()
        docs = db.collection(self.COLLECTION).where("active", "==", True).stream()
        return [{"id": d.id, **d.to_dict()} for d in docs]

    def get(self, ticker: str) -> Dict:
        db = get_db()
        doc = db.collection(self.COLLECTION).document(ticker).get()
        return doc.to_dict() if doc.exists else {}

    def upsert(self, stock: Dict) -> None:
        db = get_db()
        db.collection(self.COLLECTION).document(stock["ticker"]).set(stock, merge=True)

    def delete(self, ticker: str) -> None:
        db = get_db()
        db.collection(self.COLLECTION).document(ticker).delete()


stock_repo = StockRepository()
