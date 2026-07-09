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


def _parse_breakdown(r: Dict) -> Dict[str, int]:
    """Parse score breakdown from notes or breakdown field."""
    bd = {"trend": 0, "pullback": 0, "dividend": 0, "valuation": 0, "rsi": 0, "mkt": 0}

    # Try dedicated breakdown field first, then notes
    text = r.get("breakdown") or r.get("notes") or ""

    for part in text.split("|"):
        part = part.strip()
        try:
            if "Trend+" in part:
                bd["trend"] = int(part.split("+")[1])
            elif "Pullback+" in part:
                bd["pullback"] = int(part.split("+")[1])
            elif "Dividend+" in part:
                bd["dividend"] = int(part.split("+")[1])
            elif "Valuation+" in part:
                bd["valuation"] = int(part.split("+")[1])
            elif "RSI+" in part:
                bd["rsi"] = int(part.split("+")[1])
            elif "MktCorrection+" in part:
                bd["mkt"] = int(part.split("+")[1])
        except (IndexError, ValueError):
            pass
    return bd


def _cell(val: int, max_val: int) -> str:
    """Coloured score cell."""
    if val == 0:
        color = "#94a3b8"
    elif val >= max_val:
        color = "#16a34a"
    else:
        color = "#f59e0b"
    return (
        f'<td style="text-align:center;padding:5px 3px;'
        f'color:{color};font-weight:bold;font-size:12px">{val}</td>'
    )


def _build_table(stocks: List[Dict], section_color: str, show_reason: bool = False) -> str:
    """Build score breakdown table grouped by market, sorted by score desc."""
    if not stocks:
        return '<p style="color:#999;font-size:13px;padding:8px 0">None today</p>'

    markets = sorted(set(r.get("market", "SGX") for r in stocks))
    html = ""

    for market in markets:
        market_stocks = [r for r in stocks if r.get("market", "SGX") == market]
        market_stocks = sorted(market_stocks, key=lambda x: x.get("score", 0), reverse=True)

        if not market_stocks:
            continue

        html += f"""
        <p style="font-size:10px;color:#94a3b8;text-transform:uppercase;
                  letter-spacing:1px;margin:12px 0 4px;font-weight:600">{market}</p>
        <table width="100%" style="border-collapse:collapse;font-size:12px">
          <thead>
            <tr style="background:#f1f5f9;color:#64748b;font-size:10px;
                       text-transform:uppercase;letter-spacing:0.5px">
              <th style="text-align:left;padding:7px 8px">Stock</th>
              <th style="text-align:center;padding:7px 4px">Yield</th>
              <th style="text-align:center;padding:7px 4px">Total<br>/19</th>
              <th style="text-align:center;padding:7px 4px">Trend<br>/4</th>
              <th style="text-align:center;padding:7px 4px">Pullbk<br>/3</th>
              <th style="text-align:center;padding:7px 4px">Divid<br>/3</th>
              <th style="text-align:center;padding:7px 4px">Val<br>/2</th>
              <th style="text-align:center;padding:7px 4px">RSI<br>/3</th>
              <th style="text-align:center;padding:7px 4px">Mkt<br>/4</th>
              <th style="text-align:center;padding:7px 4px">Deploy</th>
            </tr>
          </thead>
          <tbody>"""

        for i, r in enumerate(market_stocks):
            bd = _parse_breakdown(r)
            bg = "#ffffff" if i % 2 == 0 else "#f8fafc"
            deploy = f"SGD {r['amount']:.0f}" if r.get("amount", 0) > 0 else "—"
            score = r.get("score", 0)
            score_color = "#16a34a" if score >= 13 else "#f59e0b" if score >= 9 else "#ef4444"

            # Show reason for overvalued, score breakdown for others
            reason_html = ""
            if show_reason and r.get("notes"):
                reason_html = f"""
                <tr style="background:#fef2f2">
                  <td colspan="10" style="padding:2px 8px 6px;font-size:10px;
                      color:#dc2626;font-style:italic">
                    ↳ {r['notes']}
                  </td>
                </tr>"""

            html += f"""
            <tr style="background:{bg};border-bottom:1px solid #f1f5f9">
              <td style="padding:7px 8px">
                <strong style="color:#1e293b;font-size:12px">
                  {r.get('companyName', r['ticker'])}
                </strong>
                <br>
	<a href="https://finance.yahoo.com/quote/{r['ticker']}"
                 	target="_blank"
                	 style="color:#94a3b8;font-size:10px;text-decoration:none">
                	{r['ticker']} · {r.get('category', '')} ↗
             	 </a>
              </td>
              <td style="text-align:center;padding:5px 3px;
                  color:{section_color};font-weight:bold">
                {r.get('yield', 0):.1f}%
              </td>
              <td style="text-align:center;padding:5px 3px;
                  font-weight:bold;font-size:13px;color:{score_color}">
                {score}
              </td>
              {_cell(bd['trend'], 4)}
              {_cell(bd['pullback'], 3)}
              {_cell(bd['dividend'], 3)}
              {_cell(bd['valuation'], 2)}
              {_cell(bd['rsi'], 3)}
              {_cell(bd['mkt'], 4)}
              <td style="text-align:center;padding:5px 3px;
                  font-weight:bold;color:#1e293b;font-size:11px">
                {deploy}
              </td>
            </tr>
            {reason_html}"""

        html += "</tbody></table>"

    return html


def _render_html(run_result: Dict[str, Any]) -> str:
    date_str = run_result.get("date", datetime.now().strftime("%Y-%m-%d"))
    results: List[Dict] = run_result.get("results", [])
    sti_corr = run_result.get("stiCorrection", 0)

    buy_now = [r for r in results if r["signal"] == "BUY_NOW"]
    watchlist = [r for r in results if r["signal"] == "WATCHLIST"]
    overvalued = [r for r in results if r["signal"] == "OVERVALUED"]
    total_deploy = sum(r.get("amount", 0) for r in results)

    sti_badge = ""
    if sti_corr >= 20:
        sti_badge = f"🚨 MARKET CRASH: STI down {sti_corr:.1f}% — DEPLOY CASH RESERVES"
    elif sti_corr >= 10:
        sti_badge = f"⚠️ MARKET CORRECTION: STI down {sti_corr:.1f}% — Invest SGD 1,000 extra"
    elif sti_corr >= 5:
        sti_badge = f"📉 STI pullback {sti_corr:.1f}% from 52w high"

    sti_html = f"""
    <div style="background:#fef9c3;border-left:4px solid #ca8a04;
        padding:12px 16px;font-weight:bold;font-size:13px">
        {sti_badge}
    </div>""" if sti_badge else ""

    return f"""
<!DOCTYPE html>
<html>
<head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
</head>
<body style="font-family:Arial,sans-serif;max-width:820px;margin:auto;
             background:#f8fafc;padding:16px;color:#1a1a1a">

  <div style="background:#0f172a;color:white;padding:22px 24px;
              border-radius:10px 10px 0 0">
    <h1 style="margin:0;font-size:20px;font-weight:700">
      📊 Singapore Dividend Screener
    </h1>
    <p style="margin:5px 0 0;opacity:0.55;font-size:12px">
      Daily Signals — {date_str}
    </p>
  </div>

  <div style="background:#1e293b;padding:10px 24px;display:flex;
              gap:24px;flex-wrap:wrap;border-radius:0">
    <span style="color:#4ade80;font-size:12px;font-weight:600">
      🟢 BUY NOW: {len(buy_now)}
    </span>
    <span style="color:#fbbf24;font-size:12px;font-weight:600">
      🟡 WATCHLIST: {len(watchlist)}
    </span>
    <span style="color:#f87171;font-size:12px;font-weight:600">
      🔴 OVERVALUED: {len(overvalued)}
    </span>
    <span style="color:#94a3b8;font-size:12px">
      💰 Deploy today: SGD {total_deploy:,.0f}
    </span>
    <span style="color:#94a3b8;font-size:12px">
      📈 STI correction: {sti_corr:.1f}%
    </span>
  </div>

  {sti_html}

  <!-- BUY NOW -->
  <div style="background:#fff;border-left:4px solid #16a34a;
              margin:12px 0;border-radius:0 6px 6px 0;
              box-shadow:0 1px 3px rgba(0,0,0,0.06);overflow:hidden">
    <div style="background:#f0fdf4;padding:12px 20px;
                border-bottom:1px solid #dcfce7">
      <h2 style="margin:0;color:#15803d;font-size:15px">
        🟢 BUY NOW ({len(buy_now)})
        <span style="font-size:11px;font-weight:normal;
                     color:#86efac;margin-left:8px">
          Score ≥ 13 · Yield ≥ min · Price above SMA200 · Deploy SGD 750
        </span>
      </h2>
    </div>
    <div style="padding:12px 20px;overflow-x:auto">
      {_build_table(buy_now, "#16a34a")}
    </div>
  </div>

  <!-- WATCHLIST -->
  <div style="background:#fff;border-left:4px solid #d97706;
              margin:12px 0;border-radius:0 6px 6px 0;
              box-shadow:0 1px 3px rgba(0,0,0,0.06);overflow:hidden">
    <div style="background:#fffbeb;padding:12px 20px;
                border-bottom:1px solid #fef3c7">
      <h2 style="margin:0;color:#b45309;font-size:15px">
        🟡 WATCHLIST ({len(watchlist)})
        <span style="font-size:11px;font-weight:normal;
                     color:#fcd34d;margin-left:8px">
          Score 9–12 · Yield ≥ min · Price above SMA200 · Deploy SGD 500
        </span>
      </h2>
    </div>
    <div style="padding:12px 20px;overflow-x:auto">
      {_build_table(watchlist, "#d97706")}
    </div>
  </div>

  <!-- OVERVALUED — show all with reason -->
  <div style="background:#fff;border-left:4px solid #dc2626;
              margin:12px 0;border-radius:0 6px 6px 0;
              box-shadow:0 1px 3px rgba(0,0,0,0.06);overflow:hidden">
    <div style="background:#fef2f2;padding:12px 20px;
                border-bottom:1px solid #fee2e2">
      <h2 style="margin:0;color:#b91c1c;font-size:15px">
        🔴 OVERVALUED / SKIP ({len(overvalued)})
      </h2>
    </div>
    <div style="padding:12px 20px;overflow-x:auto">
      {_build_table(overvalued, "#ef4444", show_reason=True)}
    </div>
  </div>

  <!-- Score legend -->
  <div style="background:#fff;border-radius:6px;padding:14px 20px;
              margin:12px 0;box-shadow:0 1px 3px rgba(0,0,0,0.06)">
    <p style="margin:0 0 8px;font-size:10px;color:#64748b;
              text-transform:uppercase;letter-spacing:1px;font-weight:600">
      Score Legend (max 19)
    </p>
    <table style="font-size:11px;color:#475569;border-collapse:collapse;
                  width:100%">
      <tr>
        <td style="padding:3px 12px 3px 0;white-space:nowrap">
          📈 <strong>Trend</strong> /4
        </td>
        <td style="padding:3px 12px 3px 0;color:#94a3b8">
          Price vs SMA50 + SMA200
        </td>
        <td style="padding:3px 12px 3px 0;white-space:nowrap">
          📉 <strong>Pullback</strong> /3
        </td>
        <td style="padding:3px 0;color:#94a3b8">
          Drawdown from 52w high
        </td>
      </tr>
      <tr>
        <td style="padding:3px 12px 3px 0;white-space:nowrap">
          💰 <strong>Dividend</strong> /3
        </td>
        <td style="padding:3px 12px 3px 0;color:#94a3b8">
          Category yield thresholds
        </td>
        <td style="padding:3px 12px 3px 0;white-space:nowrap">
          📊 <strong>Valuation</strong> /2
        </td>
        <td style="padding:3px 0;color:#94a3b8">
          PB vs 5-year average
        </td>
      </tr>
      <tr>
        <td style="padding:3px 12px 3px 0;white-space:nowrap">
          🔻 <strong>RSI</strong> /3
        </td>
        <td style="padding:3px 12px 3px 0;color:#94a3b8">
          Oversold signal (&lt;50)
        </td>
        <td style="padding:3px 12px 3px 0;white-space:nowrap">
          🌏 <strong>Mkt Corr</strong> /4
        </td>
        <td style="padding:3px 0;color:#94a3b8">
          STI correction bonus
        </td>
      </tr>
    </table>
  </div>

  <div style="text-align:center;font-size:10px;color:#94a3b8;padding:8px 0">
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
            total = run_result.get("signalsGenerated", 0)

            subject = (
                f"SGX Screener {date_str} · "
                f"🟢{buy_count} BUY · 🟡{watch_count} WATCH · "
                f"{total} stocks screened"
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