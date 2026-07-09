"""Transactions API routes."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.repositories.transaction_repo import transaction_repo
from app.services.portfolio_service import portfolio_service

router = APIRouter()


class TransactionCreate(BaseModel):
    ticker: str
    companyName: str
    date: str                    # YYYY-MM-DD
    price: float
    quantity: float
    commission: float = 0.0
    currency: str = "SGD"
    market: str = "SGX"
    category: str = "Equity"
    broker: str = ""
    notes: str = ""
    type: str = "BUY"


@router.get("/")
def get_transactions():
    return transaction_repo.get_all()


@router.get("/holdings")
def get_holdings():
    return transaction_repo.get_holdings()


@router.get("/portfolio")
def get_portfolio():
    """Calculate full portfolio with live prices and P&L."""
    return portfolio_service.calculate()


@router.post("/")
def add_transaction(txn: TransactionCreate):
    doc_id = transaction_repo.add(txn.model_dump())
    return {"success": True, "id": doc_id}


@router.delete("/{doc_id}")
def delete_transaction(doc_id: str):
    transaction_repo.delete(doc_id)
    return {"success": True}


@router.get("/{ticker}")
def get_ticker_transactions(ticker: str):
    return transaction_repo.get_by_ticker(ticker)