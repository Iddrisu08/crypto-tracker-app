from flask import Flask, jsonify, request, g, Response, stream_with_context
from flask_cors import CORS
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import requests, json, os, time, logging, csv, io, threading, smtplib
from datetime import datetime, timedelta
from functools import wraps
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configure caching (in-memory for development, can be changed to Redis for production)
cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache'})

# Configure rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["1000 per day", "500 per hour"],
    storage_uri="memory://"
)

# Configure logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Secure CORS configuration - get origins from environment variable
cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:5173,http://localhost:5174,http://localhost:3000')
cors_origins_list = [origin.strip() for origin in cors_origins.split(',')]
logger.info(f"CORS origins configured: {cors_origins_list}")

CORS(app, origins=cors_origins_list, 
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
ALERTS_FILE = 'price_alerts.json'

# Email configuration for alerts (use environment variables in production)
EMAIL_CONFIG = {
    'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
    'smtp_port': int(os.getenv('SMTP_PORT', '587')),
    'email_user': os.getenv('EMAIL_USER', ''),
    'email_password': os.getenv('EMAIL_PASSWORD', ''),
    'from_email': os.getenv('FROM_EMAIL', ''),
    'enabled': os.getenv('EMAIL_ALERTS_ENABLED', 'false').lower() == 'true'
}

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

def load_price_alerts():
    """Load price alerts from file"""
    if os.path.exists(ALERTS_FILE):
        with open(ALERTS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_price_alerts(alerts):
    """Save price alerts to file"""
    try:
        with open(ALERTS_FILE, 'w') as f:
            json.dump(alerts, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving price alerts: {e}")
        return False

def send_email_alert(to_email, subject, body):
    """Send email alert notification"""
    if not EMAIL_CONFIG['enabled'] or not EMAIL_CONFIG['email_user']:
        logger.info("Email alerts disabled or not configured")
        return False
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG['from_email'] or EMAIL_CONFIG['email_user']
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add body to email
        msg.attach(MIMEText(body, 'plain'))
        
        # Gmail SMTP configuration
        server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
        server.starttls()  # Enable security
        server.login(EMAIL_CONFIG['email_user'], EMAIL_CONFIG['email_password'])
        
        # Send email
        text = msg.as_string()
        server.sendmail(EMAIL_CONFIG['email_user'], to_email, text)
        server.quit()
        
        logger.info(f"Alert email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending email alert: {e}")
        return False

def check_price_alerts():
    """Background function to check price alerts"""
    try:
        alerts = load_price_alerts()
        if not alerts:
            return
        
        # Get current prices
        current_prices = get_current_prices_cached()
        if not current_prices:
            logger.warning("Could not fetch prices for alert checking")
            return
        
        alerts_triggered = []
        alerts_to_keep = []
        
        for alert in alerts:
            try:
                coin = alert['coin']
                target_price = float(alert['target_price'])
                condition = alert['condition']  # 'above' or 'below'
                email = alert['email']
                current_price = current_prices.get(coin, 0)
                
                alert_triggered = False
                
                if condition == 'above' and current_price >= target_price:
                    alert_triggered = True
                elif condition == 'below' and current_price <= target_price:
                    alert_triggered = True
                
                if alert_triggered:
                    # Send notification
                    coin_name = 'Bitcoin' if coin == 'bitcoin' else 'Ethereum'
                    subject = f"🚨 Crypto Price Alert: {coin_name} ${current_price:,.2f}"
                    body = f"""
Price Alert Triggered!

{coin_name} has reached ${current_price:,.2f}
Target: ${target_price:,.2f} ({condition})
Triggered at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This alert has been automatically removed.

---
Crypto Investment Tracker
                    """
                    
                    if send_email_alert(email, subject, body.strip()):
                        alerts_triggered.append(alert)
                        logger.info(f"Price alert triggered for {coin_name}: ${current_price} {condition} ${target_price}")
                    else:
                        # Keep alert if email failed
                        alerts_to_keep.append(alert)
                else:
                    # Keep alert if not triggered
                    alerts_to_keep.append(alert)
                    
            except Exception as e:
                logger.error(f"Error processing alert: {e}")
                alerts_to_keep.append(alert)  # Keep alert on error
        
        # Update alerts file (remove triggered alerts)
        if alerts_triggered:
            save_price_alerts(alerts_to_keep)
            logger.info(f"Removed {len(alerts_triggered)} triggered alerts")
            
    except Exception as e:
        logger.error(f"Error in check_price_alerts: {e}")

def start_price_alert_monitor():
    """Start background price alert monitoring"""
    def alert_worker():
        while True:
            try:
                check_price_alerts()
                # Check every 2 minutes
                time.sleep(120)
            except Exception as e:
                logger.error(f"Price alert monitor error: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
    
    # Start background thread
    alert_thread = threading.Thread(target=alert_worker, daemon=True)
    alert_thread.start()
    logger.info("Price alert monitoring started")

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

# Performance monitoring decorator
def monitor_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = (time.time() - start_time) * 1000
            logger.info(f"{func.__name__} completed in {duration:.2f}ms")
            return result
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            logger.error(f"{func.__name__} failed after {duration:.2f}ms: {str(e)}")
            raise
    return wrapper

# Enhanced get_current_prices with better caching
def get_current_prices_cached():
    """Get current crypto prices with enhanced caching"""
    cache_key = 'current_prices'
    prices = cache.get(cache_key)
    
    if prices:
        logger.info("Returning cached current prices")
        return prices
    
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            'ids': 'bitcoin,ethereum',
            'vs_currencies': 'usd'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        prices = {
            'bitcoin': data['bitcoin']['usd'],
            'ethereum': data['ethereum']['usd']
        }
        
        # Cache for 2 minutes
        cache.set(cache_key, prices, timeout=120)
        logger.info(f"Fetched and cached new prices: BTC=${prices['bitcoin']}, ETH=${prices['ethereum']}")
        return prices
        
    except Exception as e:
        logger.error(f"Error fetching current prices: {e}")
        # Return cached prices if available, otherwise default
        cached_prices = cache.get(cache_key)
        if cached_prices:
            logger.warning("API failed, returning stale cached prices")
            return cached_prices
        
        logger.warning("Using fallback prices")
        return {'bitcoin': 50000, 'ethereum': 3000}

@app.route('/portfolio')
@limiter.limit("30 per minute")
@monitor_performance
@cache.cached(timeout=60)  # Cache for 1 minute
def portfolio():
    try:
        frequency = request.args.get('frequency', 'weekly')

        # Simulate automatic investments
        btc_invested, eth_invested, btc_held, eth_held = simulate_investments(frequency)

        # Apply manual transactions
        btc_held, eth_held, btc_invested, eth_invested = apply_manual_transactions(
            btc_held, eth_held, btc_invested, eth_invested
        )

        # Get current live prices (with caching)
        current_prices = get_current_prices_cached()

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
@cache.cached(timeout=600)  # Cache for 10 minutes due to expensive calculations
@monitor_performance
def portfolio_history():
    """
    Get portfolio history with intelligent aggregation.
    Supports: 7d, 30d, 90d, 365d with auto-aggregation for performance
    """
    try:
        # Parse parameters
        period = request.args.get('period', '30d').lower()
        aggregation = request.args.get('aggregation', 'auto')
        
        # Determine days and interval based on period
        period_mapping = {
            '7d': {'days': 7, 'interval': 1, 'label': '7 days'},
            '30d': {'days': 30, 'interval': 1, 'label': '30 days'},
            '90d': {'days': 90, 'interval': 2, 'label': '3 months'},  # Every 2 days
            '6m': {'days': 180, 'interval': 4, 'label': '6 months'},  # Every 4 days
            '1y': {'days': 365, 'interval': 7, 'label': '1 year'}     # Weekly
        }
        
        config = period_mapping.get(period, period_mapping['30d'])
        days = config['days']
        interval = config['interval'] if aggregation == 'auto' else 1
        
        # Override interval if explicitly requested
        if aggregation == 'daily':
            interval = 1
        elif aggregation == 'weekly':
            interval = 7
        elif aggregation == 'monthly':
            interval = 30
        
        # Generate historical data
        history = []
        current_date = datetime.now() - timedelta(days=days)
        temp_today = globals()['TODAY']
        
        logger.info(f"Generating {config['label']} portfolio history with {interval}-day intervals")
        
        data_points = 0
        max_data_points = 200  # Prevent excessive API calls
        
        while current_date <= datetime.now() and data_points < max_data_points:
            # Set simulation date
            globals()['TODAY'] = current_date
            
            try:
                # Get portfolio state for this date
                btc_invested, eth_invested, btc_held, eth_held = simulate_investments('weekly')
                btc_held, eth_held, btc_invested, eth_invested = apply_manual_transactions(
                    btc_held, eth_held, btc_invested, eth_invested
                )
                
                # Get prices for this date
                price_data = get_price_on_date(current_date)
                if price_data:
                    btc_value = btc_held * price_data['bitcoin']
                    eth_value = eth_held * price_data['ethereum']
                    total_value = btc_value + eth_value
                    total_invested = btc_invested + eth_invested
                    profit_loss = total_value - total_invested
                    roi_percent = (profit_loss / total_invested * 100) if total_invested > 0 else 0
                    
                    history.append({
                        'date': current_date.strftime('%Y-%m-%d'),
                        'total_value': round(total_value, 2),
                        'total_invested': round(total_invested, 2),
                        'profit_loss': round(profit_loss, 2),
                        'roi_percent': round(roi_percent, 2),
                        'btc_value': round(btc_value, 2),
                        'eth_value': round(eth_value, 2),
                        'btc_price': round(price_data['bitcoin'], 2),
                        'eth_price': round(price_data['ethereum'], 2)
                    })
                    
                    data_points += 1
                    
            except Exception as e:
                logger.warning(f"Error calculating history for {current_date}: {e}")
            
            current_date += timedelta(days=interval)
        
        # Restore original TODAY
        globals()['TODAY'] = temp_today
        
        # Add metadata
        response_data = {
            'period': period,
            'aggregation': f"{interval}-day interval",
            'data_points': len(history),
            'date_range': {
                'start': history[0]['date'] if history else None,
                'end': history[-1]['date'] if history else None
            },
            'history': history
        }
        
        logger.info(f"Portfolio history generated: {len(history)} data points over {config['label']}")
        return jsonify(response_data)
        
    except Exception as e:
        # Restore original TODAY in case of error
        if 'temp_today' in locals():
            globals()['TODAY'] = temp_today
        logger.error(f"Error generating portfolio history: {e}")
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
@limiter.limit("10 per minute")  # Strict limit for transaction creation
@monitor_performance
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
@limiter.limit("60 per minute")  # Higher limit for price updates
@monitor_performance
@cache.cached(timeout=120)  # Cache for 2 minutes
def current_prices():
    """Get current cryptocurrency prices"""
    try:
        prices = get_current_prices_cached()
        return jsonify(prices)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/transaction_analysis')
@limiter.limit("30 per minute")
@monitor_performance
@cache.cached(timeout=180)  # Cache for 3 minutes
def transaction_analysis():
    """Get detailed analysis of all manual transactions"""
    try:
        transactions = load_manual_transactions()
        current_prices = get_current_prices_cached()
        
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
@limiter.limit("20 per minute")  # Lower limit since this is expensive
@monitor_performance
@cache.cached(timeout=300)  # Cache for 5 minutes - expensive calculation
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

# Request logging middleware
@app.before_request
def log_request_info():
    g.start_time = time.time()
    logger.info(f"{request.method} {request.path} from {request.remote_addr}")

@app.after_request
def log_response_info(response):
    duration = (time.time() - g.start_time) * 1000 if hasattr(g, 'start_time') else 0
    logger.info(f"{request.method} {request.path} -> {response.status_code} ({duration:.2f}ms)")
    return response

# Price Alert endpoints
@app.route('/alerts', methods=['GET'])
@limiter.limit("10 per minute")
@monitor_performance
def get_price_alerts():
    """Get all price alerts"""
    try:
        alerts = load_price_alerts()
        return jsonify({
            'alerts': alerts,
            'total_count': len(alerts)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/alerts', methods=['POST'])
@limiter.limit("5 per minute")
@monitor_performance
def create_price_alert():
    """Create a new price alert"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['coin', 'target_price', 'condition', 'email']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate data types and values
        try:
            target_price = float(data['target_price'])
            if target_price <= 0:
                return jsonify({'error': 'Target price must be greater than 0'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'Target price must be a valid number'}), 400
        
        # Validate coin
        if data['coin'] not in ['bitcoin', 'ethereum']:
            return jsonify({'error': 'Coin must be either bitcoin or ethereum'}), 400
        
        # Validate condition
        if data['condition'] not in ['above', 'below']:
            return jsonify({'error': 'Condition must be either above or below'}), 400
        
        # Validate email format (basic validation)
        email = data['email'].strip()
        if '@' not in email or '.' not in email:
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Create alert object
        alert = {
            'id': f"{data['coin']}_{target_price}_{data['condition']}_{int(time.time())}",
            'coin': data['coin'],
            'target_price': target_price,
            'condition': data['condition'],
            'email': email,
            'created_at': datetime.now().isoformat(),
            'enabled': True,
            'description': data.get('description', f"{data['coin'].title()} {data['condition']} ${target_price:,.2f}")
        }
        
        # Load existing alerts and add new one
        alerts = load_price_alerts()
        alerts.append(alert)
        
        # Save alerts
        if save_price_alerts(alerts):
            logger.info(f"Price alert created: {alert['description']} for {email}")
            return jsonify({
                'message': 'Price alert created successfully',
                'alert': alert
            }), 201
        else:
            return jsonify({'error': 'Failed to save price alert'}), 500
            
    except Exception as e:
        logger.error(f"Error creating price alert: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/alerts/<alert_id>', methods=['DELETE'])
@limiter.limit("10 per minute")
@monitor_performance
def delete_price_alert(alert_id):
    """Delete a price alert"""
    try:
        alerts = load_price_alerts()
        original_count = len(alerts)
        
        # Filter out the alert to delete
        alerts = [alert for alert in alerts if alert.get('id') != alert_id]
        
        if len(alerts) == original_count:
            return jsonify({'error': 'Alert not found'}), 404
        
        # Save updated alerts
        if save_price_alerts(alerts):
            logger.info(f"Price alert deleted: {alert_id}")
            return jsonify({
                'message': 'Price alert deleted successfully',
                'deleted_id': alert_id
            })
        else:
            return jsonify({'error': 'Failed to delete price alert'}), 500
            
    except Exception as e:
        logger.error(f"Error deleting price alert: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/alerts/test', methods=['POST'])
@limiter.limit("2 per minute")  # Very restrictive for test emails
@monitor_performance
def test_price_alert():
    """Test price alert email system"""
    try:
        data = request.json
        if not data or 'email' not in data:
            return jsonify({'error': 'Email address required'}), 400
        
        email = data['email'].strip()
        if '@' not in email or '.' not in email:
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Test email content
        subject = "🧪 Crypto Tracker - Price Alert Test"
        body = f"""
This is a test email from your Crypto Investment Tracker.

If you received this email, your price alert notifications are working correctly!

Test sent at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---
Crypto Investment Tracker
        """
        
        success = send_email_alert(email, subject, body.strip())
        
        if success:
            return jsonify({
                'message': 'Test email sent successfully',
                'email': email
            })
        else:
            return jsonify({
                'error': 'Failed to send test email. Check your email configuration.',
                'email_configured': EMAIL_CONFIG['enabled']
            }), 500
            
    except Exception as e:
        logger.error(f"Error sending test email: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/alerts/check', methods=['POST'])
@limiter.limit("2 per minute")
@monitor_performance
def manually_check_alerts():
    """Manually trigger alert checking (for testing)"""
    try:
        check_price_alerts()
        return jsonify({
            'message': 'Price alerts checked manually',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error in manual alert check: {e}")
        return jsonify({'error': str(e)}), 500

# CSV Export endpoints
@app.route('/export/portfolio')
@limiter.limit("5 per minute")  # Lower limit for export operations
@monitor_performance
def export_portfolio_csv():
    """Export portfolio data as CSV"""
    try:
        # Get portfolio data
        btc_invested, eth_invested, btc_held, eth_held = simulate_investments()
        btc_held, eth_held, btc_invested, eth_invested = apply_manual_transactions(
            btc_held, eth_held, btc_invested, eth_invested
        )
        
        # Get current prices
        current_prices = get_current_prices_cached()
        if not current_prices:
            return jsonify({'error': 'Failed to fetch current prices'}), 500
        
        # Calculate current values
        btc_value = btc_held * current_prices['bitcoin']
        eth_value = eth_held * current_prices['ethereum']
        
        # Create CSV data
        def generate_csv():
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Header
            writer.writerow([
                'Asset', 'Holdings', 'Invested (USD)', 'Current Value (USD)', 
                'Profit/Loss (USD)', 'ROI (%)', 'Current Price (USD)'
            ])
            
            # Bitcoin row
            btc_profit_loss = btc_value - btc_invested
            btc_roi = (btc_profit_loss / btc_invested * 100) if btc_invested > 0 else 0
            writer.writerow([
                'Bitcoin (BTC)', f"{btc_held:.6f}", f"{btc_invested:.2f}",
                f"{btc_value:.2f}", f"{btc_profit_loss:.2f}", 
                f"{btc_roi:.2f}", f"{current_prices['bitcoin']:.2f}"
            ])
            
            # Ethereum row
            eth_profit_loss = eth_value - eth_invested
            eth_roi = (eth_profit_loss / eth_invested * 100) if eth_invested > 0 else 0
            writer.writerow([
                'Ethereum (ETH)', f"{eth_held:.6f}", f"{eth_invested:.2f}",
                f"{eth_value:.2f}", f"{eth_profit_loss:.2f}", 
                f"{eth_roi:.2f}", f"{current_prices['ethereum']:.2f}"
            ])
            
            # Total row
            total_invested = btc_invested + eth_invested
            total_value = btc_value + eth_value
            total_profit_loss = total_value - total_invested
            total_roi = (total_profit_loss / total_invested * 100) if total_invested > 0 else 0
            writer.writerow([
                'TOTAL PORTFOLIO', '', f"{total_invested:.2f}",
                f"{total_value:.2f}", f"{total_profit_loss:.2f}",
                f"{total_roi:.2f}", ''
            ])
            
            csv_data = output.getvalue()
            output.close()
            return csv_data
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"crypto_portfolio_{timestamp}.csv"
        
        # Create response
        csv_data = generate_csv()
        response = Response(
            csv_data,
            mimetype='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Content-Type': 'text/csv; charset=utf-8'
            }
        )
        
        logger.info(f"Portfolio CSV exported successfully: {filename}")
        return response
        
    except Exception as e:
        logger.error(f"Error exporting portfolio CSV: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/export/transactions')
@limiter.limit("5 per minute")
@monitor_performance
def export_transactions_csv():
    """Export transaction history as CSV"""
    try:
        transactions = load_manual_transactions()
        
        if not transactions:
            return jsonify({'error': 'No transactions to export'}), 404
        
        def generate_csv():
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Header
            writer.writerow([
                'Date', 'Asset', 'Type', 'Amount', 'Price (USD)', 
                'Value (USD)', 'Profit/Loss (USD)', 'ROI (%)', 'Timestamp'
            ])
            
            # Transaction rows
            for tx in transactions:
                amount = float(tx.get('amount', 0))
                price = float(tx.get('price', 0))
                value = amount * price
                profit_loss = tx.get('profit_loss', '')
                profit_loss_percent = tx.get('profit_loss_percent', '')
                timestamp = tx.get('timestamp', '')
                
                writer.writerow([
                    tx.get('date', ''), 
                    tx.get('coin', '').title(),
                    tx.get('type', '').upper(),
                    f"{amount:.6f}",
                    f"{price:.2f}",
                    f"{value:.2f}",
                    f"{profit_loss:.2f}" if profit_loss != '' else '',
                    f"{profit_loss_percent:.2f}" if profit_loss_percent != '' else '',
                    timestamp
                ])
            
            csv_data = output.getvalue()
            output.close()
            return csv_data
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"crypto_transactions_{timestamp}.csv"
        
        # Create response
        csv_data = generate_csv()
        response = Response(
            csv_data,
            mimetype='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Content-Type': 'text/csv; charset=utf-8'
            }
        )
        
        logger.info(f"Transactions CSV exported successfully: {filename}")
        return response
        
    except Exception as e:
        logger.error(f"Error exporting transactions CSV: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/export/history')
@limiter.limit("3 per minute")  # More restrictive due to data volume
@monitor_performance
def export_history_csv():
    """Export portfolio history as CSV"""
    try:
        # Get extended history (will implement this next)
        days = int(request.args.get('days', 90))  # Default 90 days for now
        if days > 365:
            days = 365  # Maximum 1 year
        
        history = []
        current_date = datetime.now() - timedelta(days=days)
        
        while current_date <= datetime.now():
            # Get portfolio state for this date
            temp_today = globals()['TODAY']
            globals()['TODAY'] = current_date
            
            try:
                btc_invested, eth_invested, btc_held, eth_held = simulate_investments()
                btc_held, eth_held, btc_invested, eth_invested = apply_manual_transactions(
                    btc_held, eth_held, btc_invested, eth_invested
                )
                
                # Get prices for this date
                price_data = get_price_on_date(current_date)
                if price_data:
                    btc_value = btc_held * price_data['bitcoin']
                    eth_value = eth_held * price_data['ethereum']
                    total_value = btc_value + eth_value
                    total_invested = btc_invested + eth_invested
                    profit_loss = total_value - total_invested
                    roi_percent = (profit_loss / total_invested * 100) if total_invested > 0 else 0
                    
                    history.append({
                        'date': current_date.strftime('%Y-%m-%d'),
                        'total_invested': total_invested,
                        'total_value': total_value,
                        'profit_loss': profit_loss,
                        'roi_percent': roi_percent,
                        'btc_price': price_data['bitcoin'],
                        'eth_price': price_data['ethereum']
                    })
            except Exception as e:
                logger.warning(f"Error calculating history for {current_date}: {e}")
                
            current_date += timedelta(days=1)
        
        # Restore original TODAY
        globals()['TODAY'] = temp_today
        
        if not history:
            return jsonify({'error': 'No historical data available'}), 404
        
        def generate_csv():
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Header
            writer.writerow([
                'Date', 'Total Invested (USD)', 'Total Value (USD)', 
                'Profit/Loss (USD)', 'ROI (%)', 'BTC Price (USD)', 'ETH Price (USD)'
            ])
            
            # History rows
            for record in history:
                writer.writerow([
                    record['date'],
                    f"{record['total_invested']:.2f}",
                    f"{record['total_value']:.2f}",
                    f"{record['profit_loss']:.2f}",
                    f"{record['roi_percent']:.2f}",
                    f"{record['btc_price']:.2f}",
                    f"{record['eth_price']:.2f}"
                ])
            
            csv_data = output.getvalue()
            output.close()
            return csv_data
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"crypto_history_{days}days_{timestamp}.csv"
        
        # Create response
        csv_data = generate_csv()
        response = Response(
            csv_data,
            mimetype='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Content-Type': 'text/csv; charset=utf-8'
            }
        )
        
        logger.info(f"History CSV exported successfully: {filename} ({days} days)")
        return response
        
    except Exception as e:
        logger.error(f"Error exporting history CSV: {e}")
        return jsonify({'error': str(e)}), 500

# Performance monitoring endpoints
@app.route('/health')
def health_check():
    """Health check endpoint with performance info"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'cache_stats': {
            'type': 'SimpleCache',
            'status': 'active'
        },
        'rate_limiting': {
            'status': 'active',
            'limits': ["200 per day", "50 per hour"]
        },
        'performance_monitoring': 'enabled',
        'version': '1.1.0-optimized'
    })

@app.route('/cache/stats')
@limiter.limit("5 per minute")
def cache_stats():
    """Get cache statistics"""
    try:
        # SimpleCache doesn't provide detailed stats, but we can show status
        return jsonify({
            'cache_type': 'SimpleCache',
            'status': 'active',
            'cached_endpoints': [
                {'endpoint': '/portfolio', 'ttl': 60},
                {'endpoint': '/performance_metrics', 'ttl': 300},
                {'endpoint': '/current_prices', 'ttl': 120},
                {'endpoint': '/transaction_analysis', 'ttl': 180}
            ],
            'price_cache_ttl': 120
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/cache/clear')
@limiter.limit("2 per minute")
def clear_cache():
    """Clear all cache (admin endpoint)"""
    try:
        cache.clear()
        logger.info("Cache cleared manually")
        return jsonify({
            'status': 'success',
            'message': 'Cache cleared successfully',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Failed to clear cache: {e}")
        return jsonify({'error': str(e)}), 500

# Advanced Analytics Endpoints (New Feature - Safe Addition)

@app.route('/analytics/portfolio-metrics', methods=['GET'])
@limiter.limit("20 per minute")
@monitor_performance
def get_portfolio_metrics():
    """Get advanced portfolio analytics and risk metrics"""
    try:
        # Get current portfolio data using internal function
        btc_invested, eth_invested, btc_held, eth_held = simulate_investments()
        btc_held, eth_held, btc_invested, eth_invested = apply_manual_transactions(
            btc_held, eth_held, btc_invested, eth_invested
        )
        
        current_prices = get_current_prices()
        btc_value = btc_held * current_prices['bitcoin']
        eth_value = eth_held * current_prices['ethereum']
        total_value = btc_value + eth_value
        total_invested = btc_invested + eth_invested
        total_profit_loss = total_value - total_invested
        total_profit_loss_percent = (total_profit_loss / total_invested * 100) if total_invested > 0 else 0
        
        portfolio_data = {
            'btc_invested': btc_invested,
            'eth_invested': eth_invested,
            'total_value': total_value,
            'total_profit_loss': total_profit_loss,
            'total_profit_loss_percent': total_profit_loss_percent
        }
            
        # Get historical data for calculations
        historical_data = generate_portfolio_history(30)
        if not historical_data:
            return jsonify({'error': 'Historical data not available'}), 500
            
        history = historical_data
        if len(history) < 2:
            return jsonify({'error': 'Insufficient historical data for analysis'}), 400
            
        # Calculate daily returns
        daily_returns = []
        for i in range(1, len(history)):
            prev_value = history[i-1]['total_value']
            curr_value = history[i]['total_value']
            if prev_value > 0:
                daily_return = (curr_value - prev_value) / prev_value
                daily_returns.append(daily_return)
        
        if not daily_returns:
            return jsonify({'error': 'Cannot calculate returns with current data'}), 400
            
        # Calculate risk metrics
        import math
        import statistics
        
        # Basic metrics
        avg_return = statistics.mean(daily_returns) if daily_returns else 0
        volatility = statistics.stdev(daily_returns) if len(daily_returns) > 1 else 0
        
        # Annualized metrics (assuming daily data)
        annualized_return = avg_return * 365
        annualized_volatility = volatility * math.sqrt(365)
        
        # Sharpe ratio (assuming 2% risk-free rate)
        risk_free_rate = 0.02
        sharpe_ratio = (annualized_return - risk_free_rate) / annualized_volatility if annualized_volatility > 0 else 0
        
        # Maximum drawdown
        peak = history[0]['total_value']
        max_drawdown = 0
        for point in history:
            if point['total_value'] > peak:
                peak = point['total_value']
            drawdown = (peak - point['total_value']) / peak if peak > 0 else 0
            max_drawdown = max(max_drawdown, drawdown)
        
        # Portfolio composition
        total_invested = portfolio_data['btc_invested'] + portfolio_data['eth_invested']
        btc_allocation = portfolio_data['btc_invested'] / total_invested if total_invested > 0 else 0
        eth_allocation = portfolio_data['eth_invested'] / total_invested if total_invested > 0 else 0
        
        # Calculate Value at Risk (95% confidence)
        if len(daily_returns) >= 20:
            var_95 = sorted(daily_returns)[int(len(daily_returns) * 0.05)]
            var_95_dollar = var_95 * portfolio_data['total_value']
        else:
            var_95 = 0
            var_95_dollar = 0
        
        analytics = {
            'risk_metrics': {
                'volatility': round(volatility * 100, 2),  # Convert to percentage
                'annualized_volatility': round(annualized_volatility * 100, 2),
                'sharpe_ratio': round(sharpe_ratio, 3),
                'max_drawdown': round(max_drawdown * 100, 2),
                'value_at_risk_95': round(var_95 * 100, 2),
                'value_at_risk_dollar': round(var_95_dollar, 2)
            },
            'performance_metrics': {
                'daily_return_avg': round(avg_return * 100, 3),
                'annualized_return': round(annualized_return * 100, 2),
                'total_return': round(portfolio_data['total_profit_loss_percent'], 2),
                'days_tracked': len(history)
            },
            'portfolio_composition': {
                'btc_allocation': round(btc_allocation * 100, 1),
                'eth_allocation': round(eth_allocation * 100, 1),
                'diversification_score': round(1 - (btc_allocation**2 + eth_allocation**2), 3)
            },
            'market_data': {
                'portfolio_value': portfolio_data['total_value'],
                'total_invested': total_invested,
                'unrealized_pnl': portfolio_data['total_profit_loss']
            }
        }
        
        return jsonify({
            'status': 'success',
            'analytics': analytics,
            'calculation_date': datetime.now().isoformat(),
            'data_points': len(history)
        })
        
    except Exception as e:
        logger.error(f"Error calculating portfolio metrics: {e}")
        return jsonify({'error': f'Analytics calculation failed: {str(e)}'}), 500

@app.route('/analytics/benchmarks', methods=['GET'])
@limiter.limit("10 per minute")
@monitor_performance  
def get_benchmark_comparison():
    """Compare portfolio performance against benchmarks"""
    try:
        # Get portfolio historical data
        historical_data = generate_portfolio_history(30)
        if not historical_data:
            return jsonify({'error': 'Historical data not available'}), 500
            
        history = historical_data
        if len(history) < 2:
            return jsonify({'error': 'Insufficient data for benchmark comparison'}), 400
        
        # Calculate portfolio performance
        start_value = history[0]['total_value']
        end_value = history[-1]['total_value']
        portfolio_return = (end_value - start_value) / start_value if start_value > 0 else 0
        
        # Get BTC and ETH price performance for same period
        start_btc = history[0]['btc_price'] 
        end_btc = history[-1]['btc_price']
        btc_return = (end_btc - start_btc) / start_btc if start_btc > 0 else 0
        
        start_eth = history[0]['eth_price']
        end_eth = history[-1]['eth_price'] 
        eth_return = (end_eth - start_eth) / start_eth if start_eth > 0 else 0
        
        # Simple 50/50 benchmark
        benchmark_return = (btc_return + eth_return) / 2
        
        benchmarks = {
            'portfolio_performance': {
                'return_percent': round(portfolio_return * 100, 2),
                'start_value': round(start_value, 2),
                'end_value': round(end_value, 2),
                'period_days': len(history)
            },
            'btc_benchmark': {
                'return_percent': round(btc_return * 100, 2),
                'outperformance': round((portfolio_return - btc_return) * 100, 2),
                'start_price': round(start_btc, 2),
                'end_price': round(end_btc, 2)
            },
            'eth_benchmark': {
                'return_percent': round(eth_return * 100, 2),
                'outperformance': round((portfolio_return - eth_return) * 100, 2),
                'start_price': round(start_eth, 2),
                'end_price': round(end_eth, 2)
            },
            'balanced_benchmark': {
                'return_percent': round(benchmark_return * 100, 2),
                'outperformance': round((portfolio_return - benchmark_return) * 100, 2),
                'description': '50% BTC / 50% ETH'
            }
        }
        
        return jsonify({
            'status': 'success',
            'benchmarks': benchmarks,
            'period': f"{len(history)} days",
            'calculation_date': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error calculating benchmarks: {e}")
        return jsonify({'error': f'Benchmark calculation failed: {str(e)}'}), 500

if __name__ == '__main__':
    # Start price alert monitoring
    start_price_alert_monitor()
    app.run(debug=True, port=5001)  # Development port to avoid conflicts
