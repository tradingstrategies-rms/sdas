"""
Seed script — populates Firestore with the 14 watchlist stocks.
Run once: python seed.py
Requires .env to be configured.
"""

from dotenv import load_dotenv
load_dotenv()

from app.db.firebase import init_firebase, get_db

STOCKS = [
    {"ticker": "D05.SI",  "companyName": "DBS Group Holdings",                    "sector": "Financials",       "category": "Bank",           "targetYield": 5.0, "active": True},
    {"ticker": "U11.SI",  "companyName": "United Overseas Bank",                  "sector": "Financials",       "category": "Bank",           "targetYield": 5.0, "active": True},
    {"ticker": "Z74.SI",  "companyName": "Singapore Telecommunications",           "sector": "Communications",   "category": "Equity",         "targetYield": 5.5, "active": True},
    {"ticker": "S58.SI",  "companyName": "SATS Ltd",                               "sector": "Industrials",      "category": "Equity",         "targetYield": 4.5, "active": True},
    {"ticker": "C07.SI",  "companyName": "Jardine Cycle & Carriage",               "sector": "Consumer",         "category": "Equity",         "targetYield": 4.0, "active": True},
    {"ticker": "9CI.SI",  "companyName": "CapitaLand Investment",                  "sector": "Real Estate",      "category": "Equity",         "targetYield": 4.5, "active": True},
    {"ticker": "A17U.SI", "companyName": "Ascendas Real Estate Investment Trust",  "sector": "Industrial REIT",  "category": "REIT",           "targetYield": 5.5, "active": True},
    {"ticker": "C38U.SI", "companyName": "CapitaLand Integrated Commercial Trust", "sector": "Retail REIT",      "category": "REIT",           "targetYield": 5.5, "active": True},
    {"ticker": "AJBU.SI", "companyName": "Keppel Infrastructure Trust",            "sector": "Infrastructure",   "category": "Infrastructure", "targetYield": 7.0, "active": True},
    {"ticker": "HMN.SI",  "companyName": "Frasers Centrepoint Trust",              "sector": "Retail REIT",      "category": "REIT",           "targetYield": 6.0, "active": True},
    {"ticker": "M44U.SI", "companyName": "Mapletree Industrial Trust",             "sector": "Industrial REIT",  "category": "REIT",           "targetYield": 5.5, "active": True},
    {"ticker": "C2PU.SI", "companyName": "Mapletree Pan Asia Commercial Trust",    "sector": "Office REIT",      "category": "REIT",           "targetYield": 6.5, "active": True},
    {"ticker": "J69U.SI", "companyName": "Frasers Logistics & Commercial Trust",   "sector": "Industrial REIT",  "category": "REIT",           "targetYield": 6.5, "active": True},
    {"ticker": "A7RU.SI", "companyName": "Keppel DC REIT",                         "sector": "Data Centre REIT", "category": "REIT",           "targetYield": 5.5, "active": True},
]

def seed():
    print("Initialising Firebase...")
    init_firebase()
    db = get_db()

    print(f"Seeding {len(STOCKS)} stocks...")
    for stock in STOCKS:
        db.collection("stocks").document(stock["ticker"]).set(stock)
        print(f"  ✓ {stock['ticker']} — {stock['companyName']}")

    # Seed empty portfolio document
    db.collection("portfolio").document("current").set({
        "totalInvested": 0,
        "marketValue": 0,
        "annualDividend": 0,
        "monthlyDividend": 0,
        "yieldOnCost": 0,
        "cashReserve": 10000,  # Initial cash
    }, merge=True)
    print("  ✓ Portfolio document initialised")

    print("\nSeed complete!")


if __name__ == "__main__":
    seed()
