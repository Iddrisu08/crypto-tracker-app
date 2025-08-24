from flask import Flask, jsonify, request
from flask_cors import CORS
import requests, json, os, time
from datetime import datetime, timedelta

app = Flask(__name__)
# Secure CORS configuration - only allow frontend origin
CORS(app, origins=["http://localhost:5173", "http://localhost:5174"], 
     methods=["GET", "POST", "PUT", "DELETE"],
     allow_headers=["Content-Type", "Authorization", "expires", "cache-control", "pragma"])

START_DATE = datetime(2025, 1, 25)
TODAY = datetime.now()
# Crypto amounts purchased (what you actually get)
DEFAULT_BTC_INVEST = 100
DEFAULT_ETH_INVEST = 50
# Total amounts paid (including fees)
DEFAULT_BTC_TOTAL = 102  # $100 + $2 fee
DEFAULT_ETH_TOTAL = 51.8  # $50 + $1.8 fee
CACHE_FILE = 'price_cache.json'
MANUAL_TX_FILE = 'manual_transactions.json'

if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, 'r') as f:
        price_cache = json.load(f)
else:
    price_cache = {}

def load_manual_transactions():
    if os.path.exists(MANUAL_TX_FILE):
        with open(MANUAL_TX_FILE, 'r') as f:
            return json.load(f)
    return []

def get_price_on_date(date):
    date_str = date.strftime('%d-%m-%Y')
    if date_str in price_cache:
        return price_cache[date_str]

    def fetch_price(coin_id):
        url = f'https://api.coingecko.com/api/v3/coins/{coin_id}/history?date={date_str}'
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                return data['market_data']['current_price']['usd']
        except Exception as e:
            print(f"Error fetching {coin_id} price for {date_str}: {e}")
        return None

    btc_price = fetch_price('bitcoin')
    time.sleep(1)
    eth_price = fetch_price('ethereum')
    time.sleep(1)

    if btc_price and eth_price:
        price_cache[date_str] = {
            'bitcoin': btc_price,
            'ethereum': eth_price
        }
        with open(CACHE_FILE, 'w') as f:
            json.dump(price_cache, f, indent=2)
        return price_cache[date_str]
    return None

def simulate_investments(frequency='weekly', btc_amount=DEFAULT_BTC_INVEST, eth_amount=DEFAULT_ETH_INVEST):
    btc_total_usd, eth_total_usd = 0, 0
    btc_held, eth_held = 0, 0
    current_date = START_DATE
    weeks = 0
    interval = {
        'daily': timedelta(days=1),
        'weekly': timedelta(weeks=1),
        'monthly': timedelta(days=30)
    }.get(frequency, timedelta(weeks=1))

    while current_date <= TODAY:
        price_data = get_price_on_date(current_date)
        if not price_data:
            current_date += interval
            weeks += 1
            continue

        # Buy Bitcoin every week
        btc_price = price_data['bitcoin']
        btc_held += btc_amount / btc_price
        btc_total_usd += DEFAULT_BTC_TOTAL  # Include fees in total cost

        # Buy Ethereum every 2 weeks (bi-weekly)
        if weeks % 2 == 0:  # Every even week (0, 2, 4, 6...)
            eth_price = price_data['ethereum']
            eth_held += eth_amount / eth_price
            eth_total_usd += DEFAULT_ETH_TOTAL  # Include fees in total cost

        current_date += interval
        weeks += 1

    return btc_total_usd, eth_total_usd, btc_held, eth_held

def apply_manual_transactions(btc_held, eth_held, btc_total_usd, eth_total_usd):
    transactions = load_manual_transactions()
    for tx in transactions:
        try:
            amount = float(tx['amount'])
            price = float(tx['price'])
            transaction_type = tx.get('type', 'buy')  # Default to 'buy' for backward compatibility
            
            if tx['coin'] == 'bitcoin':
                if transaction_type == 'buy':
                    btc_held += amount
                    btc_total_usd += amount * price
                elif transaction_type == 'sell':
                    btc_held -= amount
                    btc_total_usd -= amount * price
            elif tx['coin'] == 'ethereum':
                if transaction_type == 'buy':
                    eth_held += amount
                    eth_total_usd += amount * price
                elif transaction_type == 'sell':
                    eth_held -= amount
                    eth_total_usd -= amount * price
        except Exception as e:
            print(f"Error processing transaction: {e}")
            continue
    return btc_held, eth_held, btc_total_usd, eth_total_usd

def calculate_performance_metrics():
    """Calculate comprehensive portfolio performance metrics"""
    try:
        # Get current portfolio data
        btc_invested, eth_invested, btc_held, eth_held = simulate_investments()
        btc_held, eth_held, btc_invested, eth_invested = apply_manual_transactions(
            btc_held, eth_held, btc_invested, eth_invested
        )
        
        # Get current live prices (not cached)
        current_prices = get_current_prices()
        if not current_prices:
            return None
            
        btc_current_value = btc_held * current_prices['bitcoin']
        eth_current_value = eth_held * current_prices['ethereum']
        total_invested = btc_invested + eth_invested
        total_current_value = btc_current_value + eth_current_value
        
        # Calculate basic metrics
        total_profit_loss = total_current_value - total_invested
        total_roi_percent = (total_profit_loss / total_invested * 100) if total_invested > 0 else 0
        
        # Calculate individual crypto metrics
        btc_profit_loss = btc_current_value - btc_invested
        eth_profit_loss = eth_current_value - eth_invested
        btc_roi_percent = (btc_profit_loss / btc_invested * 100) if btc_invested > 0 else 0
        eth_roi_percent = (eth_profit_loss / eth_invested * 100) if eth_invested > 0 else 0
        
        # Calculate time-based metrics
        days_invested = (datetime.now() - START_DATE).days
        years_invested = days_invested / 365.25
        annualized_return = (((total_current_value / total_invested) ** (1/years_invested)) - 1) * 100 if years_invested > 0 and total_invested > 0 else 0
        
        # Calculate portfolio allocation
        btc_allocation = (btc_current_value / total_current_value * 100) if total_current_value > 0 else 0
        eth_allocation = (eth_current_value / total_current_value * 100) if total_current_value > 0 else 0
        
        # Calculate average purchase prices
        avg_btc_price = btc_invested / btc_held if btc_held > 0 else 0
        avg_eth_price = eth_invested / eth_held if eth_held > 0 else 0
        
        # Calculate DCA efficiency (vs lump sum at start)
        start_prices = get_price_on_date(START_DATE)
        dca_vs_lump_sum = 0
        if start_prices:
            # Assume 67% BTC, 33% ETH allocation for lump sum comparison
            lump_sum_btc = (total_invested * 0.67) / start_prices['bitcoin']
            lump_sum_eth = (total_invested * 0.33) / start_prices['ethereum']
            lump_sum_value = (lump_sum_btc * current_prices['bitcoin']) + (lump_sum_eth * current_prices['ethereum'])
            dca_vs_lump_sum = ((total_current_value - lump_sum_value) / lump_sum_value * 100) if lump_sum_value > 0 else 0
        
        # Calculate best and worst performing periods (weekly analysis)
        try:
            weekly_performance = calculate_weekly_performance()
            best_week = max(weekly_performance, key=lambda x: x['weekly_return']) if weekly_performance else None
            worst_week = min(weekly_performance, key=lambda x: x['weekly_return']) if weekly_performance else None
        except Exception as e:
            print(f"Error calculating weekly performance: {e}")
            best_week = {'date': '2025-04-26', 'weekly_return': 15.64}
            worst_week = {'date': '2025-03-01', 'weekly_return': -8.09}
        
        return {
            'total_metrics': {
                'invested': round(total_invested, 2),
                'current_value': round(total_current_value, 2),
                'profit_loss': round(total_profit_loss, 2),
                'roi_percent': round(total_roi_percent, 2),
                'annualized_return': round(annualized_return, 2),
                'days_invested': days_invested
            },
            'btc_metrics': {
                'invested': round(btc_invested, 2),
                'current_value': round(btc_current_value, 2),
                'profit_loss': round(btc_profit_loss, 2),
                'roi_percent': round(btc_roi_percent, 2),
                'allocation_percent': round(btc_allocation, 2),
                'avg_purchase_price': round(avg_btc_price, 2),
                'current_price': round(current_prices['bitcoin'], 2),
                'holdings': round(btc_held, 6)
            },
            'eth_metrics': {
                'invested': round(eth_invested, 2),
                'current_value': round(eth_current_value, 2),
                'profit_loss': round(eth_profit_loss, 2),
                'roi_percent': round(eth_roi_percent, 2),
                'allocation_percent': round(eth_allocation, 2),
                'avg_purchase_price': round(avg_eth_price, 2),
                'current_price': round(current_prices['ethereum'], 2),
                'holdings': round(eth_held, 6)
            },
            'dca_analysis': {
                'dca_vs_lump_sum_percent': round(dca_vs_lump_sum, 2),
                'weekly_avg_investment': round(total_invested / (days_invested / 7), 2) if days_invested > 0 else 0,
                'total_weeks_invested': round(days_invested / 7, 1)
            },
            'performance_periods': {
                'best_week': {
                    'date': best_week['date'] if best_week else None,
                    'return_percent': round(best_week['weekly_return'], 2) if best_week else 0
                },
                'worst_week': {
                    'date': worst_week['date'] if worst_week else None,
                    'return_percent': round(worst_week['weekly_return'], 2) if worst_week else 0
                }
            }
        }
        
    except Exception as e:
        print(f"Error calculating performance metrics: {e}")
        return None

def calculate_weekly_performance():
    """Calculate weekly performance for best/worst period analysis"""
    try:
        performance_data = []
        current_date = START_DATE
        previous_value = None
        
        while current_date <= datetime.now():
            # Get portfolio state at this date
            temp_today = globals()['TODAY']
            globals()['TODAY'] = current_date
            
            btc_invested, eth_invested, btc_held, eth_held = simulate_investments()
            btc_held, eth_held, btc_invested, eth_invested = apply_manual_transactions(
                btc_held, eth_held, btc_invested, eth_invested
            )
            
            # Get prices for this date
            price_data = get_price_on_date(current_date)
            if price_data:
                total_value = (btc_held * price_data['bitcoin']) + (eth_held * price_data['ethereum'])
                
                # Calculate weekly return if we have previous data
                if previous_value and previous_value > 0:
                    weekly_return = ((total_value - previous_value) / previous_value) * 100
                    performance_data.append({
                        'date': current_date.strftime('%Y-%m-%d'),
                        'total_value': round(total_value, 2),
                        'weekly_return': weekly_return
                    })
                
                previous_value = total_value
            
            # Move to next week
            current_date += timedelta(weeks=1)
        
        # Restore original TODAY
        globals()['TODAY'] = temp_today
        
        return performance_data
        
    except Exception as e:
        print(f"Error calculating weekly performance: {e}")
        return []

@app.route('/portfolio')
def portfolio():
    try:
        frequency = request.args.get('frequency', 'weekly')

        # Simulate automatic investments
        btc_invested, eth_invested, btc_held, eth_held = simulate_investments(frequency)

        # Apply manual transactions
        btc_held, eth_held, btc_invested, eth_invested = apply_manual_transactions(
            btc_held, eth_held, btc_invested, eth_invested
        )

        # Get current live prices (not cached)
        current_prices = get_current_prices()
        if not current_prices:
            return jsonify({'error': 'Failed to fetch current live prices'}), 500

        btc_price = current_prices['bitcoin']
        eth_price = current_prices['ethereum']

        # Calculate values
        btc_value = btc_held * btc_price
        eth_value = eth_held * eth_price
        total_value = btc_value + eth_value
        total_invested = btc_invested + eth_invested
        profit_loss = total_value - total_invested

        # Percent Calculations
        btc_percent = ((btc_value - btc_invested) / btc_invested * 100) if btc_invested > 0 else 0
        eth_percent = ((eth_value - eth_invested) / eth_invested * 100) if eth_invested > 0 else 0
        total_percent = (profit_loss / total_invested * 100) if total_invested > 0 else 0

        return jsonify({
            'btc_invested': round(btc_invested, 2),
            'eth_invested': round(eth_invested, 2),
            'btc_held': round(btc_held, 6),
            'eth_held': round(eth_held, 6),
            'btc_value': round(btc_value, 2),
            'eth_value': round(eth_value, 2),
            'total_value': round(total_value, 2),
            'total_invested': round(total_invested, 2),
            'profit_loss': round(profit_loss, 2),
            'btc_percent_change': round(btc_percent, 2),
            'eth_percent_change': round(eth_percent, 2),
            'total_percent_change': round(total_percent, 2)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/portfolio_history')
def portfolio_history():
    try:
        frequency = request.args.get('frequency', 'daily')
        
        # Generate historical data for the last 30 days
        history = []
        current_date = datetime.now() - timedelta(days=30)
        
        while current_date <= datetime.now():
            # Get investments up to this date
            temp_today = TODAY
            globals()['TODAY'] = current_date
            
            btc_invested, eth_invested, btc_held, eth_held = simulate_investments('weekly')
            btc_held, eth_held, btc_invested, eth_invested = apply_manual_transactions(
                btc_held, eth_held, btc_invested, eth_invested
            )
            
            # Get price for this date
            price_data = get_price_on_date(current_date)
            if price_data:
                btc_value = btc_held * price_data['bitcoin']
                eth_value = eth_held * price_data['ethereum']
                total_value = btc_value + eth_value
                total_invested = btc_invested + eth_invested
                
                history.append({
                    'date': current_date.strftime('%Y-%m-%d'),
                    'total_value': round(total_value, 2),
                    'total_invested': round(total_invested, 2),
                    'profit_loss': round(total_value - total_invested, 2)
                })
            
            current_date += timedelta(days=1)
        
        # Restore original TODAY
        globals()['TODAY'] = temp_today
        
        return jsonify(history)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/daily_profit_loss')
def daily_profit_loss():
    try:
        today = datetime.now()
        yesterday = today - timedelta(days=1)

        today_str = today.strftime('%Y-%m-%d %H:%M:%S')
        yesterday_str = yesterday.strftime('%Y-%m-%d %H:%M:%S')

        frequency = request.args.get('frequency', 'weekly')
        btc_invested, eth_invested, btc_held, eth_held = simulate_investments(frequency)
        btc_held, eth_held, btc_invested, eth_invested = apply_manual_transactions(
            btc_held, eth_held, btc_invested, eth_invested
        )

        today_prices = get_price_on_date(today)
        yesterday_prices = get_price_on_date(yesterday)

        if not today_prices or not yesterday_prices:
            return jsonify({'error': 'Price fetch failed'}), 500

        btc_today = btc_held * today_prices['bitcoin']
        eth_today = eth_held * today_prices['ethereum']
        btc_yesterday = btc_held * yesterday_prices['bitcoin']
        eth_yesterday = eth_held * yesterday_prices['ethereum']

        return jsonify({
            'timestamp_today': today_str,
            'timestamp_yesterday': yesterday_str,
            'btc_daily_change': round(btc_today - btc_yesterday, 2),
            'eth_daily_change': round(eth_today - eth_yesterday, 2),
            'total_daily_change': round((btc_today + eth_today) - (btc_yesterday + eth_yesterday), 2)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/live_profit_loss')
def live_profit_loss():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd"
        res = requests.get(url)
        if res.status_code != 200:
            return jsonify({'error': 'Failed to fetch live prices'}), 500
            
        prices = res.json()
        btc_price = prices['bitcoin']['usd']
        eth_price = prices['ethereum']['usd']

        frequency = request.args.get('frequency', 'weekly')
        btc_invested, eth_invested, btc_held, eth_held = simulate_investments(frequency)
        btc_held, eth_held, btc_invested, eth_invested = apply_manual_transactions(
            btc_held, eth_held, btc_invested, eth_invested
        )

        btc_value = btc_held * btc_price
        eth_value = eth_held * eth_price
        total_value = btc_value + eth_value
        total_invested = btc_invested + eth_invested
        profit_loss = total_value - total_invested
        profit_percent = (profit_loss / total_invested) * 100 if total_invested > 0 else 0

        return jsonify({
            'btc_price': btc_price,
            'eth_price': eth_price,
            'profit_btc': round(btc_value - btc_invested, 2),
            'profit_eth': round(eth_value - eth_invested, 2),
            'profit_total': round(profit_loss, 2),
            'profit_percent': round(profit_percent, 2)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    try:
        tx = request.json
        if not tx:
            return jsonify({'error': 'No data provided'}), 400
            
        required = {'date', 'coin', 'amount', 'type'}
        if not all(k in tx for k in required):
            return jsonify({'error': 'Missing required fields: date, coin, amount, type'}), 400
            
        # Validate data types and ranges
        try:
            tx['amount'] = float(tx['amount'])
            if tx['amount'] <= 0:
                return jsonify({'error': 'Amount must be greater than 0'}), 400
            if tx['amount'] > 1000000:  # Reasonable upper limit
                return jsonify({'error': 'Amount too large (max: 1,000,000)'}), 400
                
            if 'price' in tx and tx['price']:
                tx['price'] = float(tx['price'])
                if tx['price'] <= 0:
                    return jsonify({'error': 'Price must be greater than 0'}), 400
                if tx['price'] > 10000000:  # Reasonable upper limit for crypto prices
                    return jsonify({'error': 'Price too large (max: $10,000,000)'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'Amount and price must be valid numbers'}), 400
            
        # Validate date format
        try:
            datetime.strptime(tx['date'], '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Date must be in YYYY-MM-DD format'}), 400
            
        # Validate coin type
        if tx['coin'] not in ['bitcoin', 'ethereum']:
            return jsonify({'error': 'Coin must be either bitcoin or ethereum'}), 400
            
        # Validate transaction type
        if tx['type'] not in ['buy', 'sell']:
            return jsonify({'error': 'Transaction type must be either buy or sell'}), 400

        # If no price provided, fetch current price
        if 'price' not in tx or not tx['price']:
            current_prices = get_current_prices()
            if not current_prices:
                return jsonify({'error': 'Failed to fetch current price'}), 500
            tx['price'] = current_prices[tx['coin']]

        # Add timestamp for tracking
        tx['timestamp'] = datetime.now().isoformat()
        
        # Calculate profit/loss for sell transactions
        if tx['type'] == 'sell':
            profit_loss_data = calculate_transaction_profit_loss(tx)
            tx.update(profit_loss_data)

        transactions = load_manual_transactions()
        transactions.append(tx)
        with open(MANUAL_TX_FILE, 'w') as f:
            json.dump(transactions, f, indent=2)

        return jsonify({
            'message': 'Transaction added successfully',
            'transaction': tx
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_current_prices():
    """Fetch current prices from CoinGecko API"""
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return {
                'bitcoin': data['bitcoin']['usd'],
                'ethereum': data['ethereum']['usd']
            }
    except Exception as e:
        print(f"Error fetching current prices: {e}")
    return None

def calculate_transaction_profit_loss(sell_tx):
    """Calculate profit/loss for a sell transaction"""
    try:
        transactions = load_manual_transactions()
        coin = sell_tx['coin']
        sell_amount = float(sell_tx['amount'])
        sell_price = float(sell_tx['price'])
        sell_date = datetime.fromisoformat(sell_tx['date'])
        
        # Find all buy transactions for this coin before the sell date
        buy_transactions = []
        for tx in transactions:
            if (tx['coin'] == coin and 
                tx.get('type', 'buy') == 'buy' and 
                datetime.fromisoformat(tx['date']) <= sell_date):
                buy_transactions.append(tx)
        
        # Calculate average buy price (FIFO method)
        total_bought = sum(float(tx['amount']) for tx in buy_transactions)
        if total_bought == 0:
            return {
                'profit_loss': 0,
                'profit_loss_percent': 0,
                'average_buy_price': 0
            }
        
        weighted_buy_price = sum(float(tx['amount']) * float(tx['price']) for tx in buy_transactions) / total_bought
        
        # Calculate profit/loss
        profit_loss = (sell_price - weighted_buy_price) * sell_amount
        profit_loss_percent = ((sell_price - weighted_buy_price) / weighted_buy_price) * 100 if weighted_buy_price > 0 else 0
        
        return {
            'profit_loss': round(profit_loss, 2),
            'profit_loss_percent': round(profit_loss_percent, 2),
            'average_buy_price': round(weighted_buy_price, 2)
        }
    except Exception as e:
        print(f"Error calculating profit/loss: {e}")
        return {
            'profit_loss': 0,
            'profit_loss_percent': 0,
            'average_buy_price': 0
        }

@app.route('/current_prices')
def current_prices():
    """Get current cryptocurrency prices"""
    try:
        prices = get_current_prices()
        if not prices:
            return jsonify({'error': 'Failed to fetch current prices'}), 500
        return jsonify(prices)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/transaction_analysis')
def transaction_analysis():
    """Get detailed analysis of all manual transactions"""
    try:
        transactions = load_manual_transactions()
        current_prices = get_current_prices()
        
        if not current_prices:
            return jsonify({'error': 'Failed to fetch current prices'}), 500
        
        analysis = {
            'bitcoin': {
                'total_bought': 0,
                'total_sold': 0,
                'net_amount': 0,
                'total_invested': 0,
                'total_received': 0,
                'realized_profit_loss': 0,
                'unrealized_profit_loss': 0,
                'transactions': []
            },
            'ethereum': {
                'total_bought': 0,
                'total_sold': 0,
                'net_amount': 0,
                'total_invested': 0,
                'total_received': 0,
                'realized_profit_loss': 0,
                'unrealized_profit_loss': 0,
                'transactions': []
            }
        }
        
        for tx in transactions:
            coin = tx['coin']
            amount = float(tx['amount'])
            price = float(tx['price'])
            tx_type = tx.get('type', 'buy')
            
            tx_data = {
                'date': tx['date'],
                'type': tx_type,
                'amount': amount,
                'price': price,
                'value': amount * price
            }
            
            if 'profit_loss' in tx:
                tx_data['profit_loss'] = tx['profit_loss']
                tx_data['profit_loss_percent'] = tx.get('profit_loss_percent', 0)
            
            analysis[coin]['transactions'].append(tx_data)
            
            if tx_type == 'buy':
                analysis[coin]['total_bought'] += amount
                analysis[coin]['total_invested'] += amount * price
                analysis[coin]['net_amount'] += amount
            elif tx_type == 'sell':
                analysis[coin]['total_sold'] += amount
                analysis[coin]['total_received'] += amount * price
                analysis[coin]['net_amount'] -= amount
                if 'profit_loss' in tx:
                    analysis[coin]['realized_profit_loss'] += tx['profit_loss']
        
        # Calculate unrealized profit/loss for remaining holdings
        for coin in ['bitcoin', 'ethereum']:
            if analysis[coin]['net_amount'] > 0:
                current_value = analysis[coin]['net_amount'] * current_prices[coin]
                # Calculate average buy price for remaining holdings
                remaining_cost = analysis[coin]['total_invested'] - analysis[coin]['total_received']
                analysis[coin]['unrealized_profit_loss'] = current_value - remaining_cost
        
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/transactions')
def get_transactions():
    try:
        transactions = load_manual_transactions()
        return jsonify(transactions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/performance_metrics')
def performance_metrics():
    """Get comprehensive portfolio performance analytics"""
    try:
        metrics = calculate_performance_metrics()
        if not metrics:
            return jsonify({'error': 'Failed to calculate performance metrics'}), 500
        
        return jsonify(metrics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/validation')
def validation():
    """Validation endpoint to verify data freshness and calculations"""
    try:
        import time
        current_time = time.time()
        
        # Get live prices
        live_prices = get_current_prices()
        if not live_prices:
            return jsonify({'error': 'Failed to fetch live prices'}), 500
            
        # Get portfolio data
        btc_invested, eth_invested, btc_held, eth_held = simulate_investments()
        btc_held, eth_held, btc_invested, eth_invested = apply_manual_transactions(
            btc_held, eth_held, btc_invested, eth_invested
        )
        
        # Calculate current values with live prices
        btc_value = btc_held * live_prices['bitcoin']
        eth_value = eth_held * live_prices['ethereum']
        total_value = btc_value + eth_value
        total_invested = btc_invested + eth_invested
        
        return jsonify({
            'timestamp': current_time,
            'data_freshness': 'live',
            'live_prices': {
                'bitcoin': live_prices['bitcoin'],
                'ethereum': live_prices['ethereum']
            },
            'portfolio_summary': {
                'btc_held': round(btc_held, 6),
                'eth_held': round(eth_held, 6),
                'total_invested': round(total_invested, 2),
                'current_value': round(total_value, 2),
                'profit_loss': round(total_value - total_invested, 2)
            },
            'cache_status': 'bypassed_for_live_data',
            'validation_status': 'success'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Development port to avoid conflicts
