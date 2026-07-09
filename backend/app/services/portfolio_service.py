"""
Portfolio Service
Calculates real portfolio metrics from actual transactions.
"""

import logging
from typing import List, Dict, Any

from app.repositories.transaction_repo import transaction_repo
from app.repositories.price_repo import price_repo, portfolio_repo
from app.repositories.stock_repo import stock_repo

logger = logging.getLogger(__name__)


class PortfolioService:

    def calculate(self) -> Dict[str, Any]:
        """
        Calculate real portfolio metrics from transactions.
        Saves updated portfolio snapshot to Firestore.
        Returns full portfolio data.
        """
        holdings = transaction_repo.get_holdings()
        all_stocks = {s["ticker"]: s for s in stock_repo.get_all_active()}

        enriched_holdings = []
        total_invested = 0.0
        total_market_value = 0.0
        total_annual_dividend = 0.0

        for holding in holdings:
            ticker = holding["ticker"]
            stock_meta = all_stocks.get(ticker, {})

            # Get latest price from daily_prices
            latest_price_doc = price_repo.get_latest(ticker)
            current_price = latest_price_doc.get("price", 0) if latest_price_doc else 0
            div_yield_pct = latest_price_doc.get("dividendYield", 0) if latest_price_doc else 0

            # Use targetYield from stock meta if no live yield
            if div_yield_pct == 0:
                div_yield_pct = stock_meta.get("targetYield", 0)

            shares = holding["totalShares"]
            avg_cost = holding["avgCostPrice"]
            cost_basis = holding["totalCost"]

            market_value = shares * current_price if current_price > 0 else cost_basis
            unrealised_pl = market_value - cost_basis
            unrealised_pl_pct = (unrealised_pl / cost_basis * 100) if cost_basis > 0 else 0

            annual_dividend = market_value * (div_yield_pct / 100)
            monthly_dividend = annual_dividend / 12
            yield_on_cost = (annual_dividend / cost_basis * 100) if cost_basis > 0 else 0

            enriched_holdings.append({
                **holding,
                "currentPrice": round(current_price, 4),
                "marketValue": round(market_value, 2),
                "unrealisedPL": round(unrealised_pl, 2),
                "unrealisedPLPct": round(unrealised_pl_pct, 2),
                "dividendYield": round(div_yield_pct, 2),
                "annualDividend": round(annual_dividend, 2),
                "monthlyDividend": round(monthly_dividend, 2),
                "yieldOnCost": round(yield_on_cost, 2),
                "sector": stock_meta.get("sector", ""),
            })

            total_invested += cost_basis
            total_market_value += market_value
            total_annual_dividend += annual_dividend

        total_monthly_dividend = total_annual_dividend / 12
        total_unrealised_pl = total_market_value - total_invested
        total_yield_on_cost = (
            (total_annual_dividend / total_invested * 100)
            if total_invested > 0 else 0
        )
        target_monthly = 5000.0
        progress_pct = min(
            (total_monthly_dividend / target_monthly * 100), 100
        ) if target_monthly > 0 else 0

        # Sort holdings by market value descending
        enriched_holdings.sort(key=lambda x: x["marketValue"], reverse=True)

        # Save snapshot to Firestore
        snapshot = {
            "totalInvested": round(total_invested, 2),
            "marketValue": round(total_market_value, 2),
            "unrealisedPL": round(total_unrealised_pl, 2),
            "annualDividend": round(total_annual_dividend, 2),
            "monthlyDividend": round(total_monthly_dividend, 2),
            "yieldOnCost": round(total_yield_on_cost, 2),
            "cashReserve": 0.0,
            "progressPct": round(progress_pct, 2),
            "holdingsCount": len(enriched_holdings),
        }
        portfolio_repo.update(snapshot)

        return {
            **snapshot,
            "holdings": enriched_holdings,
            "targetMonthly": target_monthly,
        }


portfolio_service = PortfolioService()