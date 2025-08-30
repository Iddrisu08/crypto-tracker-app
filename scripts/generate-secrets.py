#!/usr/bin/env python3
"""
🔐 Generate Secure Keys for Crypto Tracker Deployment
This script generates secure random keys for your Flask application.
"""

import secrets
import string

def generate_secure_key(length=32):
    """Generate a secure random key using URL-safe characters."""
    return secrets.token_urlsafe(length)

def generate_complex_key(length=32):
    """Generate a complex key with letters, digits, and special characters."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()_+-="
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def main():
    print("🔐 Crypto Tracker - Secure Key Generator")
    print("=" * 50)
    print()
    
    # Generate Flask secret key
    flask_secret = generate_secure_key(32)
    print("🔑 Flask Secret Key:")
    print(f"SECRET_KEY={flask_secret}")
    print()
    
    # Generate JWT secret key  
    jwt_secret = generate_secure_key(32)
    print("🎫 JWT Secret Key:")
    print(f"JWT_SECRET_KEY={jwt_secret}")
    print()
    
    # Generate alternative complex keys
    print("🔒 Alternative Complex Keys (if needed):")
    complex_secret = generate_complex_key(32)
    complex_jwt = generate_complex_key(32)
    print(f"SECRET_KEY={complex_secret}")
    print(f"JWT_SECRET_KEY={complex_jwt}")
    print()
    
    print("📋 Copy these values to your:")
    print("   • Render service environment variables")
    print("   • Local .env file (for development)")
    print()
    print("⚠️  SECURITY NOTES:")
    print("   • Keep these keys secret and secure")
    print("   • Use different keys for development/production")
    print("   • Never commit keys to version control")
    print("   • Regenerate keys if compromised")
    print()
    print("✅ Keys generated successfully!")

if __name__ == "__main__":
    main()