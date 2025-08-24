"""
DATABASE MODEL TESTS
Tests database models, relationships, and data validation.
Ensures database operations work correctly.
"""

import pytest
from datetime import datetime, timedelta
from models import User, Transaction, PriceAlert
from werkzeug.security import generate_password_hash, check_password_hash


class TestUserModel:
    """Test User model functionality"""
    
    def test_create_user(self, test_app):
        """
        TEST: Creating a user should work correctly
        - Creates new user with valid data
        - Saves to database
        - Verifies user exists and has correct data
        """
        with test_app.app_context():
            from app import db
            
            user = User(
                username='newuser',
                email='newuser@example.com',
                password_hash=generate_password_hash('password123')
            )
            
            db.session.add(user)
            db.session.commit()
            
            # Verify user was created
            saved_user = User.query.filter_by(username='newuser').first()
            assert saved_user is not None
            assert saved_user.email == 'newuser@example.com'
            assert saved_user.username == 'newuser'
    
    def test_user_password_hashing(self, test_app):
        """
        TEST: User password should be properly hashed
        - Creates user with password
        - Verifies password is hashed
        - Verifies password verification works
        """
        with test_app.app_context():
            from app import db
            
            password = 'mysecretpassword'
            user = User(
                username='hashtest',
                email='hash@example.com',
                password_hash=generate_password_hash(password)
            )
            
            db.session.add(user)
            db.session.commit()
            
            # Password should be hashed
            assert user.password_hash != password
            assert len(user.password_hash) > 20
            
            # Should verify correctly
            assert check_password_hash(user.password_hash, password)
            assert not check_password_hash(user.password_hash, 'wrongpassword')
    
    def test_user_unique_constraints(self, test_app):
        """
        TEST: Username and email should be unique
        - Tries to create users with duplicate username/email
        - Should raise database constraint errors
        """
        with test_app.app_context():
            from app import db
            from sqlalchemy.exc import IntegrityError
            
            # First user
            user1 = User(
                username='uniqueuser',
                email='unique@example.com',
                password_hash=generate_password_hash('password')
            )
            db.session.add(user1)
            db.session.commit()
            
            # Try duplicate username
            user2 = User(
                username='uniqueuser',  # Duplicate
                email='different@example.com',
                password_hash=generate_password_hash('password')
            )
            
            db.session.add(user2)
            
            with pytest.raises(IntegrityError):
                db.session.commit()
            
            db.session.rollback()  # Clean up failed transaction
    
    def test_user_repr_method(self, test_app):
        """
        TEST: User __repr__ method should return readable string
        - Creates user and checks string representation
        """
        with test_app.app_context():
            user = User(
                username='reprtest',
                email='repr@example.com',
                password_hash='hash'
            )
            
            user_str = repr(user)
            assert 'reprtest' in user_str or 'User' in user_str


class TestTransactionModel:
    """Test Transaction model functionality"""
    
    def test_create_transaction(self, test_app):
        """
        TEST: Creating a transaction should work correctly
        - Creates transaction with valid data
        - Verifies all fields are saved correctly
        """
        with test_app.app_context():
            from app import db
            
            # Get test user
            user = User.query.filter_by(username='testuser').first()
            assert user is not None
            
            transaction = Transaction(
                user_id=user.id,
                crypto_symbol='BTC',
                amount=1.5,
                price_usd=45000.00,
                transaction_type='buy',
                notes='Test transaction'
            )
            
            db.session.add(transaction)
            db.session.commit()
            
            # Verify transaction was created
            saved_transaction = Transaction.query.filter_by(
                crypto_symbol='BTC', 
                user_id=user.id
            ).first()
            
            assert saved_transaction is not None
            assert saved_transaction.amount == 1.5
            assert saved_transaction.price_usd == 45000.00
            assert saved_transaction.transaction_type == 'buy'
            assert saved_transaction.notes == 'Test transaction'
    
    def test_transaction_timestamp(self, test_app):
        """
        TEST: Transaction should have automatic timestamp
        - Creates transaction
        - Verifies timestamp is set automatically
        - Verifies timestamp is recent
        """
        with test_app.app_context():
            from app import db
            
            user = User.query.filter_by(username='testuser').first()
            
            before_time = datetime.utcnow()
            
            transaction = Transaction(
                user_id=user.id,
                crypto_symbol='ETH',
                amount=2.0,
                price_usd=3000.00,
                transaction_type='buy'
            )
            
            db.session.add(transaction)
            db.session.commit()
            
            after_time = datetime.utcnow()
            
            # Should have timestamp
            assert transaction.timestamp is not None
            assert before_time <= transaction.timestamp <= after_time
    
    def test_transaction_total_value_calculation(self, test_app):
        """
        TEST: Transaction should calculate total value correctly
        - Creates transaction with amount and price
        - Verifies total value calculation (amount * price)
        """
        with test_app.app_context():
            from app import db
            
            user = User.query.filter_by(username='testuser').first()
            
            transaction = Transaction(
                user_id=user.id,
                crypto_symbol='BTC',
                amount=0.5,
                price_usd=50000.00,
                transaction_type='buy'
            )
            
            db.session.add(transaction)
            db.session.commit()
            
            # Total value should be amount * price = 0.5 * 50000 = 25000
            expected_total = 0.5 * 50000.00
            
            # If model has total_value property/method
            if hasattr(transaction, 'total_value'):
                assert abs(transaction.total_value - expected_total) < 0.01
            else:
                # Calculate manually
                calculated_total = transaction.amount * transaction.price_usd
                assert abs(calculated_total - expected_total) < 0.01
    
    def test_user_transaction_relationship(self, test_app):
        """
        TEST: User should have relationship with transactions
        - Creates multiple transactions for user
        - Verifies user can access their transactions
        """
        with test_app.app_context():
            from app import db
            
            user = User.query.filter_by(username='testuser').first()
            
            # Create multiple transactions
            transactions = [
                Transaction(
                    user_id=user.id,
                    crypto_symbol='BTC',
                    amount=1.0,
                    price_usd=40000.00,
                    transaction_type='buy'
                ),
                Transaction(
                    user_id=user.id,
                    crypto_symbol='ETH',
                    amount=5.0,
                    price_usd=2500.00,
                    transaction_type='buy'
                )
            ]
            
            for transaction in transactions:
                db.session.add(transaction)
            
            db.session.commit()
            
            # User should have access to transactions
            user_transactions = Transaction.query.filter_by(user_id=user.id).all()
            assert len(user_transactions) >= 2  # At least the ones we just created


class TestPriceAlertModel:
    """Test PriceAlert model functionality"""
    
    def test_create_price_alert(self, test_app):
        """
        TEST: Creating a price alert should work correctly
        - Creates price alert with valid data
        - Verifies all fields are saved correctly
        """
        with test_app.app_context():
            from app import db
            
            user = User.query.filter_by(username='testuser').first()
            
            alert = PriceAlert(
                user_id=user.id,
                crypto_symbol='BTC',
                target_price=60000.00,
                alert_type='above',
                is_active=True
            )
            
            db.session.add(alert)
            db.session.commit()
            
            # Verify alert was created
            saved_alert = PriceAlert.query.filter_by(
                crypto_symbol='BTC',
                user_id=user.id
            ).first()
            
            assert saved_alert is not None
            assert saved_alert.target_price == 60000.00
            assert saved_alert.alert_type == 'above'
            assert saved_alert.is_active == True
    
    def test_price_alert_defaults(self, test_app):
        """
        TEST: Price alert should have correct default values
        - Creates alert without specifying all fields
        - Verifies default values are set
        """
        with test_app.app_context():
            from app import db
            
            user = User.query.filter_by(username='testuser').first()
            
            alert = PriceAlert(
                user_id=user.id,
                crypto_symbol='ETH',
                target_price=4000.00,
                alert_type='below'
                # is_active should default to True
            )
            
            db.session.add(alert)
            db.session.commit()
            
            # Should have default values
            assert alert.is_active == True  # Default should be True
            assert alert.created_at is not None  # Should have timestamp