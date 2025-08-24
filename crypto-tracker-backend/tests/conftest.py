"""
TEST CONFIGURATION FILE
This file sets up the testing environment and provides fixtures for all tests.
Fixtures are reusable test components that can be shared across multiple test files.
"""

import pytest
import os
import tempfile
from app import app, db
from models import User, Transaction, PriceAlert
from werkzeug.security import generate_password_hash


@pytest.fixture
def test_app():
    """
    FIXTURE: Creates a test Flask application
    - Sets up test database (SQLite in memory)
    - Configures testing environment
    - Returns Flask app instance for testing
    """
    # Create temporary database file
    db_fd, db_path = tempfile.mkstemp()
    
    # Configure app for testing
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    app.config['SECRET_KEY'] = 'test-secret-key'
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    
    # Create application context
    with app.app_context():
        # Create all database tables
        db.create_all()
        
        # Add test data
        test_user = User(
            username='testuser',
            email='test@example.com',
            password_hash=generate_password_hash('testpassword')
        )
        db.session.add(test_user)
        db.session.commit()
        
        yield app  # This is where the test runs
        
        # Cleanup after test
        db.session.remove()
        db.drop_all()
    
    # Close and remove temporary database
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def test_client(test_app):
    """
    FIXTURE: Creates a test client for making HTTP requests
    - Uses the test_app fixture
    - Returns client that can make GET, POST, PUT, DELETE requests
    """
    return test_app.test_client()


@pytest.fixture
def test_user_data():
    """
    FIXTURE: Provides test user data
    - Returns dictionary with user registration data
    - Used for testing authentication endpoints
    """
    return {
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'newpassword123'
    }


@pytest.fixture
def test_transaction_data():
    """
    FIXTURE: Provides test transaction data
    - Returns dictionary with crypto transaction data
    - Used for testing portfolio endpoints
    """
    return {
        'crypto_symbol': 'BTC',
        'amount': 0.5,
        'price_usd': 50000.00,
        'transaction_type': 'buy',
        'notes': 'Test purchase'
    }


@pytest.fixture
def auth_headers(test_client, test_app):
    """
    FIXTURE: Provides authentication headers for protected endpoints
    - Logs in test user and gets JWT token
    - Returns headers dictionary with Authorization token
    """
    with test_app.app_context():
        # Login test user
        login_data = {
            'username': 'testuser',
            'password': 'testpassword'
        }
        
        response = test_client.post('/api/v1/auth/login', json=login_data)
        
        if response.status_code == 200:
            token = response.json.get('access_token')
            return {'Authorization': f'Bearer {token}'}
        
        return {}


@pytest.fixture
def sample_transactions(test_app, auth_headers):
    """
    FIXTURE: Creates sample transactions for testing
    - Adds multiple crypto transactions to database
    - Returns list of transaction IDs
    """
    with test_app.app_context():
        # Get test user
        user = User.query.filter_by(username='testuser').first()
        
        if not user:
            return []
        
        # Create sample transactions
        transactions = [
            Transaction(
                user_id=user.id,
                crypto_symbol='BTC',
                amount=0.5,
                price_usd=45000.00,
                transaction_type='buy'
            ),
            Transaction(
                user_id=user.id,
                crypto_symbol='ETH',
                amount=2.0,
                price_usd=3000.00,
                transaction_type='buy'
            ),
            Transaction(
                user_id=user.id,
                crypto_symbol='BTC',
                amount=0.1,
                price_usd=50000.00,
                transaction_type='sell'
            )
        ]
        
        for transaction in transactions:
            db.session.add(transaction)
        
        db.session.commit()
        
        return [t.id for t in transactions]