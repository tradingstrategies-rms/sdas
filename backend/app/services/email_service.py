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


def _render_html(run_result: Dict[str, Any]) -> str:
    date_str = run_result.get("date", datetime.now().strftime("%Y-%m-%d"))
    results: List[Dict] = run_result.get("results", [])
    sti_corr = run_result.get("stiCorrection", 0)

    buy_now = [r for r in results if r["signal"] == "BUY_NOW"]
    watchlist_items = [r for r in results if r["signal"] == "WATCHLIST"]
    overvalued = [r for r in results if r["signal"] == "OVERVALUED"]
    markets = sorted(set(r.get("market", "SGX") for r in results))

    def stock_row(r: Dict, color: str) -> str:
        return f"""
        <tr style="border-bottom:1px solid #f0f0f0;">
          <td style="padding:8px 0;">
            <strong>{r.get('companyName', r['ticker'])}</strong>
            <br><small style="color:#666">{r['ticker']} · {r.get('category','')}</small>
          </td>
          <td style="padding:8px;color:{color};font-weight:bold;">{r['yield']:.1f}%</td>
          <td style="padding:8px;">{r['score']}/19</td>
          <td style="padding:8px;"><strong>SGD {r['amount']:.0f}</strong></td>
        </tr>"""

    def market_section(signal_list: List[Dict], color: str) -> str:
        if not signal_list:
            return "<tr><td colspan='4' style='color:#999;padding:8px'>None today</td></tr>"
        rows = ""
        for market in markets:
            market_stocks = [r for r in signal_list if r.get("market", "SGX") == market]
            if market_stocks:
                rows += f"""
                <tr>
                  <td colspan='4' style='padding:6px 0 2px;font-size:11px;
                  color:#999;text-transform:uppercase;letter-spacing:1px'>
                  {market}
                  </td>
                </tr>"""
                rows += "".join(stock_row(r, color) for r in market_stocks)
        return rows

    buy_rows = market_section(buy_now, "#16a34a")
    watch_rows = market_section(watchlist_items, "#d97706")

    ov_rows = ""
    for r in overvalued:
        ov_rows += f"""
        <tr style="border-bottom:1px solid #f0f0f0;">
          <td style="padding:8px 0;">
            <strong>{r.get('companyName', r['ticker'])}</strong>
            <br><small style="color:#666">{r['ticker']}</small>
          </td>
          <td colspan="3" style="padding:8px;color:#dc2626;font-size:12px">
            {r.get('notes','')}
          </td>
        </tr>"""
    if not ov_rows:
        ov_rows = "<tr><td colspan='4' style='color:#999;padding:8px'>None</td></tr>"

    sti_badge = ""
    if sti_corr >= 20:
        sti_badge = f"MARKET CRASH: STI down {sti_corr:.1f}% — DEPLOY CASH RESERVES"
    elif sti_corr >= 10:
        sti_badge = f"MARKET CORRECTION: STI down {sti_corr:.1f}% — Invest additional SGD 1,000"
    elif sti_corr >= 5:
        sti_badge = f"STI pullback {sti_corr:.1f}%"

    sti_html = ""
    if sti_badge:
        sti_html = f"""
        <div style="background:#fef9c3;border-left:4px solid #ca8a04;
        padding:12px;font-weight:bold">{sti_badge}</div>"""

    return f"""
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family:Arial,sans-serif;max-width:640px;margin:auto;color:#1a1a1a">

  <div style="background:#0f172a;color:white;padding:24px;border-radius:8px 8px 0 0">
    <h1 style="margin:0;font-size:22px">Singapore Dividend Screener</h1>
    <p style="margin:4px 0 0;opacity:0.7;font-size:14px">Daily Signals — {date_str}</p>
  </div>

  {sti_html}

  <div style="padding:20px;background:#f0fdf4;border-left:4px solid #16a34a;
  margin:16px 0;border-radius:4px">
    <h2 style="margin:0 0 12px;color:#15803d">BUY NOW ({len(buy_now)})</h2>
    <table width="100%" style="border-collapse:collapse">
      <thead>
        <tr style="font-size:12px;color:#555;text-transform:uppercase">
          <th align="left">Stock</th>
          <th align="left">Yield</th>
          <th align="left">Score</th>
          <th align="left">Amount</th>
        </tr>
      </thead>
      <tbody>{buy_rows}</tbody>
    </table>
  </div>

  <div style="padding:20px;background:#fffbeb;border-left:4px solid #d97706;
  margin:16px 0;border-radius:4px">
    <h2 style="margin:0 0 12px;color:#b45309">WATCHLIST ({len(watchlist_items)})</h2>
    <table width="100%" style="border-collapse:collapse">
      <thead>
        <tr style="font-size:12px;color:#555;text-transform:uppercase">
          <th align="left">Stock</th>
          <th align="left">Yield</th>
          <th align="left">Score</th>
          <th align="left">Amount</th>
        </tr>
      </thead>
      <tbody>{watch_rows}</tbody>
    </table>
  </div>

  <div style="padding:20px;background:#fef2f2;border-left:4px solid #dc2626;
  margin:16px 0;border-radius:4px">
    <h2 style="margin:0 0 12px;color:#b91c1c">OVERVALUED ({len(overvalued)})</h2>
    <table width="100%" style="border-collapse:collapse">
      <thead>
        <tr style="font-size:12px;color:#555;text-transform:uppercase">
          <th align="left">Stock</th>
          <th colspan="3" align="left">Reason</th>
        </tr>
      </thead>
      <tbody>{ov_rows}</tbody>
    </table>
  </div>

  <div style="padding:16px;background:#f8fafc;border-radius:4px;
  font-size:13px;color:#555;margin-top:8px">
    <p style="margin:0">Goal: SGD 5,000/month passive income</p>
    <p style="margin:4px 0 0">Generated by SDAS</p>
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
                f"Singapore Dividend Screener – {date_str} "
                f"Buy:{buy_count} Watch:{watch_count}"
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