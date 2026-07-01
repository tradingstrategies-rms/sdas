"""
Backtesting Engine
Replays historical signals and simulates portfolio growth.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
import yfinance as yf
import pandas as pd
import numpy as np

from app.services.scoring import scoring_engine
from app.services.market_data import MarketDataService
from app.core.config import settings

logger = logging.getLogger(__name__)

_mds = MarketDataService()


class BacktestEngine:

    def run(
        self,
        start_date: str,
        end_date: str,
        monthly_contribution: float,
        buy_now_amount: float,
        watchlist_amount: float,
        initial_cash: float,
    ) -> Dict[str, Any]:
        """
        Simulate the SDAS strategy from start_date to end_date.
        Uses weekly rebalancing (every Monday) to avoid 250+ individual day runs.
        """
        logger.info("Backtest: %s → %s", start_date, end_date)

        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")

        # Download all historical data upfront
        tickers = settings.WATCHLIST_TICKERS
        raw = yf.download(
            tickers, start=start_date, end=end_date,
            auto_adjust=True, progress=False
        )
        if raw.empty:
            return {"error": "No historical data available"}

        close_prices: pd.DataFrame = raw["Close"] if "Close" in raw else raw
        close_prices = close_prices.dropna(how="all")

        # Dividend data
        div_data: Dict[str, pd.Series] = {}
        for t in tickers:
            try:
                tk = yf.Ticker(t)
                hist = tk.history(start=start_date, end=end_date)
                if not hist.empty and "Dividends" in hist:
                    div_data[t] = hist["Dividends"]
            except Exception:
                pass

        # Simulation state
        cash = initial_cash
        holdings: Dict[str, float] = {}   # ticker → shares
        portfolio_values = []
        dividends_received = []
        trades = []
        monthly_cash_added = 0.0
        last_contribution_month = None

        dates = close_prices.index.tolist()

        for i, dt in enumerate(dates):
            dt_py = dt.to_pydatetime()

            # Monthly cash injection (1st trading day of month)
            if last_contribution_month != dt_py.month:
                cash += monthly_contribution
                monthly_cash_added += monthly_contribution
                last_contribution_month = dt_py.month

            # Collect dividends
            for ticker, div_series in div_data.items():
                if ticker in holdings and dt in div_series.index:
                    div_amt = div_series[dt] * holdings[ticker]
                    if div_amt > 0:
                        cash += div_amt          # reinvest: adds to cash
                        dividends_received.append(div_amt)

            # Weekly rebalancing (Mondays only)
            if dt_py.weekday() == 0 and i >= 200:
                window_close = close_prices.iloc[max(0, i - 250): i + 1]
                sti_corr = 0.0  # simplified for backtest

                for ticker in tickers:
                    if ticker not in window_close.columns:
                        continue
                    col = window_close[ticker].dropna()
                    if len(col) < 50:
                        continue

                    price_now = col.iloc[-1]
                    sma50 = col.rolling(50).mean().iloc[-1]
                    sma200 = col.rolling(200).mean().iloc[-1] if len(col) >= 200 else sma50
                    drawdown = ((col.max() - price_now) / col.max()) * 100
                    rsi = _mds._calc_rsi(col, 14)
                    div_yield = 5.0   # approximate; real backtest would use historical yields

                    data_pt = {
                        "price": price_now, "sma50": sma50, "sma200": sma200,
                        "rsi14": rsi, "dividendYield": div_yield,
                        "drawdownPercent": drawdown, "pbRatio": None,
                    }

                    score, signal, amount, _, _ = scoring_engine.score_stock(
                        data=data_pt, category="REIT",
                        sti_correction_pct=sti_corr,
                        min_yield=settings.MIN_DIVIDEND_YIELD,
                    )

                    invest = buy_now_amount if signal == "BUY_NOW" else (
                        watchlist_amount if signal == "WATCHLIST" else 0
                    )
                    if invest > 0 and cash >= invest:
                        shares = invest / price_now
                        holdings[ticker] = holdings.get(ticker, 0) + shares
                        cash -= invest
                        trades.append({
                            "date": dt_py.strftime("%Y-%m-%d"),
                            "ticker": ticker, "signal": signal,
                            "amount": invest, "price": price_now,
                        })

            # Portfolio value snapshot (weekly)
            if dt_py.weekday() == 0:
                market_val = cash
                for ticker, shares in holdings.items():
                    if ticker in close_prices.columns:
                        px = close_prices.loc[dt, ticker] if dt in close_prices.index else 0
                        market_val += shares * px if not np.isnan(px) else 0
                portfolio_values.append({"date": dt_py.strftime("%Y-%m-%d"), "value": market_val})

        # ── Final metrics ──────────────────────────────────────────────────────
        final_value = portfolio_values[-1]["value"] if portfolio_values else initial_cash
        total_invested = initial_cash + monthly_cash_added
        total_dividends = sum(dividends_received)

        years = max((end - start).days / 365.25, 0.01)
        cagr = ((final_value / total_invested) ** (1 / years) - 1) * 100 if total_invested > 0 else 0

        values = [p["value"] for p in portfolio_values]
        peak = values[0] if values else final_value
        max_dd = 0.0
        for v in values:
            if v > peak:
                peak = v
            dd = (peak - v) / peak * 100 if peak > 0 else 0
            max_dd = max(max_dd, dd)

        annual_dividends = total_dividends / years
        monthly_dividends = annual_dividends / 12
        yoc = (annual_dividends / total_invested * 100) if total_invested > 0 else 0

        return {
            "cagr": round(cagr, 2),
            "portfolioValue": round(final_value, 2),
            "totalInvested": round(total_invested, 2),
            "annualDividends": round(annual_dividends, 2),
            "monthlyDividends": round(monthly_dividends, 2),
            "yieldOnCost": round(yoc, 2),
            "maxDrawdown": round(max_dd, 2),
            "dividendReinvestmentValue": round(total_dividends, 2),
            "portfolioHistory": portfolio_values,
            "trades": trades[-50:],   # last 50 trades to keep payload small
        }


backtest_engine = BacktestEngine()
