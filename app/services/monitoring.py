"""Application Insights Monitoring"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime

try:
    from opencensus.ext.azure.log_exporter import AzureLogHandler
    from opencensus.ext.azure import metrics_exporter
    from opencensus.stats import aggregation as aggregation_module
    from opencensus.stats import measure as measure_module
    from opencensus.stats import stats as stats_module
    from opencensus.stats import view as view_module
    from opencensus.tags import tag_map as tag_map_module
    OPENCENSUS_AVAILABLE = True
except ImportError:
    OPENCENSUS_AVAILABLE = False

from app.config import settings

logger = logging.getLogger(__name__)


class MonitoringService:
    """Application Insights monitoring wrapper"""
    
    def __init__(self):
        """Initialize Application Insights"""
        self.enabled = False
        
        if settings.APPINSIGHTS_INSTRUMENTATIONKEY and OPENCENSUS_AVAILABLE:
            try:
                # Configure Azure Log Handler
                azure_handler = AzureLogHandler(
                    connection_string=settings.APPINSIGHTS_CONNECTION_STRING or 
                                     f"InstrumentationKey={settings.APPINSIGHTS_INSTRUMENTATIONKEY}"
                )
                azure_handler.setLevel(logging.INFO)
                
                # Add handler to root logger
                logging.getLogger().addHandler(azure_handler)
                
                self.enabled = True
                logger.info("Application Insights configured successfully")
                
            except Exception as e:
                logger.error(f"Application Insights initialization error: {str(e)}")
        else:
            if not OPENCENSUS_AVAILABLE:
                logger.warning("opencensus-ext-azure not installed, monitoring disabled")
            else:
                logger.warning("Application Insights not configured")
    
    def track_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration: float,
        custom_properties: Optional[Dict[str, Any]] = None
    ):
        """
        Track HTTP request
        
        Args:
            method: HTTP method
            path: Request path
            status_code: Response status code
            duration: Request duration in seconds
            custom_properties: Additional properties to log
        """
        if not self.enabled:
            return
        
        try:
            properties = {
                'method': method,
                'path': path,
                'status_code': status_code,
                'duration_ms': duration * 1000,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            if custom_properties:
                properties.update(custom_properties)
            
            logger.info(f"REQUEST: {method} {path} {status_code}", extra={'custom_dimensions': properties})
            
        except Exception as e:
            logger.error(f"Request tracking error: {str(e)}")
    
    def track_event(self, event_name: str, properties: Optional[Dict[str, Any]] = None):
        """
        Track custom event
        
        Args:
            event_name: Name of the event
            properties: Event properties
        """
        if not self.enabled:
            return
        
        try:
            event_props = {
                'event': event_name,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            if properties:
                event_props.update(properties)
            
            logger.info(f"EVENT: {event_name}", extra={'custom_dimensions': event_props})
            
        except Exception as e:
            logger.error(f"Event tracking error: {str(e)}")
    
    def track_exception(self, exception: Exception, properties: Optional[Dict[str, Any]] = None):
        """
        Track exception
        
        Args:
            exception: Exception object
            properties: Additional properties
        """
        if not self.enabled:
            return
        
        try:
            exc_props = {
                'exception_type': type(exception).__name__,
                'exception_message': str(exception),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            if properties:
                exc_props.update(properties)
            
            logger.exception("EXCEPTION", extra={'custom_dimensions': exc_props})
            
        except Exception as e:
            logger.error(f"Exception tracking error: {str(e)}")
    
    def track_metric(self, name: str, value: float, properties: Optional[Dict[str, Any]] = None):
        """
        Track custom metric
        
        Args:
            name: Metric name
            value: Metric value
            properties: Additional properties
        """
        if not self.enabled:
            return
        
        try:
            metric_props = {
                'metric_name': name,
                'metric_value': value,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            if properties:
                metric_props.update(properties)
            
            logger.info(f"METRIC: {name}={value}", extra={'custom_dimensions': metric_props})
            
        except Exception as e:
            logger.error(f"Metric tracking error: {str(e)}")


# Singleton instance
monitoring_service = MonitoringService()


def log_request_to_insights(method: str, path: str, status_code: int, duration: float):
    """Helper function to log requests to Application Insights"""
    monitoring_service.track_request(method, path, status_code, duration)


def log_event_to_insights(event_name: str, properties: Optional[Dict[str, Any]] = None):
    """Helper function to log events to Application Insights"""
    monitoring_service.track_event(event_name, properties)
