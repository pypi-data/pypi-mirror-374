"""
ohtell - OpenTelemetry Function Wrapper

A simple, decorator-based OpenTelemetry wrapper for tracing Python functions.
"""

__version__ = "0.2.20"

try:
    # When installed as a package
    from .tracer import task, traced_task, add_event, get_otel_context, set_trace_id
    from .providers import setup_logging, force_flush, trigger_export, shutdown, get_tracer, get_meter
    from .metrics import metric
    from .config import setup_otel_from_config, init
    from .config import *
except ImportError:
    # When running directly
    from tracer import task, traced_task, add_event, get_otel_context, set_trace_id
    from providers import setup_logging, force_flush, trigger_export, shutdown, get_tracer, get_meter
    from metrics import metric
    from config import setup_otel_from_config, init
    from config import *

import os
import requests
import logging
from urllib.parse import urljoin

# Configure logging for ohtell
logger = logging.getLogger(__name__)

def _test_otlp_connection():
    """Test OTLP endpoint connection and authentication."""
    from .config import OTEL_ENDPOINT, OTEL_HEADERS_STR, OTEL_PROTOCOL, RESOURCE_ATTRIBUTES_STR, OTEL_HEADERS
    
    logger.info("OTEL Configuration:")
    logger.info(f"  OTEL_EXPORTER_OTLP_ENDPOINT: {OTEL_ENDPOINT or 'Not set'}")
    logger.info(f"  OTEL_EXPORTER_OTLP_PROTOCOL: {OTEL_PROTOCOL}")
    logger.info(f"  OTEL_EXPORTER_OTLP_HEADERS: {'<set>' if OTEL_HEADERS_STR else 'Not set'}")
    logger.info(f"  OTEL_RESOURCE_ATTRIBUTES: {RESOURCE_ATTRIBUTES_STR or 'Not set'}")
    
    endpoint = OTEL_ENDPOINT
    headers = OTEL_HEADERS
    
    if not endpoint:
        logger.warning("No OTLP endpoint configured")
        return
    
    # Log restart information instead of creating a test span
    try:
        from .config import SERVICE_NAME
        
        logger.info(f"Service restarted: {SERVICE_NAME}")
        
        # Try to flush any existing telemetry data
        try:
            from .providers import force_flush
            force_flush()
        except Exception:
            pass  # Ignore flush errors during startup
            
    except Exception as e:
        logger.error(f"Service restart logging failed: {str(e)}")

# Test OTLP configuration on import
_test_otlp_connection()

__all__ = [
    'task', 
    'traced_task', 
    'add_event', 
    'get_otel_context',
    'set_trace_id', 
    'setup_logging', 
    'force_flush', 
    'trigger_export', 
    'shutdown', 
    'get_tracer', 
    'get_meter',
    'metric', 
    'setup_otel_from_config', 
    'init'
]