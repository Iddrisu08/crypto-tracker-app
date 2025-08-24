from datetime import datetime, timedelta

START_DATE = datetime(2025, 1, 25)
TODAY = datetime.now()

print(f'Start Date: {START_DATE}')
print(f'Today: {TODAY}')
print(f'Days difference: {(TODAY - START_DATE).days}')
print(f'Weeks difference: {(TODAY - START_DATE).days / 7:.1f}')

# Simulate the current logic
current_date = START_DATE
weeks = 0
btc_purchases = 0
eth_purchases = 0

print("\nSimulating purchases:")
while current_date <= TODAY:
    print(f"Week {weeks}: {current_date.strftime('%Y-%m-%d')}")
    
    # Buy Bitcoin every week
    btc_purchases += 1
    print(f"  - BTC purchase #{btc_purchases}")
    
    # Buy Ethereum every 2 weeks (bi-weekly)
    if weeks % 2 == 0:  # Every even week (0, 2, 4, 6...)
        eth_purchases += 1
        print(f"  - ETH purchase #{eth_purchases}")
    
    current_date += timedelta(weeks=1)
    weeks += 1
    
    if weeks > 30:  # Safety break
        break

print(f"\nTotal BTC purchases: {btc_purchases}")
print(f"Total ETH purchases: {eth_purchases}")
print(f"Expected BTC invested: ${btc_purchases * 100} (with fees: ${btc_purchases * 102})")
print(f"Expected ETH invested: ${eth_purchases * 50} (with fees: ${eth_purchases * 51.8})")
