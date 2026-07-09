"""Transaction repository — stores real buy transactions."""

from app.db.firebase import get_db
from typing import List, Dict, Optional
from datetime import datetime
import uuid


class TransactionRepository:
    COLLECTION = "transactions"

    def add(self, transaction: Dict) -> str:
        """Add a new transaction. Returns the document ID."""
        db = get_db()
        doc_id = str(uuid.uuid4())
        transaction["id"] = doc_id
        transaction["createdAt"] = datetime.now().isoformat()
        db.collection(self.COLLECTION).document(doc_id).set(transaction)
        return doc_id

    def get_all(self) -> List[Dict]:
        """Get all transactions sorted by date descending."""
        db = get_db()
        docs = (
            db.collection(self.COLLECTION)
            .order_by("date", direction="DESCENDING")
            .stream()
        )
        return [d.to_dict() for d in docs]

    def get_by_ticker(self, ticker: str) -> List[Dict]:
        """Get all transactions for a specific ticker."""
        db = get_db()
        docs = (
            db.collection(self.COLLECTION)
            .where("ticker", "==", ticker)
            .order_by("date", direction="DESCENDING")
            .stream()
        )
        return [d.to_dict() for d in docs]

    def delete(self, doc_id: str) -> None:
        db = get_db()
        db.collection(self.COLLECTION).document(doc_id).delete()

    def get_holdings(self) -> List[Dict]:
        """
        Aggregate all BUY transactions into holdings.
        Returns one row per ticker with:
        - totalShares
        - totalCost
        - avgCostPrice
        - firstBuyDate
        - lastBuyDate
        """
        all_txns = self.get_all()
        holdings: Dict[str, Dict] = {}

        for txn in all_txns:
            ticker = txn["ticker"]
            if txn.get("type", "BUY") != "BUY":
                continue

            if ticker not in holdings:
                holdings[ticker] = {
                    "ticker": ticker,
                    "companyName": txn.get("companyName", ticker),
                    "category": txn.get("category", "Equity"),
                    "market": txn.get("market", "SGX"),
                    "currency": txn.get("currency", "SGD"),
                    "totalShares": 0.0,
                    "totalCost": 0.0,
                    "firstBuyDate": txn["date"],
                    "lastBuyDate": txn["date"],
                    "transactions": [],
                }

            shares = float(txn.get("quantity", 0))
            price = float(txn.get("price", 0))
            commission = float(txn.get("commission", 0))
            cost = (shares * price) + commission

            holdings[ticker]["totalShares"] += shares
            holdings[ticker]["totalCost"] += cost
            holdings[ticker]["transactions"].append(txn)

            if txn["date"] < holdings[ticker]["firstBuyDate"]:
                holdings[ticker]["firstBuyDate"] = txn["date"]
            if txn["date"] > holdings[ticker]["lastBuyDate"]:
                holdings[ticker]["lastBuyDate"] = txn["date"]

        # Calculate average cost price
        for ticker, h in holdings.items():
            if h["totalShares"] > 0:
                h["avgCostPrice"] = round(h["totalCost"] / h["totalShares"], 4)
            else:
                h["avgCostPrice"] = 0.0
            h["totalCost"] = round(h["totalCost"], 2)
            h["totalShares"] = round(h["totalShares"], 4)

        return list(holdings.values())


transaction_repo = TransactionRepository()