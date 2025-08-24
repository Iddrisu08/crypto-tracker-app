"""
ADVANCED LOGGING CONFIGURATION
Structured logging setup for crypto tracker backend with:
- JSON formatting for machine-readable logs
- Correlation IDs for request tracing
- Performance metrics logging
- Error tracking integration
- Environment-aware log levels
"""

import logging
import logging.config
import json
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
import sys
import os
from contextlib import contextmanager
from flask import request, g, has_request_context
import traceback


class CorrelationIdFilter(logging.Filter):
    """
    CORRELATION ID FILTER
    Adds correlation ID to log records for request tracing.
    Allows tracking a single request across multiple services.
    """
    
    def filter(self, record):
        # Add correlation ID from Flask context or generate new one
        if has_request_context() and hasattr(g, 'correlation_id'):
            record.correlation_id = g.correlation_id
        else:
            record.correlation_id = getattr(record, 'correlation_id', str(uuid.uuid4())[:8])
        
        # Add request information if available
        if has_request_context():
            record.request_method = request.method
            record.request_path = request.path
            record.request_remote_addr = request.remote_addr
            record.request_user_agent = request.headers.get('User-Agent', 'unknown')[:100]
        else:
            record.request_method = 'N/A'
            record.request_path = 'N/A'
            record.request_remote_addr = 'N/A'
            record.request_user_agent = 'N/A'
        
        return True


class JSONFormatter(logging.Formatter):
    """
    JSON FORMATTER
    Formats log records as JSON for structured logging.
    Includes metadata for monitoring and analysis.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hostname = os.uname().nodename
        self.service_name = "crypto-tracker-backend"
        self.service_version = os.getenv('SERVICE_VERSION', '1.0.0')
        self.environment = os.getenv('TARGET_ENV', 'production')
    
    def format(self, record):
        # Create base log entry
        log_entry = {
            # Timestamp and basic info
            '@timestamp': datetime.utcfromtimestamp(record.created).isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            
            # Service information
            'service': {
                'name': self.service_name,
                'version': self.service_version,
                'environment': self.environment,
                'hostname': self.hostname
            },
            
            # Request context
            'request': {
                'correlation_id': getattr(record, 'correlation_id', 'unknown'),
                'method': getattr(record, 'request_method', 'N/A'),
                'path': getattr(record, 'request_path', 'N/A'),
                'remote_addr': getattr(record, 'request_remote_addr', 'N/A'),
                'user_agent': getattr(record, 'request_user_agent', 'N/A')
            },
            
            # Code location
            'location': {
                'file': record.pathname,
                'line': record.lineno,
                'function': record.funcName,
                'module': record.module
            }
        }
        
        # Add exception information if present
        if record.exc_info:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
        
        # Add custom fields from extra parameters
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'lineno', 'funcName', 'created', 
                          'msecs', 'relativeCreated', 'thread', 'threadName', 
                          'processName', 'process', 'getMessage', 'exc_info', 
                          'exc_text', 'stack_info', 'correlation_id', 'request_method',
                          'request_path', 'request_remote_addr', 'request_user_agent']:
                if not key.startswith('_'):
                    log_entry['custom'] = log_entry.get('custom', {})
                    log_entry['custom'][key] = value
        
        return json.dumps(log_entry, default=str, ensure_ascii=False)


class PerformanceLogger:
    """
    PERFORMANCE LOGGER
    Tracks and logs performance metrics for endpoints and functions.
    Provides detailed timing and resource usage information.
    """
    
    def __init__(self, logger_name: str = 'performance'):
        self.logger = logging.getLogger(logger_name)
    
    @contextmanager
    def log_performance(self, operation: str, **metadata):
        """
        Context manager for logging operation performance.
        
        Usage:
            with perf_logger.log_performance('database_query', table='users'):
                # Your operation here
                result = db.query()
        """
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        try:
            yield
            status = 'success'
        except Exception as e:
            status = 'error'
            self.logger.error(
                f"Performance tracking failed for {operation}",
                extra={
                    'operation': operation,
                    'status': status,
                    'error': str(e),
                    **metadata
                }
            )
            raise
        finally:
            duration = time.time() - start_time
            end_memory = self._get_memory_usage()
            memory_delta = end_memory - start_memory
            
            # Log performance metrics
            self.logger.info(
                f"Performance: {operation}",
                extra={
                    'operation': operation,
                    'status': status,
                    'duration_ms': round(duration * 1000, 2),
                    'duration_seconds': round(duration, 4),
                    'memory_start_mb': round(start_memory / 1024 / 1024, 2),
                    'memory_end_mb': round(end_memory / 1024 / 1024, 2),
                    'memory_delta_mb': round(memory_delta / 1024 / 1024, 2),
                    **metadata
                }
            )
    
    def _get_memory_usage(self) -> int:
        """Get current memory usage in bytes."""
        try:
            import psutil
            return psutil.Process().memory_info().rss
        except ImportError:
            return 0


class BusinessMetricsLogger:
    """
    BUSINESS METRICS LOGGER
    Logs business-relevant metrics for analytics and monitoring.
    Tracks user behavior, portfolio changes, and feature usage.
    """
    
    def __init__(self, logger_name: str = 'business_metrics'):
        self.logger = logging.getLogger(logger_name)
    
    def log_user_action(self, user_id: str, action: str, **metadata):
        """Log user actions for analytics."""
        self.logger.info(
            f"User action: {action}",
            extra={
                'metric_type': 'user_action',
                'user_id': user_id,
                'action': action,
                'timestamp': datetime.utcnow().isoformat(),
                **metadata
            }
        )
    
    def log_portfolio_change(self, user_id: str, portfolio_value: float, 
                           change_amount: float, **metadata):
        """Log portfolio value changes."""
        self.logger.info(
            "Portfolio value changed",
            extra={
                'metric_type': 'portfolio_change',
                'user_id': user_id,
                'portfolio_value': portfolio_value,
                'change_amount': change_amount,
                'change_percentage': metadata.get('change_percentage', 0),
                'timestamp': datetime.utcnow().isoformat(),
                **metadata
            }
        )
    
    def log_api_usage(self, endpoint: str, response_time: float, status_code: int, **metadata):
        """Log API endpoint usage statistics."""
        self.logger.info(
            f"API usage: {endpoint}",
            extra={
                'metric_type': 'api_usage',
                'endpoint': endpoint,
                'response_time_ms': round(response_time * 1000, 2),
                'status_code': status_code,
                'timestamp': datetime.utcnow().isoformat(),
                **metadata
            }
        )


class LoggingManager:
    """
    LOGGING MANAGER
    Central logging configuration and management.
    Provides easy setup and configuration for different environments.
    """
    
    def __init__(self, app=None):
        self.app = app
        self.performance_logger = PerformanceLogger()
        self.business_metrics = BusinessMetricsLogger()
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize logging for Flask application."""
        self.app = app
        
        # Get configuration from environment
        log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        log_format = os.getenv('LOG_FORMAT', 'json')  # 'json' or 'text'
        enable_file_logging = os.getenv('LOG_TO_FILE', 'false').lower() == 'true'
        log_file_path = os.getenv('LOG_FILE_PATH', '/app/logs/app.log')
        
        # Create logging configuration
        logging_config = self._create_logging_config(
            log_level, log_format, enable_file_logging, log_file_path
        )
        
        # Apply configuration
        logging.config.dictConfig(logging_config)
        
        # Setup Flask request logging
        self._setup_request_logging(app)
        
        # Log startup message
        logger = logging.getLogger(__name__)
        logger.info(
            "Logging system initialized",
            extra={
                'log_level': log_level,
                'log_format': log_format,
                'file_logging': enable_file_logging,
                'environment': os.getenv('TARGET_ENV', 'production')
            }
        )
    
    def _create_logging_config(self, log_level: str, log_format: str, 
                             enable_file_logging: bool, log_file_path: str) -> Dict[str, Any]:
        """Create logging configuration dictionary."""
        
        # Choose formatter based on format preference
        if log_format == 'json':
            formatter_class = 'logger_config.JSONFormatter'
            formatter_format = None
        else:
            formatter_class = 'logging.Formatter'
            formatter_format = '%(asctime)s - %(name)s - %(levelname)s - [%(correlation_id)s] - %(message)s'
        
        config = {
            'version': 1,
            'disable_existing_loggers': False,
            
            'formatters': {
                'default': {
                    '()': formatter_class,
                    'format': formatter_format
                }
            },
            
            'filters': {
                'correlation_id': {
                    '()': 'logger_config.CorrelationIdFilter'
                }
            },
            
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'stream': 'ext://sys.stdout',
                    'formatter': 'default',
                    'filters': ['correlation_id']
                }
            },
            
            'loggers': {
                # Root logger
                '': {
                    'level': log_level,
                    'handlers': ['console'],
                    'propagate': False
                },
                
                # Application loggers
                'crypto_tracker': {
                    'level': log_level,
                    'handlers': ['console'],
                    'propagate': False
                },
                
                # Performance logger
                'performance': {
                    'level': 'INFO',
                    'handlers': ['console'],
                    'propagate': False
                },
                
                # Business metrics logger
                'business_metrics': {
                    'level': 'INFO',
                    'handlers': ['console'],
                    'propagate': False
                },
                
                # Third-party loggers (reduce verbosity)
                'urllib3': {
                    'level': 'WARNING',
                    'handlers': ['console'],
                    'propagate': False
                },
                
                'requests': {
                    'level': 'WARNING',
                    'handlers': ['console'],
                    'propagate': False
                },
                
                'werkzeug': {
                    'level': 'WARNING',
                    'handlers': ['console'],
                    'propagate': False
                }
            }
        }
        
        # Add file handler if enabled
        if enable_file_logging:
            # Ensure log directory exists
            os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
            
            config['handlers']['file'] = {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': log_file_path,
                'maxBytes': 50 * 1024 * 1024,  # 50MB
                'backupCount': 5,
                'formatter': 'default',
                'filters': ['correlation_id']
            }
            
            # Add file handler to all loggers
            for logger_config in config['loggers'].values():
                if 'file' not in logger_config['handlers']:
                    logger_config['handlers'].append('file')
        
        return config
    
    def _setup_request_logging(self, app):
        """Setup Flask request/response logging."""
        
        @app.before_request
        def before_request():
            # Generate correlation ID for request
            g.correlation_id = request.headers.get('X-Correlation-ID', str(uuid.uuid4())[:8])
            g.start_time = time.time()
            
            # Log incoming request
            logger = logging.getLogger('crypto_tracker.requests')
            logger.info(
                f"Incoming request: {request.method} {request.path}",
                extra={
                    'request_id': g.correlation_id,
                    'method': request.method,
                    'path': request.path,
                    'remote_addr': request.remote_addr,
                    'user_agent': request.headers.get('User-Agent', 'unknown')[:200],
                    'content_length': request.content_length or 0,
                    'args': dict(request.args) if request.args else {}
                }
            )
        
        @app.after_request
        def after_request(response):
            # Calculate request duration
            duration = time.time() - g.start_time
            
            # Log response
            logger = logging.getLogger('crypto_tracker.requests')
            logger.info(
                f"Request completed: {request.method} {request.path}",
                extra={
                    'request_id': g.correlation_id,
                    'method': request.method,
                    'path': request.path,
                    'status_code': response.status_code,
                    'duration_ms': round(duration * 1000, 2),
                    'content_length': response.content_length or 0,
                    'response_time_category': self._categorize_response_time(duration)
                }
            )
            
            # Add correlation ID to response headers
            response.headers['X-Correlation-ID'] = g.correlation_id
            
            return response
        
        @app.teardown_appcontext
        def teardown_request(exception=None):
            if exception:
                logger = logging.getLogger('crypto_tracker.errors')
                logger.error(
                    f"Request error: {str(exception)}",
                    extra={
                        'request_id': getattr(g, 'correlation_id', 'unknown'),
                        'method': request.method,
                        'path': request.path,
                        'exception_type': type(exception).__name__,
                        'exception_message': str(exception)
                    },
                    exc_info=True
                )
    
    def _categorize_response_time(self, duration: float) -> str:
        """Categorize response time for metrics."""
        if duration < 0.1:  # < 100ms
            return 'fast'
        elif duration < 0.5:  # < 500ms
            return 'normal'
        elif duration < 2.0:  # < 2s
            return 'slow'
        else:
            return 'very_slow'


# Global instances
logging_manager = LoggingManager()
performance_logger = PerformanceLogger()
business_metrics = BusinessMetricsLogger()

# Convenience functions
def get_logger(name: str) -> logging.Logger:
    """Get logger with correlation ID support."""
    return logging.getLogger(name)

def log_performance(operation: str, **metadata):
    """Decorator/context manager for performance logging."""
    return performance_logger.log_performance(operation, **metadata)


# Example usage and testing
if __name__ == '__main__':
    # Test logging configuration
    from flask import Flask
    
    app = Flask(__name__)
    logging_manager.init_app(app)
    
    # Test different log levels
    logger = get_logger(__name__)
    
    logger.debug("Debug message")
    logger.info("Info message", extra={'custom_field': 'test_value'})
    logger.warning("Warning message")
    logger.error("Error message")
    
    # Test performance logging
    with log_performance('test_operation', operation_type='test'):
        time.sleep(0.1)  # Simulate work
    
    # Test business metrics
    business_metrics.log_user_action('user123', 'login', ip_address='127.0.0.1')
    business_metrics.log_portfolio_change('user123', 10000.0, 500.0, change_percentage=5.0)
    
    print("Logging test completed!")