import json
from datetime import datetime, timedelta

# Constants from app.py
START_DATE = datetime(2025, 1, 25)
TODAY = datetime.now()
DEFAULT_BTC_INVEST = 100
DEFAULT_ETH_INVEST = 50
DEFAULT_BTC_TOTAL = 102  # $100 + $2 fee
DEFAULT_ETH_TOTAL = 51.8  # $50 + $1.8 fee

def load_manual_transactions():
    with open('manual_transactions.json', 'r') as f:
        return json.load(f)

def simulate_investments():
    btc_total_usd, eth_total_usd = 0, 0
    btc_held, eth_held = 0, 0
    current_date = START_DATE
    weeks = 0
    
    print("=== SIMULATING WEEKLY/BI-WEEKLY INVESTMENTS ===")
    
    while current_date <= TODAY:
        # Simulate price data (we'll use dummy prices for this debug)
        btc_price = 100000  # Dummy price
        eth_price = 4000    # Dummy price
        
        # Buy Bitcoin every week
        btc_held += DEFAULT_BTC_INVEST / btc_price
        btc_total_usd += DEFAULT_BTC_TOTAL  # Include fees in total cost
        print(f"Week {weeks}: BTC purchase - ${DEFAULT_BTC_TOTAL} (total: ${btc_total_usd})")

        # Buy Ethereum every 2 weeks (bi-weekly)
        if weeks % 2 == 0:  # Every even week (0, 2, 4, 6...)
            eth_held += DEFAULT_ETH_INVEST / eth_price
            eth_total_usd += DEFAULT_ETH_TOTAL  # Include fees in total cost
            print(f"Week {weeks}: ETH purchase - ${DEFAULT_ETH_TOTAL} (total: ${eth_total_usd})")

        current_date += timedelta(weeks=1)
        weeks += 1
        
        if weeks > 25:  # Safety break
            break

    print(f"\nAfter simulation:")
    print(f"BTC invested: ${btc_total_usd}")
    print(f"ETH invested: ${eth_total_usd}")
    print(f"BTC held: {btc_held}")
    print(f"ETH held: {eth_held}")
    
    return btc_total_usd, eth_total_usd, btc_held, eth_held

def apply_manual_transactions(btc_held, eth_held, btc_total_usd, eth_total_usd):
    print("\n=== APPLYING MANUAL TRANSACTIONS ===")
    transactions = load_manual_transactions()
    
    print(f"Before manual transactions:")
    print(f"BTC held: {btc_held}, BTC invested: ${btc_total_usd}")
    print(f"ETH held: {eth_held}, ETH invested: ${eth_total_usd}")
    
    for i, tx in enumerate(transactions):
        try:
            amount = float(tx['amount'])
            price = float(tx['price'])
            total_value = amount * price
            
            print(f"\nTransaction {i+1}:")
            print(f"  Date: {tx['date']}")
            print(f"  Coin: {tx['coin']}")
            print(f"  Amount: {amount}")
            print(f"  Price: ${price}")
            print(f"  Total Value: ${total_value}")
            
            if tx['coin'] == 'bitcoin':
                btc_held += amount
                btc_total_usd += total_value
                print(f"  Updated BTC held: {btc_held}")
                print(f"  Updated BTC invested: ${btc_total_usd}")
            elif tx['coin'] == 'ethereum':
                eth_held += amount
                eth_total_usd += total_value
                print(f"  Updated ETH held: {eth_held}")
                print(f"  Updated ETH invested: ${eth_total_usd}")
        except Exception as e:
            print(f"Error processing transaction: {e}")
            continue
    
    print(f"\nAfter manual transactions:")
    print(f"BTC held: {btc_held}, BTC invested: ${btc_total_usd}")
    print(f"ETH held: {eth_held}, ETH invested: ${eth_total_usd}")
    
    return btc_held, eth_held, btc_total_usd, eth_total_usd

# Run the simulation
btc_invested, eth_invested, btc_held, eth_held = simulate_investments()
btc_held, eth_held, btc_invested, eth_invested = apply_manual_transactions(
    btc_held, eth_held, btc_invested, eth_invested
)

print(f"\n=== FINAL RESULTS ===")
print(f"Final BTC invested: ${btc_invested}")
print(f"Final ETH invested: ${eth_invested}")
print(f"Final BTC held: {btc_held}")
print(f"Final ETH held: {eth_held}")
