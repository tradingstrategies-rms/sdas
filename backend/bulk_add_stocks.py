import requests
import json

API_URL = "https://sdas-backend-697410035825.asia-southeast1.run.app"

stocks = [
  {"ticker": "C6L.SI", "companyName": "Singapore Airlines", "sector": "Airlines", "category": "Equity", "market": "SGX", "currency": "SGD", "targetYield": 4.0, "minYield": 3.0, "active": True},
  {"ticker": "OV8.SI", "companyName": "Sheng Siong Group", "sector": "Consumer Staples", "category": "Equity", "market": "SGX", "currency": "SGD", "targetYield": 4.0, "minYield": 3.0, "active": True},
  {"ticker": "BS6.SI", "companyName": "Yangzijiang Shipbuilding", "sector": "Industrials", "category": "Equity", "market": "SGX", "currency": "SGD", "targetYield": 4.0, "minYield": 3.0, "active": True},
  {"ticker": "S61.SI", "companyName": "ST Engineering", "sector": "Industrials", "category": "Equity", "market": "SGX", "currency": "SGD", "targetYield": 4.0, "minYield": 3.0, "active": True},
  {"ticker": "CY6U.SI", "companyName": "Cromwell European REIT", "sector": "Industrial REIT", "category": "REIT", "market": "SGX", "currency": "SGD", "targetYield": 7.0, "minYield": 5.5, "active": True},
  {"ticker": "9A4U.SI", "companyName": "Manulife US REIT", "sector": "Office REIT", "category": "REIT", "market": "SGX", "currency": "SGD", "targetYield": 6.0, "minYield": 5.0, "active": True},
  {"ticker": "BEC.SI", "companyName": "Bumitama Agri", "sector": "Agriculture", "category": "Equity", "market": "SGX", "currency": "SGD", "targetYield": 5.0, "minYield": 3.5, "active": True},
  {"ticker": "P34.SI", "companyName": "Petra Foods", "sector": "Consumer", "category": "Equity", "market": "SGX", "currency": "SGD", "targetYield": 4.0, "minYield": 3.0, "active": True},
  {"ticker": "TQ5.SI", "companyName": "Frencken Group", "sector": "Technology", "category": "Equity", "market": "SGX", "currency": "SGD", "targetYield": 4.0, "minYield": 3.0, "active": True},
  {"ticker": "AP4.SI", "companyName": "Centurion Corporation", "sector": "Real Estate", "category": "Equity", "market": "SGX", "currency": "SGD", "targetYield": 5.0, "minYield": 3.5, "active": True},
  {"ticker": "J85.SI", "companyName": "Intraco", "sector": "Industrials", "category": "Equity", "market": "SGX", "currency": "SGD", "targetYield": 4.0, "minYield": 3.0, "active": True},
  {"ticker": "AWZ.SI", "companyName": "Affluent Medical", "sector": "Healthcare", "category": "Equity", "market": "SGX", "currency": "SGD", "targetYield": 3.0, "minYield": 2.0, "active": True},
  {"ticker": "YF8.SI", "companyName": "Yanlord Land Group", "sector": "Real Estate", "category": "Equity", "market": "SGX", "currency": "SGD", "targetYield": 4.0, "minYield": 3.0, "active": True},
  {"ticker": "42E.SI", "companyName": "mm2 Asia", "sector": "Media", "category": "Equity", "market": "SGX", "currency": "SGD", "targetYield": 3.0, "minYield": 2.0, "active": True},
  {"ticker": "8AZ.SI", "companyName": "Winning International Group", "sector": "Industrials", "category": "Equity", "market": "SGX", "currency": "SGD", "targetYield": 3.0, "minYield": 2.0, "active": True},
  {"ticker": "JPM", "companyName": "JPMorgan Chase", "sector": "Financials", "category": "Bank", "market": "US", "currency": "USD", "targetYield": 2.5, "minYield": 2.0, "active": True},
  {"ticker": "AAPL", "companyName": "Apple Inc", "sector": "Technology", "category": "Equity", "market": "US", "currency": "USD", "targetYield": 0.5, "minYield": 0.0, "active": True},
  {"ticker": "MSFT", "companyName": "Microsoft Corporation", "sector": "Technology", "category": "Equity", "market": "US", "currency": "USD", "targetYield": 0.8, "minYield": 0.0, "active": True},
  {"ticker": "NVDA", "companyName": "NVIDIA Corporation", "sector": "Technology", "category": "Equity", "market": "US", "currency": "USD", "targetYield": 0.1, "minYield": 0.0, "active": True},
  {"ticker": "QCOM", "companyName": "Qualcomm", "sector": "Technology", "category": "Equity", "market": "US", "currency": "USD", "targetYield": 2.0, "minYield": 1.5, "active": True},
  {"ticker": "MCD", "companyName": "McDonald's Corporation", "sector": "Consumer Discretionary", "category": "Equity", "market": "US", "currency": "USD", "targetYield": 2.5, "minYield": 2.0, "active": True},
  {"ticker": "BTI", "companyName": "British American Tobacco", "sector": "Consumer Staples", "category": "Equity", "market": "US", "currency": "USD", "targetYield": 8.0, "minYield": 6.0, "active": True},
  {"ticker": "AMZN", "companyName": "Amazon.com", "sector": "Technology", "category": "Equity", "market": "US", "currency": "USD", "targetYield": 0.0, "minYield": 0.0, "active": True},
  {"ticker": "TSLA", "companyName": "Tesla Inc", "sector": "Automotive", "category": "Equity", "market": "US", "currency": "USD", "targetYield": 0.0, "minYield": 0.0, "active": True},
  {"ticker": "PLTR", "companyName": "Palantir Technologies", "sector": "Technology", "category": "Equity", "market": "US", "currency": "USD", "targetYield": 0.0, "minYield": 0.0, "active": True},
  {"ticker": "SNOW", "companyName": "Snowflake Inc", "sector": "Technology", "category": "Equity", "market": "US", "currency": "USD", "targetYield": 0.0, "minYield": 0.0, "active": True},
  {"ticker": "CRM", "companyName": "Salesforce Inc", "sector": "Technology", "category": "Equity", "market": "US", "currency": "USD", "targetYield": 0.5, "minYield": 0.0, "active": True},
  {"ticker": "META", "companyName": "Meta Platforms", "sector": "Technology", "category": "Equity", "market": "US", "currency": "USD", "targetYield": 0.4, "minYield": 0.0, "active": True},
  {"ticker": "GOOG", "companyName": "Alphabet Inc", "sector": "Technology", "category": "Equity", "market": "US", "currency": "USD", "targetYield": 0.5, "minYield": 0.0, "active": True},
  {"ticker": "ORCL", "companyName": "Oracle Corporation", "sector": "Technology", "category": "Equity", "market": "US", "currency": "USD", "targetYield": 1.0, "minYield": 0.0, "active": True},
  {"ticker": "TSM", "companyName": "Taiwan Semiconductor", "sector": "Technology", "category": "Equity", "market": "US", "currency": "USD", "targetYield": 1.5, "minYield": 1.0, "active": True},
  {"ticker": "BABA", "companyName": "Alibaba Group", "sector": "Technology", "category": "Equity", "market": "US", "currency": "USD", "targetYield": 0.0, "minYield": 0.0, "active": True},
  {"ticker": "HDB", "companyName": "HDFC Bank", "sector": "Financials", "category": "Bank", "market": "US", "currency": "USD", "targetYield": 1.0, "minYield": 0.5, "active": True},
  {"ticker": "NKE", "companyName": "Nike Inc", "sector": "Consumer Discretionary", "category": "Equity", "market": "US", "currency": "USD", "targetYield": 2.5, "minYield": 2.0, "active": True},
  {"ticker": "ARM", "companyName": "Arm Holdings", "sector": "Technology", "category": "Equity", "market": "US", "currency": "USD", "targetYield": 0.0, "minYield": 0.0, "active": True},
  {"ticker": "SMCI", "companyName": "Super Micro Computer", "sector": "Technology", "category": "Equity", "market": "US", "currency": "USD", "targetYield": 0.0, "minYield": 0.0, "active": True},
  {"ticker": "SOUN", "companyName": "SoundHound AI", "sector": "Technology", "category": "Equity", "market": "US", "currency": "USD", "targetYield": 0.0, "minYield": 0.0, "active": True},
  {"ticker": "CMG", "companyName": "Chipotle Mexican Grill", "sector": "Consumer Discretionary", "category": "Equity", "market": "US", "currency": "USD", "targetYield": 0.0, "minYield": 0.0, "active": True},
  {"ticker": "ZBRA", "companyName": "Zebra Technologies", "sector": "Technology", "category": "Equity", "market": "US", "currency": "USD", "targetYield": 0.0, "minYield": 0.0, "active": True},
  {"ticker": "LITE", "companyName": "Lumentum Holdings", "sector": "Technology", "category": "Equity", "market": "US", "currency": "USD", "targetYield": 0.0, "minYield": 0.0, "active": True},
  {"ticker": "IPGP", "companyName": "IPG Photonics", "sector": "Technology", "category": "Equity", "market": "US", "currency": "USD", "targetYield": 0.0, "minYield": 0.0, "active": True},
  {"ticker": "FRSH", "companyName": "Freshworks Inc", "sector": "Technology", "category": "Equity", "market": "US", "currency": "USD", "targetYield": 0.0, "minYield": 0.0, "active": True},
  {"ticker": "KTOS", "companyName": "Kratos Defense", "sector": "Defense", "category": "Equity", "market": "US", "currency": "USD", "targetYield": 0.0, "minYield": 0.0, "active": True},
  {"ticker": "QDEL", "companyName": "QuidelOrtho Corporation", "sector": "Healthcare", "category": "Equity", "market": "US", "currency": "USD", "targetYield": 0.0, "minYield": 0.0, "active": True},
  {"ticker": "CPNG", "companyName": "Coupang Inc", "sector": "Consumer Discretionary", "category": "Equity", "market": "US", "currency": "USD", "targetYield": 0.0, "minYield": 0.0, "active": True},
  {"ticker": "ZBH", "companyName": "Zimmer Biomet Holdings", "sector": "Healthcare", "category": "Equity", "market": "US", "currency": "USD", "targetYield": 1.0, "minYield": 0.8, "active": True},
  {"ticker": "NFLX", "companyName": "Netflix Inc", "sector": "Technology", "category": "Equity", "market": "US", "currency": "USD", "targetYield": 0.0, "minYield": 0.0, "active": True},
]

print(f"Adding {len(stocks)} stocks...")
success = 0
failed = []

for stock in stocks:
    try:
        r = requests.post(f"{API_URL}/api/v1/stocks/", json=stock)
        if r.status_code == 200:
            print(f"  OK {stock['ticker']}")
            success += 1
        else:
            print(f"  FAILED {stock['ticker']}: {r.text}")
            failed.append(stock['ticker'])
    except Exception as e:
        print(f"  ERROR {stock['ticker']}: {e}")
        failed.append(stock['ticker'])

print(f"\nDone: {success} added, {len(failed)} failed")
if failed:
    print(f"Failed tickers: {failed}")