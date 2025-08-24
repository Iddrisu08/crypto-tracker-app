"""
APPLICATION METRICS COLLECTION
Prometheus metrics integration for crypto tracker backend.
Tracks application performance, business metrics, and system health.
"""

from prometheus_client import (
    Counter, Histogram, Gauge, Info, Enum,
    generate_latest, CONTENT_TYPE_LATEST,
    CollectorRegistry, multiprocess, ProcessCollector
)
from flask import Blueprint, Response, request, g
import time
import psutil
import os
from functools import wraps
from typing import Dict, Any, Optional
import logging

# Create metrics blueprint
metrics_bp = Blueprint('metrics', __name__)

# -----------------------------------------------
# PROMETHEUS METRICS DEFINITIONS
# -----------------------------------------------

# Application info
app_info = Info('crypto_tracker_info', 'Application information')
app_info.info({
    'version': os.getenv('SERVICE_VERSION', '1.0.0'),
    'environment': os.getenv('TARGET_ENV', 'production'),
    'build_date': os.getenv('BUILD_DATE', 'unknown')
})

# HTTP Request metrics
http_requests_total = Counter(
    'flask_http_request_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'flask_http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint'],
    buckets=(.005, .01, .025, .05, .075, .1, .25, .5, .75, 1.0, 2.5, 5.0, 7.5, 10.0)
)

http_request_size_bytes = Histogram(
    'flask_http_request_size_bytes',
    'HTTP request size in bytes',
    ['method', 'endpoint'],
    buckets=(100, 1000, 10000, 100000, 1000000)
)

http_response_size_bytes = Histogram(
    'flask_http_response_size_bytes',
    'HTTP response size in bytes',
    ['method', 'endpoint'],
    buckets=(100, 1000, 10000, 100000, 1000000)
)

# Database metrics
database_connections_active = Gauge(
    'postgresql_connections_active',
    'Active database connections'
)

database_query_duration_seconds = Histogram(
    'postgresql_query_duration_seconds',
    'Database query execution time',
    ['query_type'],
    buckets=(.001, .005, .01, .025, .05, .1, .25, .5, 1.0, 2.5, 5.0)
)

database_queries_total = Counter(
    'postgresql_queries_total',
    'Total database queries',
    ['query_type', 'status']
)

# Cache metrics
cache_operations_total = Counter(
    'redis_cache_operations_total',
    'Total cache operations',
    ['operation', 'status']
)

cache_hit_ratio = Gauge(
    'redis_cache_hit_ratio',
    'Cache hit ratio'
)

# Business metrics
user_actions_total = Counter(
    'user_actions_total',
    'Total user actions',
    ['user_id', 'action_type']
)

portfolio_calculations_total = Counter(
    'portfolio_calculations_total',
    'Total portfolio calculations',
    ['calculation_type', 'status']
)

portfolio_value_current = Gauge(
    'portfolio_value_current_usd',
    'Current portfolio value in USD',
    ['user_id']
)

crypto_prices_updated_total = Counter(
    'crypto_prices_updated_total',
    'Total crypto price updates',
    ['symbol', 'source']
)

crypto_price_last_updated_timestamp = Gauge(
    'crypto_price_last_updated_timestamp',
    'Timestamp of last price update',
    ['symbol']
)

# External API metrics
external_api_requests_total = Counter(
    'external_api_requests_total',
    'Total external API requests',
    ['api', 'endpoint', 'status']
)

external_api_request_duration_seconds = Histogram(
    'external_api_request_duration_seconds',
    'External API request duration',
    ['api', 'endpoint'],
    buckets=(.1, .25, .5, 1.0, 2.5, 5.0, 10.0, 30.0)
)

# Authentication metrics
auth_attempts_total = Counter(
    'auth_attempts_total',
    'Total authentication attempts',
    ['method', 'status']
)

auth_failures_total = Counter(
    'auth_failures_total',
    'Total authentication failures',
    ['failure_reason']
)

active_users_gauge = Gauge(
    'active_users_current',
    'Currently active users'
)

# System metrics
system_cpu_usage_percent = Gauge(
    'system_cpu_usage_percent',
    'System CPU usage percentage'
)

system_memory_usage_bytes = Gauge(
    'system_memory_usage_bytes',
    'System memory usage in bytes'
)

system_disk_usage_bytes = Gauge(
    'system_disk_usage_bytes',
    'System disk usage in bytes',
    ['device']
)

# Application health
application_health_status = Enum(
    'application_health_status',
    'Application health status',
    states=['healthy', 'degraded', 'unhealthy']
)

application_uptime_seconds = Gauge(
    'application_uptime_seconds',
    'Application uptime in seconds'
)

# -----------------------------------------------
# METRICS COLLECTION CLASSES
# -----------------------------------------------

class MetricsCollector:
    """
    METRICS COLLECTOR
    Central class for collecting and updating application metrics.
    """
    
    def __init__(self):
        self.start_time = time.time()
        self.logger = logging.getLogger(__name__)
        
        # Initialize system metrics collection
        self._update_system_metrics()
    
    def track_request(self, method: str, endpoint: str, status_code: int, 
                     duration: float, request_size: int = 0, response_size: int = 0):
        """Track HTTP request metrics."""
        http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status=str(status_code)
        ).inc()
        
        http_request_duration_seconds.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
        
        if request_size > 0:
            http_request_size_bytes.labels(
                method=method,
                endpoint=endpoint
            ).observe(request_size)
        
        if response_size > 0:
            http_response_size_bytes.labels(
                method=method,
                endpoint=endpoint
            ).observe(response_size)
    
    def track_database_query(self, query_type: str, duration: float, success: bool = True):
        """Track database query metrics."""
        status = 'success' if success else 'error'
        
        database_queries_total.labels(
            query_type=query_type,
            status=status
        ).inc()
        
        database_query_duration_seconds.labels(
            query_type=query_type
        ).observe(duration)
    
    def track_cache_operation(self, operation: str, success: bool = True):
        """Track cache operation metrics."""
        status = 'hit' if success and operation == 'get' else ('success' if success else 'error')
        
        cache_operations_total.labels(
            operation=operation,
            status=status
        ).inc()
    
    def update_cache_hit_ratio(self, ratio: float):
        """Update cache hit ratio."""
        cache_hit_ratio.set(ratio)
    
    def track_user_action(self, user_id: str, action_type: str):
        """Track user actions for business metrics."""
        user_actions_total.labels(
            user_id=user_id,
            action_type=action_type
        ).inc()
    
    def track_portfolio_calculation(self, calculation_type: str, success: bool = True):
        """Track portfolio calculations."""
        status = 'success' if success else 'error'
        
        portfolio_calculations_total.labels(
            calculation_type=calculation_type,
            status=status
        ).inc()
    
    def update_portfolio_value(self, user_id: str, value: float):
        """Update portfolio value for user."""
        portfolio_value_current.labels(user_id=user_id).set(value)
    
    def track_price_update(self, symbol: str, source: str = 'coingecko'):
        """Track cryptocurrency price updates."""
        crypto_prices_updated_total.labels(
            symbol=symbol,
            source=source
        ).inc()
        
        crypto_price_last_updated_timestamp.labels(
            symbol=symbol
        ).set(time.time())
    
    def track_external_api_request(self, api: str, endpoint: str, 
                                 duration: float, status_code: int):
        """Track external API requests."""
        external_api_requests_total.labels(
            api=api,
            endpoint=endpoint,
            status=str(status_code)
        ).inc()
        
        external_api_request_duration_seconds.labels(
            api=api,
            endpoint=endpoint
        ).observe(duration)
    
    def track_auth_attempt(self, method: str, success: bool = True, failure_reason: str = None):
        """Track authentication attempts."""
        status = 'success' if success else 'failure'
        
        auth_attempts_total.labels(
            method=method,
            status=status
        ).inc()
        
        if not success and failure_reason:
            auth_failures_total.labels(
                failure_reason=failure_reason
            ).inc()
    
    def update_active_users(self, count: int):
        """Update active users count."""
        active_users_gauge.set(count)
    
    def update_health_status(self, status: str):
        """Update application health status."""
        application_health_status.state(status)
    
    def _update_system_metrics(self):
        """Update system-level metrics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            system_cpu_usage_percent.set(cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            system_memory_usage_bytes.set(memory.used)
            
            # Disk usage
            disk_usage = psutil.disk_usage('/')
            system_disk_usage_bytes.labels(device='/').set(disk_usage.used)
            
            # Application uptime
            uptime = time.time() - self.start_time
            application_uptime_seconds.set(uptime)
            
        except Exception as e:
            self.logger.error(f"Error updating system metrics: {e}")


# Global metrics collector instance
metrics_collector = MetricsCollector()

# -----------------------------------------------
# FLASK INTEGRATION
# -----------------------------------------------

def init_metrics(app):
    """Initialize metrics collection for Flask app."""
    
    # Register metrics blueprint
    app.register_blueprint(metrics_bp, url_prefix='/metrics')
    
    # Setup request tracking
    @app.before_request
    def before_request():
        g.start_time = time.time()
        g.request_size = request.content_length or 0
    
    @app.after_request
    def after_request(response):
        # Calculate request duration
        duration = time.time() - g.start_time
        
        # Get response size
        response_size = response.content_length or len(response.get_data())
        
        # Track request metrics
        metrics_collector.track_request(
            method=request.method,
            endpoint=request.endpoint or 'unknown',
            status_code=response.status_code,
            duration=duration,
            request_size=g.request_size,
            response_size=response_size
        )
        
        return response
    
    # Periodic system metrics update
    import threading
    import time
    
    def update_system_metrics_periodically():
        """Update system metrics every 30 seconds."""
        while True:
            time.sleep(30)
            metrics_collector._update_system_metrics()
    
    # Start system metrics thread
    metrics_thread = threading.Thread(target=update_system_metrics_periodically, daemon=True)
    metrics_thread.start()
    
    app.logger.info("Metrics collection initialized")


def track_performance(operation_name: str):
    """Decorator to track function performance."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                success = True
                return result
            except Exception as e:
                success = False
                raise
            finally:
                duration = time.time() - start_time
                
                # Track as database query if it looks like one
                if 'query' in operation_name.lower() or 'db' in operation_name.lower():
                    metrics_collector.track_database_query(operation_name, duration, success)
                elif 'portfolio' in operation_name.lower():
                    metrics_collector.track_portfolio_calculation(operation_name, success)
        
        return wrapper
    return decorator


# -----------------------------------------------
# METRICS ENDPOINTS
# -----------------------------------------------

@metrics_bp.route('/')
def metrics():
    """Prometheus metrics endpoint."""
    # Update health status
    metrics_collector.update_health_status('healthy')
    
    # Generate metrics in Prometheus format
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


@metrics_bp.route('/health')
def health_check():
    """Health check endpoint with metrics."""
    try:
        # Basic health checks
        health_status = {
            'status': 'healthy',
            'timestamp': time.time(),
            'uptime': time.time() - metrics_collector.start_time,
            'version': os.getenv('SERVICE_VERSION', '1.0.0')
        }
        
        # Update health metrics
        metrics_collector.update_health_status('healthy')
        
        return health_status
    
    except Exception as e:
        metrics_collector.update_health_status('unhealthy')
        return {'status': 'unhealthy', 'error': str(e)}, 500


# -----------------------------------------------
# CONVENIENCE FUNCTIONS
# -----------------------------------------------

def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance."""
    return metrics_collector