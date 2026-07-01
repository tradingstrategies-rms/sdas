"""Portfolio API routes."""
from fastapi import APIRouter
from app.repositories.price_repo import portfolio_repo

router = APIRouter()


@router.get("/")
def get_portfolio():
    return portfolio_repo.get()


@router.put("/")
def update_portfolio(data: dict):
    portfolio_repo.update(data)
    return {"success": True}
