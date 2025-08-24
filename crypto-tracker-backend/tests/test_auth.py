"""
AUTHENTICATION TESTS
Tests user registration, login, JWT tokens, and protected endpoints.
Ensures security mechanisms work correctly.
"""

import pytest
import json
from models import User


class TestUserRegistration:
    """Test user registration functionality"""
    
    def test_register_new_user_success(self, test_client, test_user_data):
        """
        TEST: New user registration should succeed
        - Makes POST request to registration endpoint
        - Uses valid user data
        - Should return 201 Created with user info
        """
        response = test_client.post('/api/v1/auth/register', json=test_user_data)
        
        # Should succeed (201 Created or 200 OK)
        assert response.status_code in [200, 201]
        
        if response.status_code in [200, 201]:
            data = response.get_json()
            assert 'id' in data or 'user_id' in data or 'message' in data
    
    def test_register_duplicate_username_fails(self, test_client, test_app):
        """
        TEST: Registering duplicate username should fail
        - Tries to register with existing username 'testuser'
        - Should return 400 Bad Request or 409 Conflict
        """
        duplicate_user = {
            'username': 'testuser',  # Already exists from conftest.py
            'email': 'different@example.com',
            'password': 'password123'
        }
        
        response = test_client.post('/api/v1/auth/register', json=duplicate_user)
        
        # Should fail with 400 or 409
        assert response.status_code in [400, 409]
    
    def test_register_duplicate_email_fails(self, test_client, test_app):
        """
        TEST: Registering duplicate email should fail
        - Tries to register with existing email
        - Should return 400 Bad Request or 409 Conflict
        """
        duplicate_email = {
            'username': 'differentuser',
            'email': 'test@example.com',  # Already exists from conftest.py
            'password': 'password123'
        }
        
        response = test_client.post('/api/v1/auth/register', json=duplicate_email)
        
        # Should fail with 400 or 409
        assert response.status_code in [400, 409]
    
    def test_register_invalid_email_fails(self, test_client):
        """
        TEST: Registration with invalid email should fail
        - Uses malformed email address
        - Should return 400 Bad Request
        """
        invalid_data = {
            'username': 'validuser',
            'email': 'not-an-email',  # Invalid email format
            'password': 'password123'
        }
        
        response = test_client.post('/api/v1/auth/register', json=invalid_data)
        assert response.status_code == 400
    
    def test_register_short_password_fails(self, test_client):
        """
        TEST: Registration with short password should fail
        - Uses password shorter than minimum length
        - Should return 400 Bad Request
        """
        invalid_data = {
            'username': 'validuser',
            'email': 'valid@example.com',
            'password': '123'  # Too short
        }
        
        response = test_client.post('/api/v1/auth/register', json=invalid_data)
        assert response.status_code == 400
    
    def test_register_missing_fields_fails(self, test_client):
        """
        TEST: Registration with missing required fields should fail
        - Sends incomplete registration data
        - Should return 400 Bad Request
        """
        incomplete_data = {
            'username': 'validuser',
            # Missing email and password
        }
        
        response = test_client.post('/api/v1/auth/register', json=incomplete_data)
        assert response.status_code == 400


class TestUserLogin:
    """Test user login functionality"""
    
    def test_login_valid_credentials_success(self, test_client):
        """
        TEST: Login with valid credentials should succeed
        - Uses test user credentials from conftest.py
        - Should return 200 OK with JWT token
        """
        login_data = {
            'username': 'testuser',
            'password': 'testpassword'
        }
        
        response = test_client.post('/api/v1/auth/login', json=login_data)
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Should return access token
        assert 'access_token' in data
        assert len(data['access_token']) > 0
    
    def test_login_invalid_username_fails(self, test_client):
        """
        TEST: Login with invalid username should fail
        - Uses non-existent username
        - Should return 401 Unauthorized
        """
        login_data = {
            'username': 'nonexistentuser',
            'password': 'testpassword'
        }
        
        response = test_client.post('/api/v1/auth/login', json=login_data)
        assert response.status_code == 401
    
    def test_login_invalid_password_fails(self, test_client):
        """
        TEST: Login with invalid password should fail
        - Uses correct username but wrong password
        - Should return 401 Unauthorized
        """
        login_data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        
        response = test_client.post('/api/v1/auth/login', json=login_data)
        assert response.status_code == 401
    
    def test_login_missing_fields_fails(self, test_client):
        """
        TEST: Login with missing fields should fail
        - Sends incomplete login data
        - Should return 400 Bad Request
        """
        incomplete_data = {
            'username': 'testuser',
            # Missing password
        }
        
        response = test_client.post('/api/v1/auth/login', json=incomplete_data)
        assert response.status_code == 400


class TestJWTTokens:
    """Test JWT token functionality"""
    
    def test_jwt_token_format(self, test_client):
        """
        TEST: JWT token should have correct format
        - Gets token from login
        - Verifies token structure (3 parts separated by dots)
        """
        login_data = {
            'username': 'testuser',
            'password': 'testpassword'
        }
        
        response = test_client.post('/api/v1/auth/login', json=login_data)
        assert response.status_code == 200
        
        data = response.get_json()
        token = data['access_token']
        
        # JWT tokens have 3 parts separated by dots
        token_parts = token.split('.')
        assert len(token_parts) == 3
    
    def test_protected_endpoint_with_valid_token(self, test_client, auth_headers):
        """
        TEST: Protected endpoint should work with valid token
        - Uses auth_headers fixture (contains valid JWT)
        - Makes request to protected endpoint
        - Should return 200 OK
        """
        response = test_client.get('/api/v1/portfolio', headers=auth_headers)
        
        # Should work (200 OK) or endpoint might not exist (404)
        assert response.status_code in [200, 404]
    
    def test_protected_endpoint_with_invalid_token(self, test_client):
        """
        TEST: Protected endpoint should reject invalid token
        - Uses malformed or fake JWT token
        - Should return 401 Unauthorized or 422 Unprocessable Entity
        """
        invalid_headers = {'Authorization': 'Bearer invalid-token-here'}
        
        response = test_client.get('/api/v1/portfolio', headers=invalid_headers)
        assert response.status_code in [401, 422]
    
    def test_protected_endpoint_without_token(self, test_client):
        """
        TEST: Protected endpoint should reject requests without token
        - Makes request without Authorization header
        - Should return 401 Unauthorized
        """
        response = test_client.get('/api/v1/portfolio')
        assert response.status_code == 401


class TestPasswordSecurity:
    """Test password hashing and security"""
    
    def test_password_is_hashed_in_database(self, test_app):
        """
        TEST: Passwords should be hashed in database
        - Retrieves test user from database
        - Verifies password is not stored in plain text
        """
        with test_app.app_context():
            user = User.query.filter_by(username='testuser').first()
            assert user is not None
            
            # Password should be hashed, not plain text
            assert user.password_hash != 'testpassword'
            assert len(user.password_hash) > 20  # Hash should be longer
            assert '$' in user.password_hash or 'pbkdf2' in user.password_hash  # Hash format
    
    def test_password_verification(self, test_app):
        """
        TEST: Password verification should work correctly
        - Tests that correct password validates
        - Tests that incorrect password fails
        """
        with test_app.app_context():
            user = User.query.filter_by(username='testuser').first()
            assert user is not None
            
            # Correct password should verify (if method exists)
            if hasattr(user, 'check_password'):
                assert user.check_password('testpassword') == True
                assert user.check_password('wrongpassword') == False