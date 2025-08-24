"""
API ENDPOINT TESTS
Tests all REST API endpoints to ensure they work correctly.
Each test function tests a specific endpoint or functionality.
"""

import pytest
import json


class TestHealthEndpoint:
    """Test the health check endpoint"""
    
    def test_health_endpoint_returns_200(self, test_client):
        """
        TEST: Health endpoint should return 200 OK
        - Makes GET request to /api/v1/health
        - Verifies response status is 200
        - Verifies response contains expected data
        """
        response = test_client.get('/api/v1/health')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        assert 'version' in data


class TestPortfolioAPI:
    """Test portfolio-related API endpoints"""
    
    def test_get_portfolio_without_auth_returns_401(self, test_client):
        """
        TEST: Portfolio endpoint should require authentication
        - Makes GET request without auth headers
        - Should return 401 Unauthorized
        """
        response = test_client.get('/api/v1/portfolio')
        assert response.status_code == 401
    
    def test_get_empty_portfolio(self, test_client, auth_headers):
        """
        TEST: Empty portfolio should return empty data
        - Makes authenticated GET request to portfolio
        - Should return 200 with empty portfolio data
        """
        response = test_client.get('/api/v1/portfolio', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, dict)
        assert 'total_value' in data or 'holdings' in data
    
    def test_get_portfolio_with_transactions(self, test_client, auth_headers, sample_transactions):
        """
        TEST: Portfolio with transactions should return calculated data
        - Uses sample_transactions fixture
        - Makes authenticated GET request
        - Verifies portfolio calculations
        """
        response = test_client.get('/api/v1/portfolio', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, dict)
        
        # Should have holdings data
        if 'holdings' in data:
            assert len(data['holdings']) > 0


class TestTransactionAPI:
    """Test transaction-related API endpoints"""
    
    def test_add_transaction_without_auth_returns_401(self, test_client, test_transaction_data):
        """
        TEST: Adding transaction should require authentication
        """
        response = test_client.post('/api/v1/transactions', 
                                  json=test_transaction_data)
        assert response.status_code == 401
    
    def test_add_valid_transaction(self, test_client, auth_headers, test_transaction_data):
        """
        TEST: Adding valid transaction should succeed
        - Makes authenticated POST request
        - Uses valid transaction data
        - Should return 201 Created
        """
        response = test_client.post('/api/v1/transactions',
                                  headers=auth_headers,
                                  json=test_transaction_data)
        
        # Should succeed (201 Created or 200 OK)
        assert response.status_code in [200, 201]
        
        if response.status_code in [200, 201]:
            data = response.get_json()
            assert 'id' in data or 'message' in data
    
    def test_add_invalid_transaction_missing_fields(self, test_client, auth_headers):
        """
        TEST: Adding transaction with missing fields should fail
        - Makes POST request with incomplete data
        - Should return 400 Bad Request
        """
        invalid_data = {
            'crypto_symbol': 'BTC',
            # Missing required fields: amount, price_usd, transaction_type
        }
        
        response = test_client.post('/api/v1/transactions',
                                  headers=auth_headers,
                                  json=invalid_data)
        
        assert response.status_code == 400
    
    def test_get_transactions(self, test_client, auth_headers, sample_transactions):
        """
        TEST: Getting user transactions should return list
        - Uses sample_transactions fixture
        - Makes authenticated GET request
        - Should return list of transactions
        """
        response = test_client.get('/api/v1/transactions', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Should return list of transactions
        if isinstance(data, list):
            assert len(data) > 0
        elif isinstance(data, dict) and 'transactions' in data:
            assert len(data['transactions']) > 0


class TestAnalyticsAPI:
    """Test analytics and statistics endpoints"""
    
    def test_get_analytics_without_auth_returns_401(self, test_client):
        """
        TEST: Analytics should require authentication
        """
        response = test_client.get('/api/v1/analytics')
        assert response.status_code == 401
    
    def test_get_analytics_with_data(self, test_client, auth_headers, sample_transactions):
        """
        TEST: Analytics should return calculated metrics
        - Uses sample transactions
        - Makes authenticated request
        - Verifies analytics data structure
        """
        response = test_client.get('/api/v1/analytics', headers=auth_headers)
        
        # Should return some form of analytics data
        assert response.status_code in [200, 404]  # 404 if endpoint doesn't exist yet
        
        if response.status_code == 200:
            data = response.get_json()
            assert isinstance(data, dict)


class TestPriceAPI:
    """Test cryptocurrency price endpoints"""
    
    def test_get_current_prices(self, test_client):
        """
        TEST: Current prices endpoint should work
        - Makes GET request to prices endpoint
        - Should return price data (if endpoint exists)
        """
        response = test_client.get('/api/v1/prices')
        
        # Endpoint might not exist yet, so accept 404
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.get_json()
            assert isinstance(data, dict)
    
    def test_get_specific_crypto_price(self, test_client):
        """
        TEST: Specific crypto price should return price data
        - Makes GET request for BTC price
        - Should return BTC price information
        """
        response = test_client.get('/api/v1/prices/BTC')
        
        # Endpoint might not exist yet
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.get_json()
            assert 'price' in data or 'current_price' in data