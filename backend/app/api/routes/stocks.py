"""Stocks API routes."""
from fastapi import APIRouter, HTTPException
from app.repositories.stock_repo import stock_repo
from app.models.schemas import StockCreate

router = APIRouter()


@router.get("/")
def list_stocks():
    return stock_repo.get_all_active()


@router.get("/{ticker}")
def get_stock(ticker: str):
    stock = stock_repo.get(ticker)
    if not stock:
        raise HTTPException(404, "Stock not found")
    return stock


@router.post("/")
def add_stock(stock: StockCreate):
    stock_repo.upsert(stock.model_dump())
    return {"success": True, "ticker": stock.ticker}


@router.delete("/{ticker}")
def remove_stock(ticker: str):
    stock_repo.delete(ticker)
    return {"success": True}
