# ohtell

## unreliable observability is worse than no observability

A simple, async-first OpenTelemetry decorator for tracing Python functions. Automatically captures traces, metrics, and logs with minimal setup.

## Disclaimer 1: Why ohtell exists

You wanted to try OpenTelemetry because it's cool, it's funky, and you want to observe your code like a l33t engineer. But then you start reading their [Getting Started guide](https://opentelemetry.io/docs/languages/python/getting-started/) and realize that OTEL becomes "Oh Hell!" 

- **What you want**: "Just works"
- **What OpenTelemetry gives you**: 47 lines of boilerplate, 12 imports, and 100 backends that work just a little bit different

So ohtell was born out of frustration that to collect and send JSON (and traces are just objects) you need a PhD in distributed tracing theory.

## Disclaimer 2: The Observability Ego Problem

Observability tools often have such an **inflated ego** that they crash your services when they can't authorize, hit rate limits, or parse your logs.

**Classic Catch-22**: You don't know that your service failed... because the observability wrapper killed your service... because it couldn't connect to the backend to tell that your app working just fine. 🤦‍♂️

- **What you want**: "Hey, I can't connect to track your stuff right now, but your code keeps working fine. I'll show you a warning when I'm back online."
- **What you get**: `AuthenticationError: Service destroyed. Have a nice day! 💥`

## Disclaimer 3: The Performance Killer Problem

Most observability tools will **murder your performance** because they send logs and traces synchronously. 

**Picture this**: You're processing a high-volume Kafka queue. Each message takes 50ms to process. But your observability tool runs 3 blocking queries around each message - authentication (300ms), span creation (200ms), and export (400ms). **Congratulations, your 50ms job now takes 950ms.**

Your Kafka queue goes from processing 1000 messages/sec to... 1 message/sec. Your observability tool just made your system 1000x slower. Great job! 👏

- **ohtell's approach**: Fire-and-forget in background threads. Your code runs at full speed while telemetry gets sent **when there's processing power available**
- **Philosophy**: Observability is important, but **not more important than your actual work**

## ⚠️ Experimental Software Warning

This is experimental software because OpenTelemetry is still evolving rapidly. Some issues may arise as the ecosystem changes. 

**Found a bug? Something broken?** Use our [GitHub issue tracker](https://github.com/anthropics/claude-code/issues) and let's fix the shit out of it together!

## Features

- 🎯 **Async-first decorator API** - All functions become async when decorated
- 🖥️ **Console output by default** - No setup needed, outputs to console when no OTEL endpoint configured
- 🔄 **Automatic span hierarchy** - Nested function calls create proper parent-child relationships  
- 📊 **Complete observability** - Traces, metrics, and logs in one package
- 📝 **Print capture** - Automatically captures print statements as events and logs
- 🏷️ **Dynamic naming** - Template-based span names with parameters
- ⚡ **Zero-block export** - Fire-and-forget telemetry that doesn't block your code

## Installation

```bash
pip install ohtell
```

## Quick Start

```python
import asyncio
from ohtell import task

@task(name="Hello World")
async def hello(name: str):
    print(f"Hello {name}!")
    return f"Greetings, {name}"

# Run it
result = asyncio.run(hello("World"))
```

When no OTLP endpoint is configured, ohtell automatically outputs all telemetry data to the console in a readable format. This includes:
- Structured trace spans with timing and hierarchy
- All print statements captured as events
- Function arguments and return values
- Error details and stack traces
- Metrics summaries

**Console output is enabled when:**
- No `OTEL_EXPORTER_OTLP_ENDPOINT` environment variable is set
- No `endpoint` is specified in config.yaml
- The endpoint is explicitly set to `console: true` in config.yaml

### Option 1: Environment Variables (OTLP Standard)

```bash
# OTLP endpoint (if not set, outputs to console)
export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4317"

# Optional: Authentication headers
export OTEL_EXPORTER_OTLP_HEADERS="Authorization=Bearer your-token"

# Optional: Service identification
export OTEL_SERVICE_NAME="my-app"
export OTEL_RESOURCE_ATTRIBUTES="service.namespace=production,deployment.environment=prod"

# Optional: Protocol (defaults to http/protobuf)
export OTEL_EXPORTER_OTLP_PROTOCOL="grpc"
```

### Option 2: Config File (config.yaml)

Create a `config.yaml` file in your project root:

```yaml
otel:
  endpoint: "http://localhost:4317"
  headers: "Authorization=Bearer your-token"
  protocol: "grpc"  # or "http/protobuf"
  resource_attributes: "service.namespace=production,deployment.environment=prod"

# Or explicitly enable console output
otel:
  console: true  # Forces console output even if endpoint is set
```

### Option 3: Programmatic Configuration

**⚠️ IMPORTANT**: Environment variables must be set **BEFORE** importing ohtell:

```python
import asyncio
import os

# Set environment variables BEFORE importing ohtell
os.environ['OTEL_EXPORTER_OTLP_ENDPOINT'] = 'http://localhost:4317'
os.environ['OTEL_EXPORTER_OTLP_HEADERS'] = 'Authorization=Bearer your-token'
os.environ['OTEL_RESOURCE_ATTRIBUTES'] = 'service.name=my-app,service.namespace=production'

# Import AFTER setting environment variables
from ohtell import task

@task(name="Configured Task")
async def configured_task():
    return "configured"

asyncio.run(configured_task())
```

**Configuration Priority**: Environment variables → config.yaml → defaults

- Environment variables set **before import** work ✅
- Config.yaml files are always reliable ✅  
- Environment variables set **after import** are ignored ❌

## Distributed Tracing

**Problem**: HTTP calls between services create separate traces.

**Solution**: Pass trace context in HTTP headers, use `__otel_context` to link spans.

### Helper Functions

#### `get_otel_context()`

Extracts current span context as a dictionary for distributed tracing:

```python
from ohtell import get_otel_context

context = get_otel_context()
# Returns: {'trace_id': '...', 'span_id': '...', 'trace_flags': 1, 'is_remote': True}
```

#### `set_trace_id(trace_id)`

Overrides the trace ID for testing or custom scenarios:

```python
from ohtell import set_trace_id

# Use a custom trace ID (32 hex characters)
set_trace_id('deadbeefcafebabe1234567890abcdef')
```


### HTTP Example

```python
import httpx
from ohtell import task, get_otel_context

@task(name="Client Service")
async def call_api():
    context = get_otel_context()
    headers = {"X-Trace-Id": context['trace_id'], "X-Span-Id": context['span_id']}
    
    async with httpx.AsyncClient() as client:
        response = await client.post("http://api/process", headers=headers, json={"data": "test"})
    
    return response.json()

@task
def process_data(data):
    print(data)

async def handle_api_request(request_headers, data):
    if "X-Trace-Id" in request_headers:
        remote_context = {
            'trace_id': request_headers["X-Trace-Id"], 
            'span_id': request_headers["X-Span-Id"],
            'trace_flags': 1,
            'is_remote': True
        }
        return await process_data(data, __otel_context=remote_context)
    
    return await process_data(data)
```

### Queue Example

```python
import asyncio
from ohtell import task, get_otel_context

@task(name="Producer")
async def send_to_queue(data):
    context = get_otel_context()
    
    # Add trace context to message
    message = {
        "data": data,
        "user_id": "123",
        "__otel_context": context
    }
    
    await queue.put(message)
    return message

@task(name="Consumer") 
async def process_queue_message(message):
    # Extract context and pass to processor
    context = message.get("__otel_context")
    return await process_data(message["data"], message["user_id"], __otel_context=context)

@task(name="Process Data")
async def process_data(data, user_id):
    return f"processed {data} for {user_id}"

# Usage
async def main():
    # Producer creates message with trace context
    message = await send_to_queue("user_signup")
    
    # Consumer processes message - maintains same trace_id as producer
    result = await process_queue_message(message)
    print(result)  # "processed user_signup for 123"

asyncio.run(main())
```

**Result**: Producer and process_data spans share the same trace_id, even though consumer has its own trace. The message payload bridges the trace across the async boundary.

**Result**: Client and server spans share the same trace_id. The `__otel_context` parameter is consumed by `@task` - your functions never see it.

## Examples

### Basic API Workflow

```python
import asyncio
from ohtell import task, add_event

@task(name="API Endpoint")
async def api_handler(request_id: str):
    """Simulate an API endpoint."""
    print(f"Processing request {request_id}")
    add_event("request_received", {"request_id": request_id})
    
    result = await process_data(request_id, data_size=100)
    
    add_event("request_completed", {"request_id": request_id, "result_size": len(result)})
    return result

@task(name="Data Processing")
async def process_data(request_id: str, data_size: int):
    """Simulate data processing."""
    print(f"Processing {data_size} items for {request_id}")
    
    processed = []
    for i in range(data_size):
        item_result = await transform_item(f"item_{i}")
        processed.append(item_result)
    
    print(f"Processed {len(processed)} items")
    return processed

@task(name="Transform Item")
async def transform_item(item: str):
    """Simulate item transformation."""
    await asyncio.sleep(0.001)  # Simulate work
    return f"transformed_{item}"

# Execute the workflow
result = asyncio.run(api_handler("test_request_123"))
```

### Error Handling

```python
import asyncio
from ohtell import task

@task(name="Failing Task")
async def failing_task(should_fail: bool = True):
    """Task that can fail."""
    print("Starting task...")
    
    if should_fail:
        raise ValueError("Simulated failure")
    
    return "success"

@task(name="Error Handler")
async def error_handler():
    """Task that handles errors."""
    results = []
    
    # Try successful task
    try:
        success_result = await failing_task(should_fail=False)
        results.append(("success", success_result))
    except Exception as e:
        results.append(("error", str(e)))
    
    # Try failing task  
    try:
        fail_result = await failing_task(should_fail=True)
        results.append(("success", fail_result))
    except Exception as e:
        results.append(("error", str(e)))
    
    return results

results = asyncio.run(error_handler())
# Results: [('success', 'success'), ('error', 'Simulated failure')]
```

### Dynamic Task Names

```python
import asyncio
from ohtell import task

@task(
    name="backup-{operation}-{priority}",
    description="Dynamic task name example"
)
async def scheduled_backup(operation: str, priority: str, size_mb: int):
    """Task with dynamic naming based on parameters."""
    print(f"Starting {operation} backup with {priority} priority")
    print(f"Backing up {size_mb}MB of data")
    
    # Simulate backup time proportional to size
    backup_time = size_mb * 0.0001  # 0.1ms per MB
    await asyncio.sleep(backup_time)
    
    print(f"Backup completed: {operation}")
    return {
        "operation": operation,
        "priority": priority, 
        "size_mb": size_mb,
        "success": True
    }

# Creates spans named: "backup-database-high", "backup-files-medium"
result1 = asyncio.run(scheduled_backup("database", "high", 1000))
result2 = asyncio.run(scheduled_backup("files", "medium", 500))
```

### Nested Span Hierarchy

```python
import asyncio
from ohtell import task

@task(name="Level 1", description="Top level task")
async def level_1():
    """Top level function."""
    print("Entering level 1")
    result = await level_2()
    print("Exiting level 1")
    return f"level_1({result})"

@task(name="Level 2", description="Second level task")
async def level_2():
    """Second level function."""
    print("Entering level 2") 
    result = await level_3()
    print("Exiting level 2")
    return f"level_2({result})"

@task(name="Level 3", description="Third level task")
async def level_3():
    """Third level function."""
    print("Entering level 3")
    await asyncio.sleep(0.001)  # Simulate work
    print("Exiting level 3")
    return "level_3()"

# Creates nested spans: Level 1 > Level 2 > Level 3
result = asyncio.run(level_1())
# Result: "level_1(level_2(level_3()))"
```

## What Gets Captured

Each decorated function automatically captures:

- **Traces**: Span hierarchy with timing, status, and relationships
- **Metrics**: Call counts, error rates, duration histograms, active task gauges
- **Logs**: Print statements and structured logs, correlated with traces
- **Events**: Custom events with `add_event()` function
- **Errors**: Automatic exception recording with full tracebacks
- **I/O**: Function arguments and return values (safely serialized)

## Metrics Collected

- `task_calls_total` - Total function calls (by task name, function, status)
- `task_errors_total` - Total errors (by error type)
- `task_prints_total` - Print statements captured
- `task_duration_seconds` - Function execution time distribution
- `task_input_size` - Size of input arguments (bytes)
- `task_output_size` - Size of return values (bytes)
- `active_tasks` - Currently executing functions

## Adding Events and Span Data

### Custom Events

Add structured events to your traces with the `add_event` function:

```python
import asyncio
import time
from ohtell import task, add_event

@task(name="User Registration")
async def register_user(email: str, plan: str):
    """Register a new user with event tracking."""
    
    # Add event at the start
    add_event("registration_started", {
        "email": email,
        "plan": plan,
        "timestamp": time.time()
    })
    
    # Simulate validation
    if "@" not in email:
        add_event("validation_failed", {"reason": "invalid_email"})
        raise ValueError("Invalid email format")
    
    # Add event for successful validation
    add_event("validation_passed", {"email_domain": email.split("@")[1]})
    
    # Simulate database save
    await asyncio.sleep(0.1)
    
    # Add event for completion
    add_event("registration_completed", {
        "user_id": f"user_{hash(email) % 10000}",
        "plan": plan,
        "success": True
    })
    
    return {"user_id": f"user_{hash(email) % 10000}", "status": "active"}

# Run it
result = asyncio.run(register_user("user@example.com", "premium"))
```

### Span Attributes vs Events

- **Events** (`add_event`): Time-stamped log entries within a span. Use for discrete occurrences.
- **Attributes**: Key-value metadata about the entire span. Automatically captured from function arguments and return values.

```python
import asyncio
from ohtell import task, add_event

@task(name="Data Processing Pipeline")
async def process_data(dataset_id: str, batch_size: int = 100):
    """Example showing events vs automatic attributes."""
    
    # Function arguments become span attributes automatically:
    # - dataset_id: "customers_2024"
    # - batch_size: 100
    
    # Events capture specific moments in time
    add_event("pipeline_started", {
        "dataset_id": dataset_id,
        "batch_size": batch_size
    })
    
    processed_count = 0
    for batch_num in range(3):  # Simulate 3 batches
        add_event("batch_started", {"batch_number": batch_num + 1})
        
        await asyncio.sleep(0.01)  # Simulate processing
        batch_processed = min(batch_size, 250 - processed_count)
        processed_count += batch_processed
        
        add_event("batch_completed", {
            "batch_number": batch_num + 1,
            "records_processed": batch_processed,
            "total_processed": processed_count
        })
    
    add_event("pipeline_completed", {
        "total_records": processed_count,
        "batches_completed": 3
    })
    
    # Return value becomes a span attribute automatically
    return {"processed_records": processed_count, "status": "success"}

result = asyncio.run(process_data("customers_2024", batch_size=150))
```

### Event Best Practices

1. **Use descriptive names**: `user_login_attempt`, `payment_processed`, `cache_miss`
2. **Include relevant context**: user IDs, request IDs, error codes
3. **Add timestamps when relevant**: Custom timestamps for external events
4. **Keep attributes simple**: Strings, numbers, booleans work best

```python
# Good event examples
add_event("cache_miss", {"key": "user_123", "cache_type": "redis"})
add_event("api_call_started", {"endpoint": "/users", "method": "GET"})
add_event("validation_error", {"field": "email", "error": "format_invalid"})

# Avoid complex objects in events
add_event("user_data", {"user": user_object})  # Bad - complex object
add_event("user_registered", {"user_id": user.id})  # Good - simple ID
```

## Error Handling and Span Status

### Automatic Exception Handling

ohtell automatically marks spans as failed when exceptions occur and captures full error details:

```python
import asyncio
from ohtell import task, add_event

@task(name="Database Operation")
async def save_user(user_id: str, email: str):
    """Function that may fail with automatic error handling."""
    
    add_event("save_started", {"user_id": user_id})
    
    # Simulate validation
    if not email or "@" not in email:
        # Exception automatically marks span as FAILED
        # Records full traceback and error details
        raise ValueError(f"Invalid email format: {email}")
    
    # Simulate database error
    if user_id == "user_999":
        raise ConnectionError("Database connection failed")
    
    add_event("save_completed", {"user_id": user_id})
    return {"status": "saved", "user_id": user_id}

# Test successful case
try:
    result = asyncio.run(save_user("user_123", "valid@example.com"))
    print(f"Success: {result}")  # Span marked as OK
except Exception as e:
    print(f"Failed: {e}")

# Test failed case  
try:
    result = asyncio.run(save_user("user_999", "test@example.com"))
except Exception as e:
    print(f"Failed: {e}")  # Span marked as ERROR with full traceback
```

### What Gets Captured on Errors

When an exception occurs, ohtell automatically captures:

- **Span Status**: Set to `ERROR` with error message
- **Exception Recording**: Full exception details using OpenTelemetry's `record_exception()`
- **Error Traceback**: Complete stack trace in `error.traceback` attribute
- **Error Type**: Exception class name in metrics and logs
- **Error Message**: Exception message in span status

### Error Propagation

Errors are automatically propagated up the span hierarchy:

```python
import asyncio
from ohtell import task, add_event

@task(name="Level 1 - API Handler")  
async def api_handler(user_id: str):
    """Top level handler - will be marked as ERROR if any child fails."""
    add_event("api_call_started", {"user_id": user_id})
    
    try:
        result = await business_logic(user_id)
        add_event("api_call_completed", {"user_id": user_id})
        return result
    except Exception as e:
        # Even though we catch here, the span is already marked as ERROR
        add_event("api_call_failed", {"user_id": user_id, "error": str(e)})
        raise  # Re-raise to maintain error status

@task(name="Level 2 - Business Logic")
async def business_logic(user_id: str):
    """Middle layer - error here affects parent span."""
    add_event("processing_started", {"user_id": user_id})
    
    result = await database_save(user_id)
    return result

@task(name="Level 3 - Database Save")  
async def database_save(user_id: str):
    """Lowest level - error originates here."""
    add_event("db_save_started", {"user_id": user_id})
    
    if user_id == "invalid":
        # This error marks ALL parent spans as ERROR too
        raise ValueError("Invalid user ID")
    
    return {"saved": user_id}

# This creates an error hierarchy:
# Level 1 - API Handler (ERROR due to child failure)
#   └── Level 2 - Business Logic (ERROR due to child failure)  
#       └── Level 3 - Database Save (ERROR - original source)
try:
    result = asyncio.run(api_handler("invalid"))
except ValueError as e:
    print(f"Caught: {e}")
```

### Custom Error Context

Add custom error context with events before exceptions:

```python
import asyncio
from ohtell import task, add_event

@task(name="File Processor")
async def process_file(file_path: str, max_size_mb: int = 10):
    """Process file with detailed error context."""
    
    add_event("processing_started", {
        "file_path": file_path,
        "max_size_mb": max_size_mb
    })
    
    # Check file existence
    import os
    if not os.path.exists(file_path):
        add_event("file_not_found", {"file_path": file_path})
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Check file size
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    add_event("file_size_checked", {
        "file_path": file_path, 
        "size_mb": file_size_mb,
        "max_allowed_mb": max_size_mb
    })
    
    if file_size_mb > max_size_mb:
        add_event("file_too_large", {
            "file_path": file_path,
            "size_mb": file_size_mb,
            "max_allowed_mb": max_size_mb,
            "over_limit_by_mb": file_size_mb - max_size_mb
        })
        raise ValueError(f"File too large: {file_size_mb}MB > {max_size_mb}MB")
    
    add_event("processing_completed", {"file_path": file_path})
    return {"processed": file_path, "size_mb": file_size_mb}

# Test error cases with rich context
try:
    result = asyncio.run(process_file("/nonexistent/file.txt"))
except FileNotFoundError as e:
    print(f"File error: {e}")

try:  
    result = asyncio.run(process_file("large_file.txt", max_size_mb=1))
except ValueError as e:
    print(f"Size error: {e}")
```

All error information is automatically captured in traces, metrics, and logs without any additional code.

## Export Control

```python
from ohtell import force_flush, trigger_export, shutdown

# Wait for all data to be exported (blocks)
force_flush()

# Trigger export in background (non-blocking)
trigger_export()

# Manual shutdown
shutdown()
```

## Configuration Options

### Environment Variables

**Core OTLP Configuration:**
| Variable | Default | Config YAML Key | Description |
|----------|---------|-----------------|-------------|
| `OTEL_EXPORTER_OTLP_ENDPOINT` | *(none)* | `endpoint` | OTLP endpoint URL. If not set, outputs to console |
| `OTEL_EXPORTER_OTLP_HEADERS` | *(none)* | `headers` | Authentication headers |
| `OTEL_EXPORTER_OTLP_PROTOCOL` | `http/protobuf` | `protocol` | Protocol: `grpc` or `http/protobuf` |
| `OTEL_SERVICE_NAME` | `ohtell-app` | *(via resource_attributes)* | Service name |
| `OTEL_RESOURCE_ATTRIBUTES` | *(none)* | `resource_attributes` | Resource attributes (comma-separated key=value) |

**Export Configuration:**
| Variable | Default | Config YAML Key | Description |
|----------|---------|-----------------|-------------|
| `OTEL_SPAN_EXPORT_INTERVAL_MS` | `500` | `span_export_interval_ms` | Trace export interval (milliseconds) |
| `OTEL_LOG_EXPORT_INTERVAL_MS` | `500` | `log_export_interval_ms` | Log export interval (milliseconds) |
| `OTEL_METRIC_EXPORT_INTERVAL_MS` | `30000` | `metric_export_interval_ms` | Metric export interval (milliseconds) |
| `OTEL_MAX_EXPORT_BATCH_SIZE` | `50` | `max_export_batch_size` | Maximum batch size for exports |
| `OTEL_MAX_QUEUE_SIZE` | `512` | `max_queue_size` | Maximum queue size |

**ohtell-Specific Configuration:**
| Variable | Default | Config YAML Key | Description |
|----------|---------|-----------------|-------------|
| `OTEL_METRICS_SAMPLING_RATE` | `0.1` | `metrics_sampling_rate` | Metrics sampling rate (0.0 to 1.0) |
| `OTEL_METRICS_ENABLED` | `true` | `metrics_enabled` | Enable/disable metrics collection |
| `OTEL_WRAPPER_SKIP_CLEANUP` | `true` | `skip_cleanup` | Skip automatic cleanup on process exit |

**Environment variables always take precedence over config.yaml settings.**

### Config File Format (config.yaml)

```yaml
otel:
  # Core OTLP Configuration
  endpoint: "http://localhost:4317"           # OTLP endpoint (omit for console output)
  console: true                              # Force console output (overrides endpoint)
  headers: "Authorization=Bearer token123"    # Auth headers  
  protocol: "grpc"                           # grpc or http/protobuf
  resource_attributes: "key1=value1,key2=value2"  # Resource attributes
  
  # Export Intervals (milliseconds)
  span_export_interval_ms: 500               # Trace export interval (0.5 seconds)
  log_export_interval_ms: 500                # Log export interval (0.5 seconds)  
  metric_export_interval_ms: 30000           # Metric export interval (30 seconds)
  
  # Batch Configuration
  max_export_batch_size: 50                  # Maximum batch size for exports
  max_queue_size: 512                        # Maximum queue size
  
  # Metrics Configuration
  metrics_sampling_rate: 0.1                 # Sample 10% of metrics
  metrics_enabled: true                      # Enable metrics collection
  
  # Cleanup Configuration  
  skip_cleanup: true                         # Skip automatic cleanup on exit
```

The config file is automatically loaded from the project root if it exists. **Environment variables take precedence over config file values.**

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest tests/

# Run specific test categories
pytest tests/test_integration.py  # Integration tests with real examples
pytest tests/test_config.py       # Configuration tests
pytest tests/test_metrics.py      # Metrics functionality tests
```

The integration tests in `tests/test_integration.py` contain realistic examples that demonstrate all features working together.
