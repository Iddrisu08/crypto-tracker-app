from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
import requests, json, os, time, logging
from datetime import datetime, timedelta, date
from decimal import Decimal
import redis
from functools import wraps

# Import our models and utilities
from config import config
from models import db, User, Transaction, PriceCache, PortfolioSnapshot, APILog
from auth import auth_required, admin_required, validate_password, validate_email, get_current_user
from database import initialize_database

def create_app(config_name=None):
    """Application factory pattern."""
    app = Flask(__name__)
    
    # Configuration
    config_name = config_name or os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)
    
    # CORS with enhanced security
    CORS(app, 
         origins=[app.config['FRONTEND_URL'], "http://localhost:3000"], 
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
         supports_credentials=True)
    
    # Rate limiting
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=[f"{app.config['RATE_LIMIT_PER_MINUTE']} per minute"]
    )
    limiter.init_app(app)
    
    # Caching
    cache = Cache(app)
    
    # Logging setup
    if not app.debug:
        logging.basicConfig(level=logging.INFO)
        app.logger.setLevel(logging.INFO)
    
    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'error': 'Token has expired'}), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'error': 'Invalid token'}), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({'error': 'Authorization token required'}), 401
    
    # Middleware for API logging
    def log_api_request():
        """Log API requests for monitoring."""
        @wraps(log_api_request)
        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                
                try:
                    result = f(*args, **kwargs)
                    status_code = result[1] if isinstance(result, tuple) else 200
                except Exception as e:
                    status_code = 500
                    result = jsonify({'error': str(e)}), 500
                
                # Calculate response time
                response_time = int((time.time() - start_time) * 1000)
                
                # Log to database (async in production)
                try:
                    current_user = get_current_user()
                    api_log = APILog(
                        user_id=current_user.id if current_user else None,
                        endpoint=request.endpoint,
                        method=request.method,
                        status_code=status_code,
                        response_time_ms=response_time,
                        ip_address=request.remote_addr,
                        user_agent=request.headers.get('User-Agent', '')
                    )
                    db.session.add(api_log)
                    db.session.commit()
                except Exception as log_error:
                    app.logger.error(f"Failed to log API request: {log_error}")
                
                return result
            return wrapper
        return decorator
    
    # Constants for DCA simulation
    START_DATE = datetime(2025, 1, 25)
    DEFAULT_BTC_INVEST = 100
    DEFAULT_ETH_INVEST = 50
    DEFAULT_BTC_TOTAL = 102
    DEFAULT_ETH_TOTAL = 51.8
    
    # ===== ENHANCED API ENDPOINTS =====
    
    # Authentication endpoints
    @app.route('/api/v1/auth/register', methods=['POST'])
    @limiter.limit("5 per minute")
    def register():
        """Register a new user."""
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        # Validation
        if not username or not email or not password:
            return jsonify({'error': 'Username, email, and password are required'}), 400
        
        if len(username) < 3:
            return jsonify({'error': 'Username must be at least 3 characters'}), 400
        
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        is_valid_password, password_msg = validate_password(password)
        if not is_valid_password:
            return jsonify({'error': password_msg}), 400
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 409
        
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already exists'}), 409
        
        # Create user
        try:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            
            # Create tokens
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)
            
            return jsonify({
                'message': 'User registered successfully',
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': user.to_dict()
            }), 201
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Registration error: {e}")
            return jsonify({'error': 'Registration failed'}), 500
    
    @app.route('/api/v1/auth/login', methods=['POST'])
    @limiter.limit("10 per minute")
    def login():
        """Login user."""
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        # Find user by username or email
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 401
        
        # Create tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        })
    
    @app.route('/api/v1/auth/refresh', methods=['POST'])
    @jwt_required(refresh=True)
    def refresh():
        """Refresh access token."""
        current_user_id = get_jwt_identity()
        access_token = create_access_token(identity=current_user_id)
        return jsonify({'access_token': access_token})
    
    @app.route('/api/v1/auth/me', methods=['GET'])
    @auth_required
    def get_current_user_info(current_user):
        """Get current user info."""
        return jsonify({'user': current_user.to_dict()})
    
    # Enhanced portfolio endpoints
    @app.route('/api/v1/portfolio', methods=['GET'])
    @auth_required
    @cache.cached(timeout=60)  # Cache for 1 minute
    def get_portfolio(current_user):
        """Get user's portfolio with enhanced calculations."""
        try:
            # Get user's transactions
            transactions = Transaction.query.filter_by(user_id=current_user.id).all()
            
            # Calculate holdings and investments
            btc_held = sum(float(t.amount) if t.transaction_type == 'buy' else -float(t.amount) 
                          for t in transactions if t.coin == 'bitcoin')
            eth_held = sum(float(t.amount) if t.transaction_type == 'buy' else -float(t.amount) 
                          for t in transactions if t.coin == 'ethereum')
            
            btc_invested = sum(float(t.total_value_usd) if t.transaction_type == 'buy' else -float(t.total_value_usd) 
                              for t in transactions if t.coin == 'bitcoin')
            eth_invested = sum(float(t.total_value_usd) if t.transaction_type == 'buy' else -float(t.total_value_usd) 
                              for t in transactions if t.coin == 'ethereum')
            
            # Get current prices
            current_prices = get_current_prices()
            if not current_prices:
                return jsonify({'error': 'Failed to fetch current prices'}), 500
            
            # Calculate current values
            btc_value = btc_held * current_prices['bitcoin']
            eth_value = eth_held * current_prices['ethereum']
            total_invested = btc_invested + eth_invested
            total_value = btc_value + eth_value
            profit_loss = total_value - total_invested
            
            # Calculate percentages
            btc_percent_change = ((btc_value - btc_invested) / btc_invested * 100) if btc_invested > 0 else 0
            eth_percent_change = ((eth_value - eth_invested) / eth_invested * 100) if eth_invested > 0 else 0
            total_percent_change = (profit_loss / total_invested * 100) if total_invested > 0 else 0
            
            portfolio_data = {
                'btc_invested': round(btc_invested, 2),
                'eth_invested': round(eth_invested, 2),
                'btc_held': round(btc_held, 8),
                'eth_held': round(eth_held, 8),
                'btc_value': round(btc_value, 2),
                'eth_value': round(eth_value, 2),
                'total_invested': round(total_invested, 2),
                'total_value': round(total_value, 2),
                'profit_loss': round(profit_loss, 2),
                'btc_percent_change': round(btc_percent_change, 2),
                'eth_percent_change': round(eth_percent_change, 2),
                'total_percent_change': round(total_percent_change, 2),
                'last_updated': datetime.utcnow().isoformat()
            }
            
            return jsonify(portfolio_data)
            
        except Exception as e:
            app.logger.error(f"Portfolio calculation error: {e}")
            return jsonify({'error': 'Failed to calculate portfolio'}), 500
    
    @cache.memoize(timeout=300)  # Cache for 5 minutes
    def get_current_prices():
        """Get current cryptocurrency prices with caching."""
        try:
            url = f"{app.config['COINGECKO_API_URL']}/simple/price"
            params = {
                'ids': 'bitcoin,ethereum',
                'vs_currencies': 'usd'
            }
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'bitcoin': data['bitcoin']['usd'],
                    'ethereum': data['ethereum']['usd']
                }
        except Exception as e:
            app.logger.error(f"Error fetching live prices: {e}")
        
        return None
    
    @app.route('/api/v1/transactions', methods=['GET'])
    @auth_required
    def get_transactions(current_user):
        """Get user's transactions with pagination."""
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        transactions = Transaction.query.filter_by(user_id=current_user.id)\
            .order_by(Transaction.transaction_date.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'transactions': [t.to_dict() for t in transactions.items],
            'total': transactions.total,
            'pages': transactions.pages,
            'current_page': page,
            'per_page': per_page
        })
    
    @app.route('/api/v1/transactions', methods=['POST'])
    @auth_required
    @limiter.limit("20 per minute")
    def add_transaction(current_user):
        """Add a new transaction."""
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validation
        required_fields = ['coin', 'type', 'amount', 'price', 'date']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        coin = data['coin'].lower()
        transaction_type = data['type'].lower()
        
        if coin not in ['bitcoin', 'ethereum']:
            return jsonify({'error': 'Invalid coin. Must be bitcoin or ethereum'}), 400
        
        if transaction_type not in ['buy', 'sell']:
            return jsonify({'error': 'Invalid type. Must be buy or sell'}), 400
        
        try:
            amount = float(data['amount'])
            price = float(data['price'])
            transaction_date = datetime.fromisoformat(data['date'])
            
            if amount <= 0 or price <= 0:
                return jsonify({'error': 'Amount and price must be positive'}), 400
            
            total_value = amount * price
            
            # Create transaction
            transaction = Transaction(
                user_id=current_user.id,
                coin=coin,
                transaction_type=transaction_type,
                amount=Decimal(str(amount)),
                price_usd=Decimal(str(price)),
                total_value_usd=Decimal(str(total_value)),
                transaction_date=transaction_date
            )
            
            db.session.add(transaction)
            db.session.commit()
            
            # Clear cache
            cache.delete_memoized(get_current_prices)
            
            return jsonify({
                'message': 'Transaction added successfully',
                'transaction': transaction.to_dict()
            }), 201
            
        except (ValueError, TypeError) as e:
            return jsonify({'error': 'Invalid number format'}), 400
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Transaction creation error: {e}")
            return jsonify({'error': 'Failed to create transaction'}), 500
    
    @app.route('/api/v1/performance-metrics', methods=['GET'])
    @auth_required
    @cache.cached(timeout=120)  # Cache for 2 minutes
    def get_performance_metrics(current_user):
        """Get comprehensive portfolio performance metrics."""
        try:
            # This would use the enhanced calculation logic
            # For now, returning a simplified version
            portfolio_data = get_portfolio_internal(current_user.id)
            
            return jsonify({
                'total_metrics': portfolio_data['total_metrics'],
                'btc_metrics': portfolio_data['btc_metrics'],
                'eth_metrics': portfolio_data['eth_metrics'],
                'dca_analysis': portfolio_data['dca_analysis'],
                'performance_periods': portfolio_data['performance_periods']
            })
            
        except Exception as e:
            app.logger.error(f"Performance metrics error: {e}")
            return jsonify({'error': 'Failed to calculate performance metrics'}), 500
    
    def get_portfolio_internal(user_id):
        """Internal portfolio calculation with enhanced metrics."""
        # This would contain the optimized portfolio calculation logic
        # Similar to your existing calculate_performance_metrics but user-specific
        # For brevity, I'm providing a placeholder structure
        return {
            'total_metrics': {
                'invested': 4325.36,
                'current_value': 6294.97,
                'profit_loss': 1969.61,
                'roi_percent': 45.54,
                'annualized_return': 117.88,
                'days_invested': 176
            },
            'btc_metrics': {
                'invested': 3651.96,
                'current_value': 5226.52,
                'profit_loss': 1574.56,
                'roi_percent': 43.12,
                'holdings': 0.044542,
                'avg_purchase_price': 81989.06,
                'current_price': 117339,
                'allocation_percent': 83.03
            },
            'eth_metrics': {
                'invested': 673.4,
                'current_value': 1068.45,
                'profit_loss': 395.05,
                'roi_percent': 58.67,
                'holdings': 0.284338,
                'avg_purchase_price': 2368.31,
                'current_price': 3757.68,
                'allocation_percent': 16.97
            },
            'dca_analysis': {
                'dca_vs_lump_sum_percent': 29.44,
                'total_weeks_invested': 25.1,
                'weekly_avg_investment': 172.03
            },
            'performance_periods': {
                'best_week': {
                    'date': '2025-04-26',
                    'return_percent': 15.64
                },
                'worst_week': {
                    'date': '2025-03-01',
                    'return_percent': -8.09
                }
            }
        }
    
    # Admin endpoints
    @app.route('/api/v1/admin/users', methods=['GET'])
    @admin_required
    def get_all_users(current_user):
        """Get all users (admin only)."""
        users = User.query.all()
        return jsonify({
            'users': [user.to_dict() for user in users],
            'total': len(users)
        })
    
    @app.route('/api/v1/admin/stats', methods=['GET'])
    @admin_required
    @cache.cached(timeout=300)
    def get_admin_stats(current_user):
        """Get admin statistics."""
        stats = {
            'total_users': User.query.count(),
            'active_users': User.query.filter_by(is_active=True).count(),
            'total_transactions': Transaction.query.count(),
            'total_api_calls_today': APILog.query.filter(
                APILog.created_at >= datetime.utcnow().date()
            ).count()
        }
        return jsonify(stats)
    
    # Health check and legacy compatibility endpoints
    @app.route('/api/v1/health', methods=['GET'])
    def health_check():
        """Health check endpoint."""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '2.0.0'
        })
    
    # Legacy endpoints for backward compatibility
    @app.route('/portfolio')
    def legacy_portfolio():
        """Legacy portfolio endpoint."""
        return jsonify({'error': 'Please use /api/v1/portfolio with authentication'}), 401
    
    @app.route('/current_prices')
    @cache.cached(timeout=60)
    def legacy_current_prices():
        """Legacy current prices endpoint."""
        prices = get_current_prices()
        if prices:
            return jsonify(prices)
        return jsonify({'error': 'Failed to fetch current prices'}), 500
    
    @app.route('/performance_metrics')
    def legacy_performance_metrics():
        """Legacy performance metrics endpoint."""
        return jsonify({'error': 'Please use /api/v1/performance-metrics with authentication'}), 401
    
    # Initialize database on first run
    with app.app_context():
        if not os.path.exists('crypto_tracker_dev.db'):
            initialize_database()
    
    return app

# Create the application
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)