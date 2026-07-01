"""
SDAS Scoring Engine
Implements the full scoring + signal logic as specified.
Maximum possible score: 19
"""

from typing import Dict, Any, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ScoreBreakdown:
    trend: int = 0
    pullback: int = 0
    dividend: int = 0
    valuation: int = 0
    rsi: int = 0
    market_correction: int = 0

    @property
    def total(self) -> int:
        return (
            self.trend + self.pullback + self.dividend +
            self.valuation + self.rsi + self.market_correction
        )

    def to_notes(self) -> str:
        parts = []
        if self.trend:
            parts.append(f"Trend+{self.trend}")
        if self.pullback:
            parts.append(f"Pullback+{self.pullback}")
        if self.dividend:
            parts.append(f"Dividend+{self.dividend}")
        if self.valuation:
            parts.append(f"Valuation+{self.valuation}")
        if self.rsi:
            parts.append(f"RSI+{self.rsi}")
        if self.market_correction:
            parts.append(f"MktCorrection+{self.market_correction}")
        return " | ".join(parts) if parts else "No score"


class ScoringEngine:
    """
    Calculates composite score for a stock given its daily price data,
    category, and current STI correction %.
    """

    # ── Trend ──────────────────────────────────────────────────────────────────

    def _trend_score(self, price: float, sma50: float, sma200: float) -> int:
        score = 0
        if price > sma200:
            score += 2
        if price > sma50:
            score += 1
        if sma50 > sma200:
            score += 1
        return score

    # ── Pullback ───────────────────────────────────────────────────────────────

    def _pullback_score(self, drawdown: float) -> int:
        if drawdown < 5:
            return 0
        elif drawdown < 10:
            return 1
        elif drawdown < 15:
            return 2
        else:
            return 3

    # ── Dividend ───────────────────────────────────────────────────────────────

    def _dividend_score(self, yield_pct: float, category: str) -> int:
        cat = category.lower()

        if cat == "bank":
            if yield_pct > 5.0:
                return 2
            elif yield_pct > 4.5:
                return 1
            return 0

        elif cat == "reit":
            if yield_pct > 7.5:
                return 3
            elif yield_pct > 6.5:
                return 2
            elif yield_pct > 5.5:
                return 1
            return 0

        elif cat == "infrastructure":
            if yield_pct > 6.5:
                return 2
            return 0

        else:  # Equity / default
            if yield_pct > 4.0:
                return 1
            return 0

    # ── Valuation (PB) ─────────────────────────────────────────────────────────

    def _valuation_score(self, pb_ratio: float, pb_5yr_avg: float) -> int:
        """
        pb_5yr_avg: 5-year average PB for this stock.
        If unavailable, return 0.
        """
        if not pb_ratio or not pb_5yr_avg or pb_5yr_avg <= 0:
            return 0
        discount = (pb_5yr_avg - pb_ratio) / pb_5yr_avg * 100
        if discount >= 10:
            return 2
        elif discount > 0:
            return 1
        return 0

    # ── RSI ────────────────────────────────────────────────────────────────────

    def _rsi_score(self, rsi: float) -> int:
        if rsi < 30:
            return 3
        elif rsi < 40:
            return 2
        elif rsi < 50:
            return 1
        return 0

    # ── Market Correction Bonus ────────────────────────────────────────────────

    def _market_correction_score(self, sti_correction_pct: float) -> int:
        if sti_correction_pct >= 20:
            return 4
        elif sti_correction_pct >= 10:
            return 2
        elif sti_correction_pct >= 5:
            return 1
        return 0

    # ── Master Rules ───────────────────────────────────────────────────────────

    def _apply_master_rules(
        self,
        yield_pct: float,
        price: float,
        sma200: float,
        score: int,
        min_yield: float = 4.0,
    ) -> Tuple[str, float, str]:
        """
        Returns (signal, amount, rule_note).
        OVERVALUED short-circuits further logic.
        """
        # Rule 1: min yield
        if yield_pct < min_yield:
            return "OVERVALUED", 0.0, f"Yield {yield_pct:.1f}% < {min_yield}% minimum"

        # Rule 2: below SMA200
        if price < sma200:
            return "OVERVALUED", 0.0, f"Price {price} < SMA200 {sma200:.2f}"

        # Signal classification
        if score >= 13:
            return "BUY_NOW", 750.0, ""
        elif score >= 9:
            return "WATCHLIST", 500.0, ""
        else:
            return "OVERVALUED", 0.0, f"Score {score} < 9 threshold"

    # ── Public API ─────────────────────────────────────────────────────────────

    def score_stock(
        self,
        data: Dict[str, Any],
        category: str,
        sti_correction_pct: float = 0.0,
        pb_5yr_avg: float = None,
        min_yield: float = 4.0,
    ) -> Tuple[int, str, float, str, ScoreBreakdown]:
        """
        Returns (score, signal, amount, notes, breakdown).
        """
        price = data["price"]
        sma50 = data["sma50"]
        sma200 = data["sma200"]
        rsi = data["rsi14"]
        yield_pct = data["dividendYield"]
        drawdown = data["drawdownPercent"]
        pb_ratio = data.get("pbRatio")

        breakdown = ScoreBreakdown(
            trend=self._trend_score(price, sma50, sma200),
            pullback=self._pullback_score(drawdown),
            dividend=self._dividend_score(yield_pct, category),
            valuation=self._valuation_score(pb_ratio, pb_5yr_avg),
            rsi=self._rsi_score(rsi),
            market_correction=self._market_correction_score(sti_correction_pct),
        )

        score = breakdown.total
        signal, amount, rule_note = self._apply_master_rules(
            yield_pct, price, sma200, score, min_yield
        )

        notes = rule_note if rule_note else breakdown.to_notes()
        return score, signal, amount, notes, breakdown


scoring_engine = ScoringEngine()
