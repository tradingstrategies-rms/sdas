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
    """Build the HTML email body from screening results."""
    date_str = run_result.get("date", datetime.now().strftime("%Y-%m-%d"))
    results: List[Dict] = run_result.get("results", [])
    sti_corr = run_result.get("stiCorrection", 0)

    buy_now = [r for r in results if r["signal"] == "BUY_NOW"]
    watchlist_items = [r for r in results if r["signal"] == "WATCHLIST"]
    overvalued = [r for r in results if r["signal"] == "OVERVALUED"]

    def stock_row(r: Dict, color: str, show_amount: bool = True) -> str:
        amount_html = f"<td><strong>SGD {r['amount']:.0f}</strong></td>" if show_amount else ""
        return f"""
        <tr style="border-bottom:1px solid #f0f0f0;">
          <td style="padding:8px 0;"><strong>{r.get('companyName', r['ticker'])}</strong>
            <br><small style="color:#666">{r['ticker']} · {r.get('category','')}</small></td>
          <td style="padding:8px;color:{color};font-weight:bold;">{r['yield']:.1f}%</td>
          <td style="padding:8px;">{r['score']}/19</td>
          {amount_html if show_amount else '<td></td>'}
        </tr>"""

    buy_rows = "".join(stock_row(r, "#16a34a") for r in buy_now) if buy_now else \
        "<tr><td colspan='4' style='color:#999;padding:8px'>No BUY NOW signals today</td></tr>"

    watch_rows = "".join(stock_row(r, "#d97706") for r in watchlist_items) if watchlist_items else \
        "<tr><td colspan='4' style='color:#999;padding:8px'>No WATCHLIST signals today</td></tr>"

    ov_rows = ""
    for r in overvalued:
        ov_rows += f"""
        <tr style="border-bottom:1px solid #f0f0f0;">
          <td style="padding:8px 0;"><strong>{r.get('companyName', r['ticker'])}</strong>
            <br><small style="color:#666">{r['ticker']}</small></td>
          <td colspan="3" style="padding:8px;color:#dc2626;font-size:12px">{r.get('notes','')}</td>
        </tr>"""
    if not ov_rows:
        ov_rows = "<tr><td colspan='4' style='color:#999;padding:8px'>None</td></tr>"

    sti_badge = ""
    if sti_corr >= 20:
        sti_badge = f"🚨 MARKET CRASH: STI down {sti_corr:.1f}% — DEPLOY CASH RESERVES"
    elif sti_corr >= 10:
        sti_badge = f"⚠️ MARKET CORRECTION: STI down {sti_corr:.1f}% — Invest additional SGD 1,000"
    elif sti_corr >= 5:
        sti_badge = f"📉 STI pullback {sti_corr:.1f}%"

    return f"""
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family:Arial,sans-serif;max-width:640px;margin:auto;color:#1a1a1a">
  <div style="background:#0f172a;color:white;padding:24px;border-radius:8px 8px 0 0">
    <h1 style="margin:0;font-size:22px">📊 Singapore Dividend Screener</h1>
    <p style="margin:4px 0 0;opacity:0.7;font-size:14px">Daily Signals — {date_str}</p>
  </div>

  {"<div style='background:#fef9c3;border-left:4px solid #ca8a04;padding:12px;font-weight:bold'>" + sti_badge + "</div>" if sti_badge else ""}

  <!-- BUY NOW -->
  <div style="padding:20px;background:#f0fdf4;border-left:4px solid #16a34a;margin:16px 0;border-radius:4px">
    <h2 style="margin:0 0 12px;color:#15803d">🟢 BUY NOW ({len(buy_now)})</h2>
    <table width="100%" style="border-collapse:collapse">
      <thead><tr style="font-size:12px;color:#555;text-transform:uppercase">
        <th align="left">Stock</th><th align="left">Yield</th><th align="left">Score</th><th align="left">Amount</th>
      </tr></thead>
      <tbody>{buy_rows}</tbody>
    </table>
  </div>

  <!-- WATCHLIST -->
  <div style="padding:20px;background:#fffbeb;border-left:4px solid #d97706;margin:16px 0;border-radius:4px">
    <h2 style="margin:0 0 12px;color:#b45309">🟡 WATCHLIST ({len(watchlist_items)})</h2>
    <table width="100%" style="border-collapse:collapse">
      <thead><tr style="font-size:12px;color:#555;text-transform:uppercase">
        <th align="left">Stock</th><th align="left">Yield</th><th align="left">Score</th><th align="left">Amount</th>
      </tr></thead>
      <tbody>{watch_rows}</tbody>
    </table>
  </div>

  <!-- OVERVALUED -->
  <div style="padding:20px;background:#fef2f2;border-left:4px solid #dc2626;margin:16px 0;border-radius:4px">
    <h2 style="margin:0 0 12px;color:#b91c1c">🔴 OVERVALUED / SKIP ({len(overvalued)})</h2>
    <table width="100%" style="border-collapse:collapse">
      <thead><tr style="font-size:12px;color:#555;text-transform:uppercase">
        <th align="left">Stock</th><th colspan="3" align="left">Reason</th>
      </tr></thead>
      <tbody>{ov_rows}</tbody>
    </table>
  </div>

  <div style="padding:16px;background:#f8fafc;border-radius:4px;font-size:13px;color:#555;margin-top:8px">
    <p style="margin:0">🎯 <strong>Goal:</strong> SGD 5,000/month passive income</p>
    <p style="margin:4px 0 0">Generated by SDAS — Singapore Dividend Accumulation Screener</p>
  </div>
</body>
</html>"""


class EmailService:

    def send_daily_signals(self, run_result: Dict[str, Any]) -> bool:
        """Send the daily signals email. Returns True on success."""
        try:
            html = _render_html(run_result)
            date_str = run_result.get("date", "")
            buy_count = run_result.get("buyNow", 0)
            watch_count = run_result.get("watchlist", 0)

            subject = (
                f"Singapore Dividend Screener – Daily Signals [{date_str}] "
                f"🟢{buy_count} 🟡{watch_count}"
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
