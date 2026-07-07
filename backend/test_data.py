from app.services.market_data import market_data_service

print("Testing Yahoo Finance connection...")
print()

# Test one SGX stock
print("Testing D05.SI (DBS)...")
data = market_data_service.get_stock_data('D05.SI')
if data:
    print(f"  Price:     {data['price']}")
    print(f"  Yield:     {data['dividendYield']}%")
    print(f"  SMA200:    {data['sma200']}")
    print(f"  RSI:       {data['rsi14']}")
    print(f"  Drawdown:  {data['drawdownPercent']}%")
    print("  STATUS: OK")
else:
    print("  STATUS: FAILED - no data returned")

print()

# Test one US stock
print("Testing AAPL...")
data2 = market_data_service.get_stock_data('AAPL')
if data2:
    print(f"  Price:     {data2['price']}")
    print(f"  Yield:     {data2['dividendYield']}%")
    print("  STATUS: OK")
else:
    print("  STATUS: FAILED - no data returned")