"""
ENVIRONMENT CONFIGURATION LOADER
Dynamically loads configuration based on the current environment.
Handles development, staging, and production settings with proper validation.
"""

import os
import sys
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import logging


class EnvironmentConfig:
    """
    Environment configuration manager that loads settings based on environment.
    Provides validation, fallbacks, and environment-specific overrides.
    """
    
    def __init__(self, env_name: Optional[str] = None):
        """
        Initialize environment configuration.
        
        Args:
            env_name: Override environment name (development, staging, production)
        """
        self.env_name = env_name or self._detect_environment()
        self.config = {}
        self._load_environment_config()
        self._validate_config()
    
    def _detect_environment(self) -> str:
        """
        Detect current environment from various sources.
        Priority: ENV_NAME > FLASK_ENV > NODE_ENV > default to development
        """
        # Check environment variables in order of priority
        env_vars = ['ENV_NAME', 'FLASK_ENV', 'NODE_ENV']
        
        for env_var in env_vars:
            env_value = os.getenv(env_var, '').lower()
            if env_value in ['development', 'staging', 'production']:
                return env_value
        
        # Default to development if nothing specified
        return 'development'
    
    def _load_environment_config(self):
        """Load environment-specific configuration files."""
        # Load base .env file first (if exists)
        base_env_path = '.env'
        if os.path.exists(base_env_path):
            load_dotenv(base_env_path, override=False)
        
        # Load environment-specific .env file
        env_file_path = f'.env.{self.env_name}'
        if os.path.exists(env_file_path):
            load_dotenv(env_file_path, override=True)
            print(f"✅ Loaded environment config: {env_file_path}")
        else:
            print(f"⚠️  Environment file not found: {env_file_path}")
        
        # Load configuration into dictionary
        self._populate_config()
    
    def _populate_config(self):
        """Populate configuration dictionary from environment variables."""
        self.config = {
            # Environment identification
            'ENV_NAME': self.env_name,
            'IS_DEVELOPMENT': self.env_name == 'development',
            'IS_STAGING': self.env_name == 'staging',
            'IS_PRODUCTION': self.env_name == 'production',
            
            # Flask configuration
            'FLASK_ENV': os.getenv('FLASK_ENV', self.env_name),
            'FLASK_DEBUG': self._get_boolean('FLASK_DEBUG', False),
            'SECRET_KEY': os.getenv('SECRET_KEY'),
            
            # Database configuration
            'DATABASE_URL': os.getenv('DATABASE_URL'),
            'DATABASE_ECHO': self._get_boolean('DATABASE_ECHO', False),
            'DATABASE_POOL_SIZE': self._get_integer('DATABASE_POOL_SIZE', 5),
            'DATABASE_MAX_OVERFLOW': self._get_integer('DATABASE_MAX_OVERFLOW', 10),
            
            # Redis configuration
            'REDIS_URL': os.getenv('REDIS_URL'),
            'CACHE_TIMEOUT': self._get_integer('CACHE_TIMEOUT', 300),
            
            # JWT configuration
            'JWT_SECRET_KEY': os.getenv('JWT_SECRET_KEY'),
            'JWT_ACCESS_TOKEN_EXPIRES': self._get_integer('JWT_ACCESS_TOKEN_EXPIRES', 3600),
            
            # API configuration
            'RATE_LIMIT_PER_MINUTE': self._get_integer('RATE_LIMIT_PER_MINUTE', 60),
            'API_VERSION': os.getenv('API_VERSION', 'v1'),
            
            # CORS configuration
            'FRONTEND_URL': os.getenv('FRONTEND_URL'),
            'CORS_ORIGINS': self._get_list('CORS_ORIGINS'),
            
            # External APIs
            'COINGECKO_API_URL': os.getenv('COINGECKO_API_URL', 'https://api.coingecko.com/api/v3'),
            'COINGECKO_API_KEY': os.getenv('COINGECKO_API_KEY'),
            
            # Logging configuration
            'LOG_LEVEL': os.getenv('LOG_LEVEL', 'INFO').upper(),
            'LOG_TO_FILE': self._get_boolean('LOG_TO_FILE', False),
            'LOG_FILE_PATH': os.getenv('LOG_FILE_PATH', './logs/app.log'),
            
            # Feature flags
            'ENABLE_DEBUG_ENDPOINTS': self._get_boolean('ENABLE_DEBUG_ENDPOINTS', False),
            'ENABLE_MOCK_DATA': self._get_boolean('ENABLE_MOCK_DATA', False),
            'SKIP_EMAIL_VERIFICATION': self._get_boolean('SKIP_EMAIL_VERIFICATION', False),
            
            # Monitoring
            'ENABLE_METRICS': self._get_boolean('ENABLE_METRICS', False),
            'ENABLE_TRACING': self._get_boolean('ENABLE_TRACING', False),
            'SENTRY_DSN': os.getenv('SENTRY_DSN'),
            
            # Performance settings
            'WORKER_PROCESSES': self._get_integer('WORKER_PROCESSES', 1),
            'WORKER_TIMEOUT': self._get_integer('WORKER_TIMEOUT', 30),
            
            # Security settings
            'USE_HTTPS': self._get_boolean('USE_HTTPS', False),
            'BYPASS_RATE_LIMITS': self._get_boolean('BYPASS_RATE_LIMITS', False),
            
            # Server configuration
            'HOST': os.getenv('HOST', '0.0.0.0'),
            'PORT': self._get_integer('PORT', 5001),
        }
    
    def _get_boolean(self, key: str, default: bool = False) -> bool:
        """Convert environment variable to boolean."""
        value = os.getenv(key, '').lower()
        if value in ['true', '1', 'yes', 'on']:
            return True
        elif value in ['false', '0', 'no', 'off']:
            return False
        return default
    
    def _get_integer(self, key: str, default: int = 0) -> int:
        """Convert environment variable to integer."""
        try:
            return int(os.getenv(key, default))
        except (ValueError, TypeError):
            return default
    
    def _get_list(self, key: str, separator: str = ',') -> list:
        """Convert environment variable to list."""
        value = os.getenv(key, '')
        if not value:
            return []
        return [item.strip() for item in value.split(separator) if item.strip()]
    
    def _validate_config(self):
        """Validate configuration based on environment."""
        errors = []
        
        # Common required settings
        required_keys = ['SECRET_KEY', 'JWT_SECRET_KEY']
        
        # Environment-specific requirements
        if self.env_name in ['staging', 'production']:
            required_keys.extend(['DATABASE_URL', 'REDIS_URL'])
        
        # Check required keys
        for key in required_keys:
            if not self.config.get(key):
                errors.append(f"Missing required configuration: {key}")
        
        # Production-specific validations
        if self.env_name == 'production':
            self._validate_production_config(errors)
        
        # Development-specific warnings
        if self.env_name == 'development':
            self._validate_development_config()
        
        if errors:
            print("❌ Configuration validation errors:")
            for error in errors:
                print(f"   • {error}")
            sys.exit(1)
        
        print(f"✅ Configuration validation passed for {self.env_name} environment")
    
    def _validate_production_config(self, errors: list):
        """Validate production-specific configuration."""
        # Skip secret validation in CI/CD environments where secrets are managed externally
        if os.getenv('CI') or os.getenv('GITHUB_ACTIONS'):
            print("🔧 Skipping secret validation in CI/CD environment")
            return
            
        # Check for development secrets in production
        secret_key = self.config.get('SECRET_KEY', '')
        if secret_key.startswith('dev-') or secret_key.startswith('${'):
            errors.append("Development secret key used in production")
        
        jwt_secret = self.config.get('JWT_SECRET_KEY', '')
        if jwt_secret.startswith('dev-') or jwt_secret.startswith('${'):
            errors.append("Development JWT secret used in production")
        
        # Check debug settings
        if self.config.get('FLASK_DEBUG'):
            errors.append("Debug mode enabled in production")
        
        if self.config.get('DATABASE_ECHO'):
            errors.append("Database query logging enabled in production")
        
        # Check security settings
        if not self.config.get('USE_HTTPS'):
            print("⚠️  HTTPS not enforced in production")
        
        # Check monitoring
        if not self.config.get('SENTRY_DSN'):
            print("⚠️  Error monitoring (Sentry) not configured")
    
    def _validate_development_config(self):
        """Validate development-specific configuration and show warnings."""
        if self.config.get('SECRET_KEY') and not self.config.get('SECRET_KEY').startswith('dev-'):
            print("⚠️  Using production-like secret in development")
        
        if not self.config.get('DATABASE_URL', '').startswith('sqlite'):
            print("ℹ️  Using external database in development")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)
    
    def get_flask_config(self) -> Dict[str, Any]:
        """Get Flask-specific configuration dictionary."""
        flask_config = {
            'SECRET_KEY': self.get('SECRET_KEY'),
            'SQLALCHEMY_DATABASE_URI': self.get('DATABASE_URL'),
            'SQLALCHEMY_ECHO': self.get('DATABASE_ECHO'),
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'JWT_SECRET_KEY': self.get('JWT_SECRET_KEY'),
            'JWT_ACCESS_TOKEN_EXPIRES': self.get('JWT_ACCESS_TOKEN_EXPIRES'),
            'REDIS_URL': self.get('REDIS_URL'),
            'CACHE_DEFAULT_TIMEOUT': self.get('CACHE_TIMEOUT'),
            'TESTING': False,
            'DEBUG': self.get('FLASK_DEBUG'),
        }
        
        # Environment-specific Flask settings
        if self.env_name == 'production':
            flask_config.update({
                'SESSION_COOKIE_SECURE': True,
                'SESSION_COOKIE_HTTPONLY': True,
                'SESSION_COOKIE_SAMESITE': 'Lax',
            })
        
        return flask_config
    
    def setup_logging(self):
        """Configure logging based on environment settings."""
        log_level = getattr(logging, self.get('LOG_LEVEL', 'INFO'))
        
        # Configure logging format
        if self.env_name == 'production':
            # Structured logging for production
            log_format = '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "module": "%(name)s", "message": "%(message)s"}'
        else:
            # Human-readable format for development/staging
            log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        # Configure handlers
        handlers = [logging.StreamHandler(sys.stdout)]
        
        if self.get('LOG_TO_FILE'):
            log_file = self.get('LOG_FILE_PATH')
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            handlers.append(logging.FileHandler(log_file))
        
        # Apply logging configuration
        logging.basicConfig(
            level=log_level,
            format=log_format,
            handlers=handlers,
            force=True  # Override any existing configuration
        )
        
        # Set third-party library log levels
        if self.env_name == 'production':
            logging.getLogger('urllib3').setLevel(logging.WARNING)
            logging.getLogger('requests').setLevel(logging.WARNING)
    
    def print_summary(self):
        """Print configuration summary."""
        print(f"\n🔧 Environment Configuration Summary")
        print(f"{'='*50}")
        print(f"Environment: {self.env_name}")
        print(f"Flask Debug: {self.get('FLASK_DEBUG')}")
        print(f"Database: {self.get('DATABASE_URL', 'Not configured')}")
        print(f"Redis: {self.get('REDIS_URL', 'Not configured')}")
        print(f"Frontend URL: {self.get('FRONTEND_URL', 'Not configured')}")
        print(f"Log Level: {self.get('LOG_LEVEL')}")
        print(f"{'='*50}\n")


# Global configuration instance
config = EnvironmentConfig()

# Helper function to get configuration instance
def get_config() -> EnvironmentConfig:
    """Get the global configuration instance."""
    return config

# Helper function to reload configuration
def reload_config(env_name: Optional[str] = None) -> EnvironmentConfig:
    """Reload configuration with optional environment override."""
    global config
    config = EnvironmentConfig(env_name)
    return config


# CLI tool for configuration management
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Environment Configuration Tool')
    parser.add_argument('--env', choices=['development', 'staging', 'production'], 
                       help='Environment to load')
    parser.add_argument('--validate', action='store_true', 
                       help='Validate configuration only')
    parser.add_argument('--summary', action='store_true', 
                       help='Show configuration summary')
    
    args = parser.parse_args()
    
    # Create configuration instance
    if args.env:
        config = EnvironmentConfig(args.env)
    else:
        config = EnvironmentConfig()
    
    if args.validate:
        print("Configuration validation completed successfully!")
    
    if args.summary:
        config.print_summary()
    
    if not args.validate and not args.summary:
        config.print_summary()