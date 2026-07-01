"""
Unit tests for the SDAS scoring engine.
Run: pytest tests/ -v
"""

import pytest
from app.services.scoring import ScoringEngine, ScoreBreakdown

engine = ScoringEngine()


def _make_data(
    price=3.50, sma50=3.40, sma200=3.20, rsi=45,
    div_yield=5.5, drawdown=12.0, pb=1.0,
):
    return {
        "price": price, "sma50": sma50, "sma200": sma200,
        "rsi14": rsi, "dividendYield": div_yield,
        "drawdownPercent": drawdown, "pbRatio": pb,
    }


class TestTrendScore:
    def test_all_trend_signals(self):
        # price > sma200 (+2), price > sma50 (+1), sma50 > sma200 (+1) = 4
        score = engine._trend_score(price=3.5, sma50=3.4, sma200=3.2)
        assert score == 4

    def test_below_sma200(self):
        score = engine._trend_score(price=3.0, sma50=3.1, sma200=3.2)
        assert score == 0

    def test_above_sma200_only(self):
        # price > sma200 (+2), sma50 > sma200 (+1), price < sma50 (no +1) = 3
        score = engine._trend_score(price=3.5, sma50=3.6, sma200=3.2)
        assert score == 3


class TestPullbackScore:
    def test_no_pullback(self):
        assert engine._pullback_score(3.0) == 0

    def test_moderate_pullback(self):
        assert engine._pullback_score(7.0) == 1
        assert engine._pullback_score(12.0) == 2
        assert engine._pullback_score(20.0) == 3


class TestDividendScore:
    def test_reit_high_yield(self):
        assert engine._dividend_score(8.0, "REIT") == 3

    def test_reit_mid_yield(self):
        assert engine._dividend_score(7.0, "REIT") == 2

    def test_bank_high(self):
        assert engine._dividend_score(5.5, "Bank") == 2

    def test_bank_low(self):
        assert engine._dividend_score(4.0, "Bank") == 0

    def test_equity(self):
        assert engine._dividend_score(4.5, "Equity") == 1


class TestRsiScore:
    def test_oversold(self):
        assert engine._rsi_score(28) == 3

    def test_weak(self):
        assert engine._rsi_score(38) == 2
        assert engine._rsi_score(48) == 1
        assert engine._rsi_score(55) == 0


class TestMarketCorrectionBonus:
    def test_crash(self):
        assert engine._market_correction_score(22) == 4

    def test_correction(self):
        assert engine._market_correction_score(12) == 2

    def test_pullback(self):
        assert engine._market_correction_score(6) == 1

    def test_none(self):
        assert engine._market_correction_score(2) == 0


class TestMasterRules:
    def test_low_yield_is_overvalued(self):
        signal, amount, _ = engine._apply_master_rules(3.5, 3.5, 3.2, 15)
        assert signal == "OVERVALUED"
        assert amount == 0

    def test_below_sma200_is_overvalued(self):
        signal, amount, _ = engine._apply_master_rules(5.0, 3.0, 3.5, 15)
        assert signal == "OVERVALUED"

    def test_buy_now(self):
        signal, amount, _ = engine._apply_master_rules(5.0, 3.5, 3.2, 14)
        assert signal == "BUY_NOW"
        assert amount == 750

    def test_watchlist(self):
        signal, amount, _ = engine._apply_master_rules(5.0, 3.5, 3.2, 10)
        assert signal == "WATCHLIST"
        assert amount == 500

    def test_low_score_overvalued(self):
        signal, amount, _ = engine._apply_master_rules(5.0, 3.5, 3.2, 8)
        assert signal == "OVERVALUED"


class TestFullScoreStock:
    def test_buy_now_reit(self):
        data = _make_data(div_yield=7.8, drawdown=18, rsi=28)
        score, signal, amount, notes, breakdown = engine.score_stock(
            data, category="REIT", sti_correction_pct=12
        )
        assert signal == "BUY_NOW"
        assert score >= 13

    def test_overvalued_low_yield(self):
        data = _make_data(div_yield=3.0)
        score, signal, amount, notes, breakdown = engine.score_stock(data, "Equity")
        assert signal == "OVERVALUED"
        assert amount == 0
