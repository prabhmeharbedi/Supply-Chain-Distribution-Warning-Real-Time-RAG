"""
Monitoring and Metrics System for Supply Chain Disruption Predictor
"""

import time
import psutil
from typing import Dict, Any
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

# Prometheus Metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

PIPELINE_PROCESSING_TIME = Histogram(
    'pipeline_processing_duration_seconds',
    'Time spent processing pipeline data',
    ['source_type']
)

DISRUPTION_ALERTS = Counter(
    'disruption_alerts_total',
    'Total disruption alerts generated',
    ['severity', 'source']
)

ACTIVE_DISRUPTIONS = Gauge(
    'active_disruptions_count',
    'Number of currently active disruptions'
)

DATA_SOURCE_AVAILABILITY = Gauge(
    'data_source_availability',
    'Data source availability (1=up, 0=down)',
    ['source']
)

SYSTEM_CPU_USAGE = Gauge(
    'system_cpu_usage_percent',
    'System CPU usage percentage'
)

SYSTEM_MEMORY_USAGE = Gauge(
    'system_memory_usage_percent',
    'System memory usage percentage'
)

DATABASE_CONNECTIONS = Gauge(
    'database_connections_active',
    'Number of active database connections'
)

API_ERRORS = Counter(
    'api_errors_total',
    'Total API errors',
    ['error_type', 'endpoint']
)

class MetricsCollector:
    def __init__(self):
        self.start_time = time.time()
        
    def record_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Record HTTP request metrics"""
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
        REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
        
    def record_pipeline_processing(self, source_type: str, duration: float):
        """Record pipeline processing metrics"""
        PIPELINE_PROCESSING_TIME.labels(source_type=source_type).observe(duration)
        
    def record_disruption_alert(self, severity: str, source: str):
        """Record disruption alert metrics"""
        DISRUPTION_ALERTS.labels(severity=severity, source=source).inc()
        
    def update_active_disruptions(self, count: int):
        """Update active disruptions count"""
        ACTIVE_DISRUPTIONS.set(count)
        
    def update_data_source_status(self, source: str, is_available: bool):
        """Update data source availability"""
        DATA_SOURCE_AVAILABILITY.labels(source=source).set(1 if is_available else 0)
        
    def record_api_error(self, error_type: str, endpoint: str):
        """Record API error"""
        API_ERRORS.labels(error_type=error_type, endpoint=endpoint).inc()
        
    def update_system_metrics(self):
        """Update system resource metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            SYSTEM_CPU_USAGE.set(cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            SYSTEM_MEMORY_USAGE.set(memory.percent)
            
            logger.debug(f"System metrics updated - CPU: {cpu_percent}%, Memory: {memory.percent}%")
            
        except Exception as e:
            logger.error(f"Error updating system metrics: {e}")
    
    def get_application_metrics(self) -> Dict[str, Any]:
        """Get application-specific metrics"""
        uptime = time.time() - self.start_time
        
        return {
            "uptime_seconds": uptime,
            "uptime_formatted": self._format_uptime(uptime),
            "system_info": {
                "cpu_count": psutil.cpu_count(),
                "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
                "disk_usage_percent": psutil.disk_usage('/').percent
            }
        }
    
    def _format_uptime(self, seconds: float) -> str:
        """Format uptime in human-readable format"""
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"

# Global metrics collector instance
metrics_collector = MetricsCollector()

def get_prometheus_metrics() -> Response:
    """Get Prometheus metrics endpoint"""
    try:
        # Update system metrics before returning
        metrics_collector.update_system_metrics()
        
        # Generate Prometheus format
        metrics_data = generate_latest()
        
        return Response(
            content=metrics_data,
            media_type=CONTENT_TYPE_LATEST
        )
    except Exception as e:
        logger.error(f"Error generating Prometheus metrics: {e}")
        return Response(
            content="# Error generating metrics\n",
            media_type=CONTENT_TYPE_LATEST,
            status_code=500
        )

class PerformanceMonitor:
    """Context manager for monitoring performance"""
    
    def __init__(self, operation_name: str, source_type: str = None):
        self.operation_name = operation_name
        self.source_type = source_type
        self.start_time = None
        
    def __enter__(self):
        self.start_time = time.time()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.time() - self.start_time
            
            if self.source_type:
                metrics_collector.record_pipeline_processing(self.source_type, duration)
            
            logger.debug(f"{self.operation_name} completed in {duration:.3f}s")
            
            if exc_type:
                logger.error(f"Error in {self.operation_name}: {exc_val}")
                metrics_collector.record_api_error(str(exc_type.__name__), self.operation_name)

# Health check metrics
class HealthChecker:
    def __init__(self):
        self.checks = {}
        
    def register_check(self, name: str, check_func):
        """Register a health check function"""
        self.checks[name] = check_func
        
    def run_checks(self) -> Dict[str, Any]:
        """Run all health checks"""
        results = {}
        overall_healthy = True
        
        for name, check_func in self.checks.items():
            try:
                result = check_func()
                results[name] = {
                    "status": "healthy" if result else "unhealthy",
                    "details": result if isinstance(result, dict) else {}
                }
                if not result:
                    overall_healthy = False
            except Exception as e:
                results[name] = {
                    "status": "error",
                    "error": str(e)
                }
                overall_healthy = False
                
        results["overall"] = "healthy" if overall_healthy else "unhealthy"
        return results

# Global health checker
health_checker = HealthChecker() 