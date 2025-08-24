from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    """User model for authentication."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    transactions = db.relationship('Transaction', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    portfolio_snapshots = db.relationship('PortfolioSnapshot', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Set password hash."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash."""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active
        }

class Transaction(db.Model):
    """Transaction model for tracking buys/sells."""
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    coin = db.Column(db.String(20), nullable=False, index=True)  # 'bitcoin', 'ethereum'
    transaction_type = db.Column(db.String(10), nullable=False)  # 'buy', 'sell'
    amount = db.Column(db.Numeric(20, 8), nullable=False)  # Amount of crypto
    price_usd = db.Column(db.Numeric(15, 2), nullable=False)  # Price per unit in USD
    total_value_usd = db.Column(db.Numeric(15, 2), nullable=False)  # Total transaction value
    transaction_date = db.Column(db.DateTime, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'coin': self.coin,
            'type': self.transaction_type,
            'amount': float(self.amount),
            'price_usd': float(self.price_usd),
            'total_value_usd': float(self.total_value_usd),
            'transaction_date': self.transaction_date.isoformat(),
            'created_at': self.created_at.isoformat()
        }

class PriceCache(db.Model):
    """Cache for cryptocurrency prices."""
    __tablename__ = 'price_cache'
    
    id = db.Column(db.Integer, primary_key=True)
    coin = db.Column(db.String(20), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    price_usd = db.Column(db.Numeric(15, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Composite index for efficient lookups
    __table_args__ = (
        db.UniqueConstraint('coin', 'date', name='unique_coin_date'),
    )
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'coin': self.coin,
            'date': self.date.isoformat(),
            'price_usd': float(self.price_usd)
        }

class PortfolioSnapshot(db.Model):
    """Portfolio value snapshots for performance tracking."""
    __tablename__ = 'portfolio_snapshots'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    snapshot_date = db.Column(db.DateTime, nullable=False, index=True)
    btc_held = db.Column(db.Numeric(20, 8), default=0)
    eth_held = db.Column(db.Numeric(20, 8), default=0)
    btc_value_usd = db.Column(db.Numeric(15, 2), default=0)
    eth_value_usd = db.Column(db.Numeric(15, 2), default=0)
    total_invested = db.Column(db.Numeric(15, 2), default=0)
    total_value_usd = db.Column(db.Numeric(15, 2), default=0)
    profit_loss_usd = db.Column(db.Numeric(15, 2), default=0)
    roi_percent = db.Column(db.Numeric(8, 4), default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'snapshot_date': self.snapshot_date.isoformat(),
            'btc_held': float(self.btc_held),
            'eth_held': float(self.eth_held),
            'btc_value_usd': float(self.btc_value_usd),
            'eth_value_usd': float(self.eth_value_usd),
            'total_invested': float(self.total_invested),
            'total_value_usd': float(self.total_value_usd),
            'profit_loss_usd': float(self.profit_loss_usd),
            'roi_percent': float(self.roi_percent)
        }

class APILog(db.Model):
    """API request logging for monitoring."""
    __tablename__ = 'api_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    endpoint = db.Column(db.String(255), nullable=False, index=True)
    method = db.Column(db.String(10), nullable=False)
    status_code = db.Column(db.Integer, nullable=False, index=True)
    response_time_ms = db.Column(db.Integer)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'endpoint': self.endpoint,
            'method': self.method,
            'status_code': self.status_code,
            'response_time_ms': self.response_time_ms,
            'created_at': self.created_at.isoformat()
        }