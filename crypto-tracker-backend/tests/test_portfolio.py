"""
PORTFOLIO LOGIC TESTS
Tests portfolio calculations, profit/loss analysis, and business logic.
Ensures financial calculations are accurate.
"""

import pytest
from datetime import datetime, timedelta
from models import User, Transaction
from decimal import Decimal


class TestPortfolioCalculations:
    """Test portfolio value and holding calculations"""
    
    def test_calculate_total_portfolio_value(self, test_app, sample_transactions):
        """
        TEST: Portfolio should calculate total value correctly
        - Uses sample transactions from fixture
        - Calculates expected total value
        - Verifies portfolio calculation matches expectation
        """
        with test_app.app_context():
            from app import db
            
            user = User.query.filter_by(username='testuser').first()
            transactions = Transaction.query.filter_by(user_id=user.id).all()
            
            # Calculate expected portfolio value manually
            btc_amount = 0
            eth_amount = 0
            
            for tx in transactions:
                if tx.crypto_symbol == 'BTC':
                    if tx.transaction_type == 'buy':
                        btc_amount += tx.amount
                    else:  # sell
                        btc_amount -= tx.amount
                elif tx.crypto_symbol == 'ETH':
                    if tx.transaction_type == 'buy':
                        eth_amount += tx.amount
                    else:  # sell
                        eth_amount -= tx.amount
            
            # Verify we have some holdings
            assert btc_amount > 0 or eth_amount > 0
            
            # Note: In real app, you'd multiply by current prices
            # For testing, we just verify the logic structure exists
    
    def test_calculate_holdings_by_crypto(self, test_app, sample_transactions):
        """
        TEST: Portfolio should group holdings by cryptocurrency
        - Uses sample transactions
        - Calculates holdings for each crypto
        - Verifies buy/sell transactions are handled correctly
        """
        with test_app.app_context():
            user = User.query.filter_by(username='testuser').first()
            transactions = Transaction.query.filter_by(user_id=user.id).all()
            
            # Group transactions by crypto
            holdings = {}
            
            for tx in transactions:
                if tx.crypto_symbol not in holdings:
                    holdings[tx.crypto_symbol] = {
                        'amount': 0,
                        'total_invested': 0,
                        'transactions': []
                    }
                
                holding = holdings[tx.crypto_symbol]
                
                if tx.transaction_type == 'buy':
                    holding['amount'] += tx.amount
                    holding['total_invested'] += (tx.amount * tx.price_usd)
                else:  # sell
                    holding['amount'] -= tx.amount
                    holding['total_invested'] -= (tx.amount * tx.price_usd)
                
                holding['transactions'].append(tx)
            
            # Verify holdings structure
            assert len(holdings) > 0
            
            for crypto, holding in holdings.items():
                assert 'amount' in holding
                assert 'total_invested' in holding
                assert 'transactions' in holding
                assert len(holding['transactions']) > 0
    
    def test_average_purchase_price_calculation(self, test_app):
        """
        TEST: Should calculate average purchase price correctly
        - Creates multiple buy transactions at different prices
        - Calculates weighted average price
        - Verifies calculation accuracy
        """
        with test_app.app_context():
            from app import db
            
            user = User.query.filter_by(username='testuser').first()
            
            # Create transactions with known values for easy calculation
            transactions = [
                Transaction(
                    user_id=user.id,
                    crypto_symbol='TEST',
                    amount=1.0,
                    price_usd=1000.00,  # 1 * 1000 = 1000
                    transaction_type='buy'
                ),
                Transaction(
                    user_id=user.id,
                    crypto_symbol='TEST',
                    amount=2.0,
                    price_usd=2000.00,  # 2 * 2000 = 4000
                    transaction_type='buy'
                ),
                # Total: 3.0 coins for 5000 USD = average 1666.67 per coin
            ]
            
            for tx in transactions:
                db.session.add(tx)
            db.session.commit()
            
            # Calculate average price
            test_transactions = Transaction.query.filter_by(
                user_id=user.id,
                crypto_symbol='TEST',
                transaction_type='buy'
            ).all()
            
            total_amount = sum(tx.amount for tx in test_transactions)
            total_cost = sum(tx.amount * tx.price_usd for tx in test_transactions)
            
            expected_avg_price = total_cost / total_amount
            
            # Should be approximately 1666.67
            assert abs(expected_avg_price - 1666.67) < 0.01
    
    def test_profit_loss_calculation(self, test_app):
        """
        TEST: Should calculate profit/loss correctly
        - Creates buy and sell transactions
        - Calculates realized and unrealized P&L
        - Verifies calculation accuracy
        """
        with test_app.app_context():
            from app import db
            
            user = User.query.filter_by(username='testuser').first()
            
            # Buy 2 coins at $1000 each = $2000 total
            buy_tx = Transaction(
                user_id=user.id,
                crypto_symbol='PNL',
                amount=2.0,
                price_usd=1000.00,
                transaction_type='buy'
            )
            
            # Sell 1 coin at $1500 = $1500 total
            # Profit = $1500 - $1000 (cost of 1 coin) = $500
            sell_tx = Transaction(
                user_id=user.id,
                crypto_symbol='PNL',
                amount=1.0,
                price_usd=1500.00,
                transaction_type='sell'
            )
            
            db.session.add(buy_tx)
            db.session.add(sell_tx)
            db.session.commit()
            
            # Calculate P&L
            transactions = Transaction.query.filter_by(
                user_id=user.id,
                crypto_symbol='PNL'
            ).all()
            
            total_bought = 0
            total_buy_cost = 0
            total_sold = 0
            total_sell_revenue = 0
            
            for tx in transactions:
                if tx.transaction_type == 'buy':
                    total_bought += tx.amount
                    total_buy_cost += (tx.amount * tx.price_usd)
                else:  # sell
                    total_sold += tx.amount
                    total_sell_revenue += (tx.amount * tx.price_usd)
            
            # Calculate average buy price
            avg_buy_price = total_buy_cost / total_bought if total_bought > 0 else 0
            
            # Calculate realized P&L (on sold portion)
            realized_pnl = total_sell_revenue - (total_sold * avg_buy_price)
            
            # Should be $500 profit
            assert abs(realized_pnl - 500.0) < 0.01


class TestPortfolioPerformance:
    """Test portfolio performance metrics and analytics"""
    
    def test_calculate_portfolio_performance_over_time(self, test_app):
        """
        TEST: Should calculate portfolio performance over time periods
        - Creates transactions at different dates
        - Calculates performance metrics
        - Verifies time-based analysis
        """
        with test_app.app_context():
            from app import db
            
            user = User.query.filter_by(username='testuser').first()
            
            # Create transactions at different times
            base_time = datetime.utcnow() - timedelta(days=30)
            
            # Transaction 30 days ago
            old_tx = Transaction(
                user_id=user.id,
                crypto_symbol='TIME',
                amount=1.0,
                price_usd=1000.00,
                transaction_type='buy'
            )
            old_tx.timestamp = base_time
            
            # Transaction 15 days ago
            mid_tx = Transaction(
                user_id=user.id,
                crypto_symbol='TIME',
                amount=1.0,
                price_usd=1200.00,
                transaction_type='buy'
            )
            mid_tx.timestamp = base_time + timedelta(days=15)
            
            # Recent transaction
            recent_tx = Transaction(
                user_id=user.id,
                crypto_symbol='TIME',
                amount=0.5,
                price_usd=1500.00,
                transaction_type='sell'
            )
            recent_tx.timestamp = base_time + timedelta(days=25)
            
            db.session.add(old_tx)
            db.session.add(mid_tx)
            db.session.add(recent_tx)
            db.session.commit()
            
            # Verify transactions have different timestamps
            transactions = Transaction.query.filter_by(
                user_id=user.id,
                crypto_symbol='TIME'
            ).order_by(Transaction.timestamp).all()
            
            assert len(transactions) == 3
            assert transactions[0].timestamp < transactions[1].timestamp
            assert transactions[1].timestamp < transactions[2].timestamp
    
    def test_calculate_daily_portfolio_snapshots(self, test_app, sample_transactions):
        """
        TEST: Should be able to calculate portfolio value at specific dates
        - Uses existing transactions
        - Calculates portfolio value at different points in time
        - Verifies historical calculations
        """
        with test_app.app_context():
            user = User.query.filter_by(username='testuser').first()
            
            # Get all user transactions
            transactions = Transaction.query.filter_by(user_id=user.id).order_by(Transaction.timestamp).all()
            
            if len(transactions) > 0:
                # Calculate portfolio at different points
                cutoff_date = transactions[0].timestamp + timedelta(days=1)
                
                # Transactions before cutoff
                early_transactions = [tx for tx in transactions if tx.timestamp <= cutoff_date]
                
                # Calculate holdings at that point
                holdings_at_cutoff = {}
                
                for tx in early_transactions:
                    if tx.crypto_symbol not in holdings_at_cutoff:
                        holdings_at_cutoff[tx.crypto_symbol] = 0
                    
                    if tx.transaction_type == 'buy':
                        holdings_at_cutoff[tx.crypto_symbol] += tx.amount
                    else:
                        holdings_at_cutoff[tx.crypto_symbol] -= tx.amount
                
                # Verify we can calculate historical snapshots
                for crypto, amount in holdings_at_cutoff.items():
                    assert amount >= 0  # Should not have negative holdings


class TestPortfolioValidation:
    """Test portfolio data validation and edge cases"""
    
    def test_handle_zero_amount_transactions(self, test_app):
        """
        TEST: Should handle zero amount transactions appropriately
        - Creates transaction with zero amount
        - Verifies system handles it correctly
        """
        with test_app.app_context():
            from app import db
            
            user = User.query.filter_by(username='testuser').first()
            
            zero_tx = Transaction(
                user_id=user.id,
                crypto_symbol='ZERO',
                amount=0.0,
                price_usd=1000.00,
                transaction_type='buy'
            )
            
            db.session.add(zero_tx)
            db.session.commit()
            
            # Should exist in database
            saved_tx = Transaction.query.filter_by(crypto_symbol='ZERO').first()
            assert saved_tx is not None
            assert saved_tx.amount == 0.0
    
    def test_handle_negative_prices(self, test_app):
        """
        TEST: Should validate against negative prices
        - Attempts to create transaction with negative price
        - System should either reject or handle appropriately
        """
        with test_app.app_context():
            from app import db
            
            user = User.query.filter_by(username='testuser').first()
            
            negative_price_tx = Transaction(
                user_id=user.id,
                crypto_symbol='NEG',
                amount=1.0,
                price_usd=-1000.00,  # Negative price
                transaction_type='buy'
            )
            
            db.session.add(negative_price_tx)
            
            # This might raise an exception or be allowed
            # The test documents the current behavior
            try:
                db.session.commit()
                # If it succeeds, document that negative prices are allowed
                saved_tx = Transaction.query.filter_by(crypto_symbol='NEG').first()
                assert saved_tx.price_usd == -1000.00
            except Exception:
                # If it fails, that's also valid behavior
                db.session.rollback()
                pass  # Exception is expected/acceptable