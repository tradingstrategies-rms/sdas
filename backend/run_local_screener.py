"""
Run the screener locally and save results to Firestore.
Use this every weekday evening instead of the Cloud Run endpoint.
"""
import os
from dotenv import load_dotenv
load_dotenv()

from app.services.screener import screener_service
from app.services.email_service import email_service

print("Running SDAS screener locally...")
print()

result = screener_service.run()

print()
print(f"Date:       {result['date']}")
print(f"Processed:  {result['signalsGenerated']} stocks")
print(f"BUY NOW:    {result['buyNow']}")
print(f"WATCHLIST:  {result['watchlist']}")
print(f"OVERVALUED: {result['overvalued']}")
print()

if result['signalsGenerated'] > 0:
    print("Top signals:")
    for r in result['results']:
        if r['signal'] != 'OVERVALUED':
            print(f"  {r['ticker']:12} {r['signal']:10} score={r['score']:2}/19  yield={r['yield']:.1f}%")

    print()
    print("Sending email...")
    sent = email_service.send_daily_signals(result)
    print(f"Email sent: {sent}")
else:
    print("No signals generated — check logs above for errors")