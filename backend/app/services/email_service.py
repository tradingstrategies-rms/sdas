"""
Email service — sends the daily signals digest via SendGrid.
"""

import logging
from typing import List, Dict, Any
from datetime import datetime

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from app.core.config import settings

logger = logging.getLogger(__name__)


def _score_breakdown(notes: str) -> Dict[str, str]:
    """Parse notes string like 'Trend+4 | Pullback+3 | Dividend+2' into dict."""
    breakdown = {
        "trend": "0", "pullback": "0", "dividend": "0",
        "valuation": "0", "rsi": "0", "mkt": "0"
    }
    if not notes:
        return breakdown
    for part in notes.split("|"):
        part = part.strip()
        if part.startswith("Trend+"):
            breakdown["trend"] = part.replace("Trend+", "")
        elif part.startswith("Pullback+"):
            breakdown["pullback"] = part.replace("Pullback+", "")
        elif part.startswith("Dividend+"):
            breakdown["dividend"] = part.replace("Dividend+", "")
        elif part.startswith("Valuation+"):
            breakdown["valuation"] = part.replace("Valuation+", "")
        elif part.startswith("RSI+"):
            breakdown["rsi"] = part.replace("RSI+", "")
        elif part.startswith("MktCorrection+"):
            breakdown["mkt"] = part.replace("MktCorrection+", "")
    return breakdown


def _score_cell(val: str, max_val: int) -> str:
    """Return a coloured score cell."""
    try:
        v = int(val)
    except ValueError:
        v = 0
    if v == 0:
        color = "#cbd5e1"
    elif v >= max_val:
        color = "#16a34a"
    else:
        color = "#d97706"
    return f'<td style="text-align:center;padding:6px 4px;color:{color};font-weight:bold;font-size:13px">{val}</td>'


def _stock_table(signal_list: List[Dict], section_color: str) -> str:
    """Build a full breakdown table for a list of signals, grouped by market, sorted by score."""
    if not signal_list:
        return '<p style="color:#999;padding:8px 0;font-size:13px">None today</p>'

    markets = sorted(set(r.get("market", "SGX") for r in signal_list))
    html = ""

    header = """
    <table width="100%" style="border-collapse:collapse;font-size:12px">
      <thead>
        <tr style="background:#f8fafc;color:#64748b;text-transform:uppercase;
                   letter-spacing:0.5px;font-size:10px">
          <th style="text-align:left;padding:8px 6px;min-width:160px">Stock</th>
          <th style="text-align:center;padding:8px 4px">Yield</th>
          <th style="text-align:center;padding:8px 4px">Total<br>Score</th>
          <th style="text-align:center;padding:8px 4px">Trend<br>/4</th>
          <th style="text-align:center;padding:8px 4px">Pullback<br>/3</th>
          <th style="text-align:center;padding:8px 4px">Dividend<br>/3</th>
          <th style="text-align:center;padding:8px 4px">Valuation<br>/2</th>
          <th style="text-align:center;padding:8px 4px">RSI<br>/3</th>
          <th style="text-align:center;padding:8px 4px">Mkt Corr<br>/4</th>
          <th style="text-align:center;padding:8px 4px">Deploy</th>
        </tr>
      </thead>
      <tbody>"""

    for market in markets:
        market_stocks = [r for r in signal_list if r.get("market", "SGX") == market]
        market_stocks = sorted(market_stocks, key=lambda x: x.get("score", 0), reverse=True)

        if not market_stocks:
            continue

        html += header
        html += f"""
        <tr>
          <td colspan="10" style="padding:10px 6px 4px;font-size:10px;
              color:#94a3b8;text-transform:uppercase;letter-spacing:1px;
              border-bottom:1px solid #e2e8f0">
            {market}
          </td>
        </tr>"""

        for i, r in enumerate(market_stocks):
            bd = _score_breakdown(r.get("notes", ""))
            row_bg = "#ffffff" if i % 2 == 0 else "#f8fafc"
            deploy = f"SGD {r['amount']:.0f}" if r.get("amount", 0) > 0 else "—"

            html += f"""
            <tr style="background:{row_bg};border-bottom:1px solid #f1f5f9">
              <td style="padding:8px 6px">
                <strong style="color:#1e293b">{r.get('companyName', r['ticker'])}</strong>
                <br><span style="color:#94a3b8;font-size:10px">{r['ticker']} · {r.get('category','')}</span>
              </td>
              <td style="text-align:center;padding:6px 4px;
                  color:{section_color};font-weight:bold">{r.get('yield', 0):.1f}%</td>
              <td style="text-align:center;padding:6px 4px;
                  font-weight:bold;font-size:14px;color:{section_color}">{r.get('score', 0)}/19</td>
              {_score_cell(bd['trend'], 4)}
              {_score_cell(bd['pullback'], 3)}
              {_score_cell(bd['dividend'], 3)}
              {_score_cell(bd['valuation'], 2)}
              {_score_cell(bd['rsi'], 3)}
              {_score_cell(bd['mkt'], 4)}
              <td style="text-align:center;padding:6px 4px;
                  font-weight:bold;color:#1e293b">{deploy}</td>
            </tr>"""

        html += "</tbody></table>"

    return html


def _overvalued_table(signal_list: List[Dict]) -> str:
    """Compact table for overvalued stocks — no score breakdown, just reason."""
    if not signal_list:
        return '<p style="color:#999;padding:8px 0;font-size:13px">None today</p>'

    markets = sorted(set(r.get("market", "SGX") for r in signal_list))
    html = ""

    for market in markets:
        market_stocks = [r for r in signal_list if r.get("market", "SGX") == market]
        market_stocks = sorted(market_stocks, key=lambda x: x.get("score", 0), reverse=True)

        if not market_stocks:
            continue

        html += f"""
        <p style="font-size:10px;color:#94a3b8;text-transform:uppercase;
            letter-spacing:1px;margin:12px 0 4px">{market}</p>
        <table width="100%" style="border-collapse:collapse;font-size:12px">
          <thead>
            <tr style="background:#f8fafc;color:#64748b;text-transform:uppercase;
                       font-size:10px;letter-spacing:0.5px">
              <th style="text-align:left;padding:6px">Stock</th>
              <th style="text-align:center;padding:6px">Score</th>
              <th style="text-align:center;padding:6px">Yield</th>
              <th style="text-align:left;padding:6px">Reason</th>
            </tr>
          </thead>
          <tbody>"""

        for i, r in enumerate(market_stocks):
            row_bg = "#ffffff" if i % 2 == 0 else "#fef2f2"
            html += f"""
            <tr style="background:{row_bg};border-bottom:1px solid #fee2e2">
              <td style="padding:6px">
                <strong>{r.get('companyName', r['ticker'])}</strong>
                <br><span style="color:#94a3b8;font-size:10px">{r['ticker']}</span>
              </td>
              <td style="text-align:center;padding:6px;color:#dc2626">{r.get('score',0)}/19</td>
              <td style="text-align:center;padding:6px;color:#dc2626">{r.get('yield',0):.1f}%</td>
              <td style="padding:6px;color:#dc2626;font-size:11px">{r.get('notes','')}</td>
            </tr>"""

        html += "</tbody></table>"

    return html


def _render_html(run_result: Dict[str, Any]) -> str:
    date_str = run_result.get("date", datetime.now().strftime("%Y-%m-%d"))
    results: List[Dict] = run_result.get("results", [])
    sti_corr = run_result.get("stiCorrection", 0)

    buy_now = [r for r in results if r["signal"] == "BUY_NOW"]
    watchlist_items = [r for r in results if r["signal"] == "WATCHLIST"]
    overvalued = [r for r in results if r["signal"] == "OVERVALUED"]

    sti_badge = ""
    if sti_corr >= 20:
        sti_badge = f"🚨 MARKET CRASH: STI down {sti_corr:.1f}% — DEPLOY CASH RESERVES"
    elif sti_corr >= 10:
        sti_badge = f"⚠️ MARKET CORRECTION: STI down {sti_corr:.1f}% — Invest additional SGD 1,000"
    elif sti_corr >= 5:
        sti_badge = f"📉 STI pullback {sti_corr:.1f}%"

    sti_html = ""
    if sti_badge:
        sti_html = f"""
        <div style="background:#fef9c3;border-left:4px solid #ca8a04;
            padding:12px 16px;font-weight:bold;font-size:14px">
            {sti_badge}
        </div>"""

    total_deploy = sum(r.get("amount", 0) for r in results)

    return f"""
<!DOCTYPE html>
<html>
<head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
</head>
<body style="font-family:Arial,sans-serif;max-width:780px;margin:auto;
             color:#1a1a1a;background:#f8fafc;padding:16px">

  <!-- Header -->
  <div style="background:#0f172a;color:white;padding:24px 28px;
              border-radius:10px 10px 0 0">
    <h1 style="margin:0;font-size:22px;font-weight:700">
      📊 Singapore Dividend Screener
    </h1>
    <p style="margin:6px 0 0;opacity:0.6;font-size:13px">
      Daily Signals — {date_str}
    </p>
  </div>

  <!-- Summary bar -->
  <div style="background:#1e293b;padding:12px 28px;display:flex;gap:32px">
    <span style="color:#4ade80;font-size:13px;font-weight:600">
      🟢 BUY NOW: {len(buy_now)}
    </span>
    <span style="color:#fbbf24;font-size:13px;font-weight:600">
      🟡 WATCHLIST: {len(watchlist_items)}
    </span>
    <span style="color:#f87171;font-size:13px;font-weight:600">
      🔴 OVERVALUED: {len(overvalued)}
    </span>
    <span style="color:#94a3b8;font-size:13px">
      💰 Deploy today: SGD {total_deploy:,.0f}
    </span>
  </div>

  {sti_html}

  <!-- BUY NOW -->
  <div style="background:#ffffff;border-left:4px solid #16a34a;
              margin:16px 0;border-radius:6px;overflow:hidden;
              box-shadow:0 1px 3px rgba(0,0,0,0.08)">
    <div style="background:#f0fdf4;padding:14px 20px;
                border-bottom:1px solid #dcfce7">
      <h2 style="margin:0;color:#15803d;font-size:16px">
        🟢 BUY NOW ({len(buy_now)})
        <span style="font-size:12px;font-weight:normal;color:#4ade80;margin-left:8px">
          Score ≥ 13 · Yield ≥ 4% · Price above SMA200
        </span>
      </h2>
    </div>
    <div style="padding:16px 20px;overflow-x:auto">
      {_stock_table(buy_now, "#16a34a")}
    </div>
  </div>

  <!-- WATCHLIST -->
  <div style="background:#ffffff;border-left:4px solid #d97706;
              margin:16px 0;border-radius:6px;overflow:hidden;
              box-shadow:0 1px 3px rgba(0,0,0,0.08)">
    <div style="background:#fffbeb;padding:14px 20px;
                border-bottom:1px solid #fef3c7">
      <h2 style="margin:0;color:#b45309;font-size:16px">
        🟡 WATCHLIST ({len(watchlist_items)})
        <span style="font-size:12px;font-weight:normal;color:#f59e0b;margin-left:8px">
          Score 9–12 · Yield ≥ 4% · Price above SMA200
        </span>
      </h2>
    </div>
    <div style="padding:16px 20px;overflow-x:auto">
      {_stock_table(watchlist_items, "#d97706")}
    </div>
  </div>

  <!-- OVERVALUED -->
  <div style="background:#ffffff;border-left:4px solid #dc2626;
              margin:16px 0;border-radius:6px;overflow:hidden;
              box-shadow:0 1px 3px rgba(0,0,0,0.08)">
    <div style="background:#fef2f2;padding:14px 20px;
                border-bottom:1px solid #fee2e2">
      <h2 style="margin:0;color:#b91c1c;font-size:16px">
        🔴 OVERVALUED / SKIP ({len(overvalued)})
      </h2>
    </div>
    <div style="padding:16px 20px">
      {_overvalued_table(overvalued)}
    </div>
  </div>

  <!-- Score legend -->
  <div style="background:#ffffff;border-radius:6px;padding:16px 20px;
              margin:16px 0;box-shadow:0 1px 3px rgba(0,0,0,0.08)">
    <p style="margin:0 0 10px;font-size:11px;color:#64748b;
              text-transform:uppercase;letter-spacing:1px">
      Score Legend (max 19)
    </p>
    <table style="font-size:12px;color:#475569;border-collapse:collapse">
      <tr>
        <td style="padding:3px 16px 3px 0">📈 <strong>Trend</strong> /4</td>
        <td style="padding:3px 16px 3px 0">Price vs SMA50 + SMA200</td>
        <td style="padding:3px 16px 3px 0">📉 <strong>Pullback</strong> /3</td>
        <td style="padding:3px 0">Drawdown from 52w high</td>
      </tr>
      <tr>
        <td style="padding:3px 16px 3px 0">💰 <strong>Dividend</strong> /3</td>
        <td style="padding:3px 16px 3px 0">Category yield thresholds</td>
        <td style="padding:3px 16px 3px 0">📊 <strong>Valuation</strong> /2</td>
        <td style="padding:3px 0">PB vs 5-year average</td>
      </tr>
      <tr>
        <td style="padding:3px 16px 3px 0">🔻 <strong>RSI</strong> /3</td>
        <td style="padding:3px 16px 3px 0">Oversold signal (&lt;50)</td>
        <td style="padding:3px 16px 3px 0">🌏 <strong>Mkt Corr</strong> /4</td>
        <td style="padding:3px 0">STI correction bonus</td>
      </tr>
    </table>
  </div>

  <!-- Footer -->
  <div style="padding:12px 0;text-align:center;font-size:11px;color:#94a3b8">
    SDAS · Singapore Dividend Accumulation Screener · Goal: SGD 5,000/month
  </div>

</body>
</html>"""


class EmailService:

    def send_daily_signals(self, run_result: Dict[str, Any]) -> bool:
        try:
            html = _render_html(run_result)
            date_str = run_result.get("date", "")
            buy_count = run_result.get("buyNow", 0)
            watch_count = run_result.get("watchlist", 0)

            subject = (
                f"SGX Dividend Screener – {date_str} · "
                f"🟢{buy_count} BUY · 🟡{watch_count} WATCH"
            )

            message = Mail(
                from_email=settings.EMAIL_FROM,
                to_emails=settings.EMAIL_TO,
                subject=subject,
                html_content=html,
            )

            sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
            response = sg.send(message)
            logger.info("Email sent, status=%s", response.status_code)
            return response.status_code in (200, 202)

        except Exception as e:
            logger.error("Failed to send email: %s", e)
            return False


email_service = EmailService()