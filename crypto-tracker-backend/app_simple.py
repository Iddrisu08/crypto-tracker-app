from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
import requests, json, os, time, logging
from datetime import datetime, timedelta, date
from decimal import Decimal
from functools import wraps

# Import our models and utilities
from config import config
from models import db, User, Transaction, PriceCache, PortfolioSnapshot, APILog
from database import initialize_database

def create_app(config_name=None):
    """Application factory pattern - Simplified without JWT auth."""
    app = Flask(__name__)
    
    # Configuration
    config_name = config_name or os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    
    # CORS with enhanced security
    CORS(app, 
         origins=[app.config['FRONTEND_URL'], "http://localhost:3000", "http://localhost:5173", "http://localhost:5174"], 
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
         supports_credentials=True)
    
    # Rate limiting
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=[f"{app.config['RATE_LIMIT_PER_MINUTE']} per minute"]
    )
    limiter.init_app(app)
    
    # Caching (simple memory cache, no Redis required)
    cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache'})
    
    # Logging setup
    if not app.debug:
        logging.basicConfig(level=logging.INFO)
    
    # API request logging middleware
    @app.before_request
    def log_request():
        """Log API requests for monitoring."""
        if request.endpoint and request.endpoint.startswith('api'):
            try:
                log_entry = APILog(
                    endpoint=request.endpoint,
                    method=request.method,
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent', ''),
                    timestamp=datetime.utcnow()
                )
                db.session.add(log_entry)
                db.session.commit()
            except Exception as e:
                app.logger.error(f"Failed to log request: {e}")
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request'}), 400

    # ==================== API ENDPOINTS ====================
    
    @app.route('/api/v1/health', methods=['GET'])
    def health():
        """Health check endpoint."""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '2.0.0-simplified'
        })
    
    @app.route('/api/v1/portfolio', methods=['GET'])
    @cache.cached(timeout=60)  # Cache for 1 minute
    @limiter.limit("30 per minute")
    def get_portfolio():
        """Get portfolio data - no auth required."""
        try:
            # Get default user's transactions (for backward compatibility)
            default_user = User.query.filter_by(username='default').first()
            if not default_user:
                # Create default user if doesn't exist
                default_user = User(
                    username='default',
                    email='default@local',
                    password_hash='dummy'  # Not used since no auth
                )
                db.session.add(default_user)
                db.session.commit()
            
            transactions = Transaction.query.filter_by(user_id=default_user.id).all()
            
            # Calculate portfolio metrics
            btc_transactions = [t for t in transactions if t.coin == 'bitcoin']
            eth_transactions = [t for t in transactions if t.coin == 'ethereum']
            
            # Get current prices
            current_prices = get_current_prices()
            btc_price = current_prices.get('bitcoin', 0)
            eth_price = current_prices.get('ethereum', 0)
            
            # Calculate BTC metrics
            btc_invested = float(sum(t.total_value_usd for t in btc_transactions if t.transaction_type == 'buy') - \
                          sum(t.total_value_usd for t in btc_transactions if t.transaction_type == 'sell'))
            btc_held = float(sum(t.amount for t in btc_transactions if t.transaction_type == 'buy') - \
                      sum(t.amount for t in btc_transactions if t.transaction_type == 'sell'))
            btc_value = btc_held * btc_price
            
            # Calculate ETH metrics
            eth_invested = float(sum(t.total_value_usd for t in eth_transactions if t.transaction_type == 'buy') - \
                          sum(t.total_value_usd for t in eth_transactions if t.transaction_type == 'sell'))
            eth_held = float(sum(t.amount for t in eth_transactions if t.transaction_type == 'buy') - \
                      sum(t.amount for t in eth_transactions if t.transaction_type == 'sell'))
            eth_value = eth_held * eth_price
            
            # Calculate totals
            total_invested = btc_invested + eth_invested
            total_value = btc_value + eth_value
            profit_loss = total_value - total_invested
            
            # Calculate percentages
            btc_percent_change = ((btc_value - btc_invested) / btc_invested * 100) if btc_invested > 0 else 0
            eth_percent_change = ((eth_value - eth_invested) / eth_invested * 100) if eth_invested > 0 else 0
            total_percent_change = ((total_value - total_invested) / total_invested * 100) if total_invested > 0 else 0
            
            return jsonify({
                'btc_invested': round(btc_invested, 2),
                'btc_held': round(btc_held, 8),
                'btc_value': round(btc_value, 2),
                'btc_percent_change': round(btc_percent_change, 2),
                'eth_invested': round(eth_invested, 2),
                'eth_held': round(eth_held, 8),
                'eth_value': round(eth_value, 2),
                'eth_percent_change': round(eth_percent_change, 2),
                'total_invested': round(total_invested, 2),
                'total_value': round(total_value, 2),
                'profit_loss': round(profit_loss, 2),
                'total_percent_change': round(total_percent_change, 2),
                'last_updated': datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            app.logger.error(f"Portfolio calculation error: {e}")
            return jsonify({'error': 'Failed to calculate portfolio'}), 500
    
    @app.route('/api/v1/performance-metrics', methods=['GET'])
    @cache.cached(timeout=300)  # Cache for 5 minutes
    @limiter.limit("20 per minute")
    def get_performance_metrics():
        """Get detailed performance metrics - no auth required."""
        try:
            # Get default user's data
            default_user = User.query.filter_by(username='default').first()
            if not default_user:
                return jsonify({'error': 'No data available'}), 404
            
            transactions = Transaction.query.filter_by(user_id=default_user.id).all()
            if not transactions:
                return jsonify({'error': 'No transactions found'}), 404
            
            # Get current prices
            current_prices = get_current_prices()
            btc_price = current_prices.get('bitcoin', 0)
            eth_price = current_prices.get('ethereum', 0)
            
            # Calculate metrics (simplified version)
            btc_transactions = [t for t in transactions if t.coin == 'bitcoin']
            eth_transactions = [t for t in transactions if t.coin == 'ethereum']
            
            # BTC calculations
            btc_invested = float(sum(t.total_value_usd for t in btc_transactions if t.transaction_type == 'buy'))
            btc_held = float(sum(t.amount for t in btc_transactions if t.transaction_type == 'buy'))
            btc_current_value = btc_held * btc_price
            btc_profit_loss = btc_current_value - btc_invested
            btc_roi = (btc_profit_loss / btc_invested * 100) if btc_invested > 0 else 0
            
            # ETH calculations
            eth_invested = float(sum(t.total_value_usd for t in eth_transactions if t.transaction_type == 'buy'))
            eth_held = float(sum(t.amount for t in eth_transactions if t.transaction_type == 'buy'))
            eth_current_value = eth_held * eth_price
            eth_profit_loss = eth_current_value - eth_invested
            eth_roi = (eth_profit_loss / eth_invested * 100) if eth_invested > 0 else 0
            
            # Total calculations
            total_invested = btc_invested + eth_invested
            total_current_value = btc_current_value + eth_current_value
            total_profit_loss = total_current_value - total_invested
            total_roi = (total_profit_loss / total_invested * 100) if total_invested > 0 else 0
            
            # Calculate days invested
            earliest_transaction = min(transactions, key=lambda t: t.transaction_date)
            earliest_date = earliest_transaction.transaction_date
            if isinstance(earliest_date, datetime):
                earliest_date = earliest_date.date()
            days_invested = (datetime.utcnow().date() - earliest_date).days
            
            # Annualized return
            annualized_return = (total_roi * 365 / days_invested) if days_invested > 0 else 0
            
            return jsonify({
                'total_metrics': {
                    'invested': round(total_invested, 2),
                    'current_value': round(total_current_value, 2),
                    'profit_loss': round(total_profit_loss, 2),
                    'roi_percent': round(total_roi, 2),
                    'annualized_return': round(annualized_return, 2),
                    'days_invested': days_invested
                },
                'btc_metrics': {
                    'invested': round(btc_invested, 2),
                    'current_value': round(btc_current_value, 2),
                    'profit_loss': round(btc_profit_loss, 2),
                    'roi_percent': round(btc_roi, 2),
                    'holdings': round(btc_held, 8),
                    'avg_purchase_price': round(btc_invested / btc_held, 2) if btc_held > 0 else 0,
                    'current_price': round(btc_price, 2),
                    'allocation_percent': round(btc_invested / total_invested * 100, 1) if total_invested > 0 else 0
                },
                'eth_metrics': {
                    'invested': round(eth_invested, 2),
                    'current_value': round(eth_current_value, 2),
                    'profit_loss': round(eth_profit_loss, 2),
                    'roi_percent': round(eth_roi, 2),
                    'holdings': round(eth_held, 8),
                    'avg_purchase_price': round(eth_invested / eth_held, 2) if eth_held > 0 else 0,
                    'current_price': round(eth_price, 2),
                    'allocation_percent': round(eth_invested / total_invested * 100, 1) if total_invested > 0 else 0
                },
                'dca_analysis': {
                    'dca_vs_lump_sum_percent': 0,  # Simplified - would need complex calculation
                    'total_weeks_invested': days_invested // 7,
                    'weekly_avg_investment': round(total_invested / (days_invested / 7), 2) if days_invested > 0 else 0
                },
                'performance_periods': {
                    'best_week': {'date': None, 'return_percent': 0},
                    'worst_week': {'date': None, 'return_percent': 0}
                }
            })
            
        except Exception as e:
            app.logger.error(f"Performance metrics error: {e}")
            return jsonify({'error': f'Failed to calculate performance metrics: {str(e)}'}), 500
    
    @app.route('/api/v1/transactions', methods=['GET'])
    @limiter.limit("30 per minute")
    def get_transactions():
        """Get user's transactions - no auth required."""
        try:
            page = request.args.get('page', 1, type=int)
            per_page = min(request.args.get('per_page', 20, type=int), 100)
            
            # Get default user
            default_user = User.query.filter_by(username='default').first()
            if not default_user:
                return jsonify({'transactions': [], 'total': 0, 'pages': 0, 'current_page': 1}), 200
            
            transactions = Transaction.query.filter_by(user_id=default_user.id)\
                .order_by(Transaction.transaction_date.desc())\
                .paginate(page=page, per_page=per_page, error_out=False)
            
            return jsonify({
                'transactions': [t.to_dict() for t in transactions.items],
                'total': transactions.total,
                'pages': transactions.pages,
                'current_page': transactions.page,
                'per_page': per_page
            })
            
        except Exception as e:
            app.logger.error(f"Transactions fetch error: {e}")
            return jsonify({'error': 'Failed to fetch transactions'}), 500
    
    @app.route('/api/v1/transactions', methods=['POST'])
    @limiter.limit("10 per minute")
    def add_transaction():
        """Add new transaction - no auth required."""
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['coin', 'type', 'amount', 'price', 'date']
            for field in required_fields:
                if field not in data:
                    return jsonify({'error': f'Missing required field: {field}'}), 400
            
            # Get or create default user
            default_user = User.query.filter_by(username='default').first()
            if not default_user:
                default_user = User(
                    username='default',
                    email='default@local',
                    password_hash='dummy'
                )
                db.session.add(default_user)
                db.session.commit()
            
            # Create transaction
            transaction = Transaction(
                user_id=default_user.id,
                coin=data['coin'],
                transaction_type=data['type'],
                amount=float(data['amount']),
                price_usd=float(data['price']),
                total_value_usd=float(data['amount']) * float(data['price']),
                transaction_date=datetime.strptime(data['date'], '%Y-%m-%d').date()
            )
            
            db.session.add(transaction)
            db.session.commit()
            
            return jsonify({
                'message': 'Transaction added successfully',
                'transaction': transaction.to_dict()
            }), 201
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Add transaction error: {e}")
            return jsonify({'error': f'Failed to add transaction: {str(e)}'}), 500
    
    @app.route('/api/v1/current-prices', methods=['GET'])
    @cache.cached(timeout=60)  # Cache for 1 minute
    @limiter.limit("60 per minute")
    def get_current_prices_endpoint():
        """Get current cryptocurrency prices."""
        try:
            prices = get_current_prices()
            return jsonify(prices)
        except Exception as e:
            app.logger.error(f"Price fetch error: {e}")
            return jsonify({'error': 'Failed to fetch current prices'}), 500
    
    # Helper functions
    def get_current_prices():
        """Fetch current prices from CoinGecko API with caching."""
        try:
            # Check cache first
            cached_prices = PriceCache.query.filter(
                PriceCache.created_at > datetime.utcnow() - timedelta(minutes=5)
            ).first()
            
            if cached_prices:
                # For now, return default prices since the cache structure is different
                # This is simplified version - will use live API calls
                pass
            
            # Fetch from API
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
            
            # For simplified version, we'll skip caching prices
            # The PriceCache model is different and more complex
            # Just return live prices
            
            return prices
            
        except Exception as e:
            app.logger.error(f"Price fetch error: {e}")
            # Return default prices if API fails
            app.logger.error(f"Using default prices due to API error: {e}")
            return {'bitcoin': 50000, 'ethereum': 3000}  # Default fallback prices
    
    # Initialize database
    with app.app_context():
        try:
            initialize_database()
            app.logger.info("Database initialized successfully")
        except Exception as e:
            app.logger.error(f"Database initialization failed: {e}")
    
    return app

# Create the app
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)