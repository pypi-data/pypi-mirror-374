import functools
import json
import traceback
import logging
import time
from typing import Any, Optional, Dict, Callable
from datetime import datetime
import inspect

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode, SpanKind

try:
    # When installed as a package
    from .providers import get_tracer, setup_logging
except ImportError:
    # When running directly
    from providers import get_tracer, setup_logging


def safe_serialize(obj: Any) -> Any:
    """Safely serialize objects for span attributes."""
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj
    elif isinstance(obj, (list, tuple)):
        return [safe_serialize(item) for item in obj[:10]]  # Limit to 10 items
    elif isinstance(obj, dict):
        return {k: safe_serialize(v) for k, v in list(obj.items())[:10]}  # Limit to 10 items
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif hasattr(obj, '__dict__'):
        return f"<{obj.__class__.__name__} object>"
    else:
        return str(obj)[:100]  # Limit string representation


def add_event(event_name: str, attributes: Optional[Dict[str, Any]] = None) -> bool:
    """
    Add an event to the current active span if one exists.
    
    Args:
        event_name: Name of the event
        attributes: Optional attributes to include with the event
        
    Returns:
        True if event was added, False if no active span
    """
    current_span = trace.get_current_span()
    if current_span and current_span.is_recording():
        current_span.add_event(event_name, attributes or {})
        return True
    return False


def get_otel_context() -> Optional[Dict[str, Any]]:
    """
    Extract the current span context as a dictionary for distributed tracing.
    
    Returns:
        Dict with trace_id, span_id, trace_flags, and is_remote keys if there's an active span,
        None otherwise.
    """
    current_span = trace.get_current_span()
    if current_span and current_span.is_recording():
        span_context = current_span.get_span_context()
        return {
            'trace_id': format(span_context.trace_id, '032x'),
            'span_id': format(span_context.span_id, '016x'),
            'trace_flags': int(span_context.trace_flags),
            'is_remote': True
        }
    return None


def set_trace_id(trace_id: str) -> None:
    """
    Set a custom trace ID for the current context.
    
    Args:
        trace_id: 32-character hex string for the trace ID
    """
    if len(trace_id) != 32:
        raise ValueError("trace_id must be 32 hex characters")
    
    # Create a span context with the custom trace ID
    custom_span_context = trace.SpanContext(
        trace_id=int(trace_id, 16),
        span_id=int('fedcba9876543210', 16),
        is_remote=False,
        trace_flags=trace.TraceFlags(0x01)
    )
    
    # Set it as the current context
    from opentelemetry import context as otel_context
    ctx = trace.set_span_in_context(
        trace.NonRecordingSpan(custom_span_context),
        otel_context.get_current()
    )
    token = otel_context.attach(ctx)
    return token




def format_task_name(template: str, **kwargs) -> str:
    """Format task name with template variables like Prefect."""
    try:
        # Handle datetime formatting
        for key, value in kwargs.items():
            if isinstance(value, datetime) and ':' in template:
                # Extract format after colon
                pattern = f"{{{key}:([^}}]+)}}"
                import re
                match = re.search(pattern, template)
                if match:
                    date_format = match.group(1)
                    formatted_date = value.strftime(date_format.replace('%', ''))
                    template = template.replace(f"{{{key}:{match.group(1)}}}", formatted_date)
        
        # Regular string formatting for remaining variables
        return template.format(**kwargs)
    except Exception:
        return template


class task:
    """
    Decorator for tracing functions with OpenTelemetry.
    
    Similar to Prefect's @task decorator, supports:
    - Custom task names with template variables
    - Task descriptions
    - Automatic span creation and nesting
    - Input/output capture
    - Print statement interception
    - Automatic logging to SigNoz
    - Span kind differentiation (root/child)
    - Comprehensive metrics collection
    """
    
    # Class-level logger setup
    _logger_initialized = False
    _task_logger = None
    
    @classmethod
    def _ensure_logger(cls):
        """Ensure the task logger is initialized."""
        if not cls._logger_initialized:
            cls._task_logger = setup_logging("ohtell.task")
            cls._logger_initialized = True
        return cls._task_logger
    
    def _filter_traceback(self, exception: Exception) -> str:
        """Filter traceback to remove ohtell internal frames and show only user code."""
        import traceback
        import sys
        
        # Get the current traceback
        exc_type, exc_value, exc_tb = sys.exc_info()
        
        # Filter out frames from ohtell package and OpenTelemetry
        filtered_frames = []
        tb = exc_tb
        
        while tb is not None:
            frame = tb.tb_frame
            filename = frame.f_code.co_filename
            
            # Skip frames that are from ohtell package or opentelemetry
            is_internal = (
                '/ohtell/' in filename or 
                'ohtell' in filename or
                'opentelemetry' in filename or
                filename.endswith('tracer.py')
            )
            
            if not is_internal:
                filtered_frames.append(tb)
            
            tb = tb.tb_next
        
        # If we have filtered frames, create a clean traceback
        if filtered_frames:
            # Create traceback string from filtered frames
            lines = ['Traceback (most recent call last):']
            
            for tb_frame in filtered_frames:
                frame = tb_frame.tb_frame
                filename = frame.f_code.co_filename
                lineno = tb_frame.tb_lineno
                name = frame.f_code.co_name
                
                lines.append(f'  File "{filename}", line {lineno}, in {name}')
                
                # Try to get the source line
                try:
                    import linecache
                    line = linecache.getline(filename, lineno).strip()
                    if line:
                        lines.append(f'    {line}')
                except:
                    pass
            
            # Add the exception
            lines.append(f'{exc_type.__name__}: {exc_value}')
            
            return '\n'.join(lines)
        else:
            # Fallback - just show the exception without traceback
            return f'{exc_type.__name__}: {exc_value}'
    
    def __init__(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        is_entrypoint: bool = False,
        trace_context_key: Optional[str] = None,
    ):
        self.name = name
        self.description = description
        self.is_entrypoint = is_entrypoint
        self.trace_context_key = trace_context_key or "trace_context"
        self.tracer = get_tracer()
        self.logger = self._ensure_logger()
    
    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Start timing
            start_time = time.time()
            
            # Determine span name
            span_name = self.name or func.__name__
            
            # Build context for name template if it contains variables
            if self.name and '{' in self.name:
                # Get parameter names
                sig = inspect.signature(func)
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()
                
                # Format the span name with parameters
                span_name = format_task_name(self.name, **bound_args.arguments)
            
            # Handle __otel_context magic parameter for automatic distributed tracing
            otel_context = kwargs.pop('__otel_context', None)
            parent_context = None
            
            if otel_context:
                self.logger.info(f"🔧 Processing __otel_context: {otel_context}")
                # Create parent span context from otel_context dict
                try:
                    parent_trace_id = int(otel_context['trace_id'], 16)
                    parent_span_id = int(otel_context['span_id'], 16)
                    
                    self.logger.info(f"🔧 Creating parent span context: trace_id={hex(parent_trace_id)}, span_id={hex(parent_span_id)}")
                    
                    parent_span_context = trace.SpanContext(
                        trace_id=parent_trace_id,
                        span_id=parent_span_id,
                        is_remote=True,
                        trace_flags=trace.TraceFlags(otel_context.get('trace_flags', 0x01))
                    )
                    
                    from opentelemetry import context as otel_context_module
                    parent_context = trace.set_span_in_context(
                        trace.NonRecordingSpan(parent_span_context),
                        otel_context_module.get_current()
                    )
                    
                    self.logger.info(f"✅ Successfully created parent context from __otel_context: {otel_context['trace_id']}")
                except Exception as e:
                    self.logger.warning(f"❌ Failed to process __otel_context: {e}")
                    otel_context = None
            else:
                self.logger.debug("No __otel_context parameter found")
            
            # Extract trace context if present in arguments (legacy support)
            trace_context_value = None
            if self.trace_context_key in kwargs:
                trace_context_value = kwargs[self.trace_context_key]
            else:
                # Look for trace_context in any of the arguments
                for arg in args:
                    if isinstance(arg, dict) and self.trace_context_key in arg:
                        trace_context_value = arg[self.trace_context_key]
                        break
                    # Also check for common trace ID patterns
                    if isinstance(arg, str) and (
                        arg.startswith('trace_') or 
                        len(arg) == 36 and arg.count('-') == 4  # UUID format
                    ):
                        trace_context_value = arg
                        break
            
            # Check if we have a current span (to determine if this is a root span)
            current_span = trace.get_current_span()
            is_root = current_span is None or not current_span.is_recording()
            
            # Determine span kind
            if self.is_entrypoint or is_root:
                span_kind = SpanKind.SERVER  # Entry point spans
            else:
                span_kind = SpanKind.INTERNAL  # Child spans
            
            
            # Get current trace ID for logging
            current_span = trace.get_current_span()
            current_trace_id = None
            if current_span and current_span.is_recording():
                current_trace_id = format(current_span.get_span_context().trace_id, '032x')
            
            # Log task start
            self.logger.debug(f"Task started: {span_name} (parent_trace: {current_trace_id}, is_root: {is_root})", extra={
                "task.name": span_name,
                "task.function": func.__name__,
                "task.module": func.__module__,
                "task.is_root": is_root,
                "task.is_entrypoint": self.is_entrypoint,
                "parent_trace_id": current_trace_id,
            })
            
            
            # Prepare span attributes
            span_attributes = {
                "task.is_root": is_root,
            }
            
            # Add otel context linking if available 
            if otel_context:
                span_attributes["parent.trace_id"] = otel_context['trace_id']
                span_attributes["parent.span_id"] = otel_context['span_id']
                span_attributes["trace.linked"] = True
                
            # Add trace context linking if available (legacy support)
            if trace_context_value:
                span_attributes["linked.trace_id"] = str(trace_context_value)
                span_attributes["trace.context"] = str(trace_context_value)
            
            # Start span with appropriate kind and parent context if available
            span_kwargs = {
                "name": span_name,
                "kind": span_kind,
                "attributes": span_attributes
            }
            if parent_context:
                span_kwargs["context"] = parent_context
            
            with self.tracer.start_as_current_span(**span_kwargs) as span:
                # Add description as attribute
                if self.description:
                    span.set_attribute("task.description", self.description)
                
                # Add function metadata
                span.set_attribute("function.name", func.__name__)
                span.set_attribute("function.module", func.__module__)
                
                # Log the span's trace ID
                new_trace_id = format(span.get_span_context().trace_id, '032x')
                self.logger.debug(f"Span created: {span_name} (trace_id: {new_trace_id}, parent_trace: {current_trace_id})")
                
                # Add otel context linking event
                if otel_context:
                    span.add_event("distributed_trace_linked", {
                        "parent_trace_id": otel_context['trace_id'],
                        "parent_span_id": otel_context['span_id'],
                        "span_name": span_name,
                        "function": func.__name__
                    })
                
                # Add trace context linking event (legacy support)
                if trace_context_value:
                    span.add_event("trace_context_linked", {
                        "linked_trace_id": str(trace_context_value),
                        "span_name": span_name,
                        "function": func.__name__
                    })
                
                
                # Variables for metrics
                input_size = None
                output_size = None
                serialized_args = None
                serialized_kwargs = None
                serialized_result = None
                
                # Capture input arguments
                try:
                    if args:
                        serialized_args = json.dumps(safe_serialize(args))
                        span.set_attribute("function.args", serialized_args)
                        input_size = len(serialized_args.encode('utf-8'))
                        self.logger.debug(f"Task args: {serialized_args}", extra={"task.name": span_name})
                    if kwargs:
                        serialized_kwargs = json.dumps(safe_serialize(kwargs))
                        span.set_attribute("function.kwargs", serialized_kwargs)
                        kwargs_size = len(serialized_kwargs.encode('utf-8'))
                        input_size = (input_size or 0) + kwargs_size
                        self.logger.debug(f"Task kwargs: {serialized_kwargs}", extra={"task.name": span_name})
                except Exception as e:
                    span.set_attribute("function.args_error", str(e))
                
                # Execute function
                result = None
                error = None
                error_type = None
                
                try:
                    if inspect.iscoroutinefunction(func):
                        result = await func(*args, **kwargs)
                    else:
                        result = func(*args, **kwargs)
                    
                    # Capture output
                    try:
                        serialized_result = json.dumps(safe_serialize(result))
                        span.set_attribute("function.result", serialized_result)
                        output_size = len(serialized_result.encode('utf-8'))
                        self.logger.debug(f"Task result: {serialized_result}", extra={"task.name": span_name})
                    except Exception as e:
                        span.set_attribute("function.result_error", str(e))
                    
                    # Set success status
                    span.set_status(Status(StatusCode.OK))
                    
                    # Log task completion
                    self.logger.info(f"Task '{span_name}' completed successfully", extra={
                        "task.name": span_name,
                        "task.status": "success",
                        "task.is_root": is_root,
                    })
                    
                except Exception as e:
                    error = e
                    error_type = type(e).__name__
                    
                    # Set error status (let OpenTelemetry auto-record exception on re-raise)
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    
                    # Add traceback
                    tb = traceback.format_exc()
                    span.set_attribute("error.traceback", tb)
                    
                    # Create clean traceback for logging (filter out ohtell frames)
                    clean_tb = self._filter_traceback(e)
                    
                    # Application error - log as ERROR since user needs to see their exceptions
                    # Ohtell wraps user code and should surface their errors
                    self.logger.error(f"Task '{span_name}' failed: {clean_tb}", extra={
                        "task.name": span_name,
                        "task.status": "error",
                        "task.is_root": is_root,
                        "error.type": error_type,
                        "error.message": str(e),
                        "error.category": "application"
                    })
                
                finally:
                    pass
                
                # Re-raise exception if occurred
                if error:
                    raise error
                
                return result
        
        # Store original function reference
        wrapper.__wrapped__ = func
        
        return wrapper


# Convenience decorators for common span types


def traced_task(name: Optional[str] = None, description: Optional[str] = None, task_run_name: Optional[str] = None, trace_context_key: str = "trace_id"):
    """
    Decorator for tasks that automatically link trace context.
    
    Args:
        name: Task name
        description: Task description  
        task_run_name: Template for dynamic task names
        trace_context_key: Parameter name or key to look for trace context (default: "trace_id")
    
    Usage:
        @traced_task(description="Process queue message")
        def process_message(content, trace_id):
            # trace_id automatically linked in span
            pass
    """
    return task(
        name=name,
        description=description, 
        task_run_name=task_run_name,
        trace_context_key=trace_context_key
    )


