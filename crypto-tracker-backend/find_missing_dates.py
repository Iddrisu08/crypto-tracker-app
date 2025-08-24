import json
from datetime import datetime, timedelta

# Load price cache
with open('price_cache.json', 'r') as f:
    price_cache = json.load(f)

START_DATE = datetime(2025, 1, 25)
TODAY = datetime.now()

print("=== CHECKING FOR MISSING WEEKLY DATES ===")
current_date = START_DATE
weeks = 0
missing_dates = []
found_dates = []

while current_date <= TODAY:
    date_str = current_date.strftime('%d-%m-%Y')
    
    if date_str in price_cache:
        found_dates.append(date_str)
        print(f"Week {weeks}: {date_str} ✅ FOUND")
    else:
        missing_dates.append(date_str)
        print(f"Week {weeks}: {date_str} ❌ MISSING")
    
    current_date += timedelta(weeks=1)
    weeks += 1
    
    if weeks > 25:  # Safety break
        break

print(f"\n=== SUMMARY ===")
print(f"Total expected weeks: {weeks}")
print(f"Found dates: {len(found_dates)}")
print(f"Missing dates: {len(missing_dates)}")
print(f"Missing dates list: {missing_dates}")

# Calculate what the investments should be based on found dates
btc_purchases = len(found_dates)
eth_purchases = sum(1 for i, date in enumerate(found_dates) if i % 2 == 0)

print(f"\nBased on FOUND dates:")
print(f"BTC purchases: {btc_purchases}")
print(f"ETH purchases: {eth_purchases}")
print(f"Expected BTC invested: ${btc_purchases * 102}")
print(f"Expected ETH invested: ${eth_purchases * 51.8}")
