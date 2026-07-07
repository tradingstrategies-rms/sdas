from app.services.market_data import market_data_service

print("=" * 50)
print("Testing Yahoo Finance - D05.SI")
print("=" * 50)

import yfinance as yf
tk = yf.Ticker("D05.SI")
hist = tk.history(period="1y")
print(f"Rows returned: {len(hist)}")
print(f"Last 3 rows:")
print(hist.tail(3))
print()

info = tk.info
print(f"dividendYield from info: {info.get('dividendYield')}")
print(f"trailingAnnualDividendYield: {info.get('trailingAnnualDividendYield')}")
print()

data = market_data_service.get_stock_data("D05.SI")
print(f"market_data_service result: {data}")