#!/usr/bin/env python3
"""
Test script to demonstrate colored logging output and task name coloring.
Run this to see how the colored logs look in your terminal.
"""

import asyncio
from ohtell import task, add_event

# Test different log levels and scenarios
@task(name="Colored Log Demo")
async def demo_logging():
    """Demonstrate different types of log messages with colors."""
    
    print("=== Testing Colored Logging Output ===")
    print("Colors should appear as:")
    print("- Timestamp: Grey")
    print("- Logger name (ohtell.task): Grey") 
    print("- Log levels: INFO=Green, ERROR=Red, WARNING=Yellow, DEBUG=Cyan")
    print("- Task names: Success=Bold Green, Failed=Bold Red")
    print()
    
    # Add some events to generate different log messages
    add_event("demo_started", {"test": "colored_logging"})
    
    # Simulate some work
    await asyncio.sleep(0.1)
    
    add_event("processing_data", {"records": 100, "status": "in_progress"})
    
    # More work
    await asyncio.sleep(0.1)
    
    add_event("demo_completed", {"success": True, "duration_ms": 200})
    
    return {"status": "completed", "colors_tested": True}

@task(name="Success Task")
async def success_task():
    """This will succeed and show green bold task name."""
    print("This task will succeed!")
    return {"status": "success"}

@task(name="Warning Demo") 
async def demo_warning():
    """This will generate a warning-level log."""
    import logging
    logger = logging.getLogger("ohtell.task")
    logger.warning("This is a warning message - should be YELLOW")
    return "warning_shown"

@task(name="Failure Task")
async def failure_task():
    """This will fail and show red bold task name."""
    print("This task will fail!")
    raise ValueError("This task failed on purpose")

@task(name="Debug Demo")  
async def demo_debug():
    """This will generate debug messages."""
    import logging
    logger = logging.getLogger("ohtell.task")
    logger.setLevel(logging.DEBUG)  # Enable debug for this test
    logger.debug("This is a debug message - should be CYAN")
    return "debug_shown"

async def main():
    """Run all the demo tasks."""
    print("🎨 Colored Logging Demo")
    print("=" * 50)
    
    # Test successful task (INFO level)
    result1 = await demo_logging()
    print(f"✅ Demo result: {result1}")
    
    # Test successful task with different name
    result2 = await success_task()
    print(f"✅ Success result: {result2}")
    
    # Test warning level
    result3 = await demo_warning() 
    print(f"⚠️  Warning demo: {result3}")
    
    # Test debug level
    result4 = await demo_debug()
    print(f"🐛 Debug demo: {result4}")
    
    # Test error level (this will show error logs)
    try:
        await failure_task()
    except ValueError as e:
        print(f"❌ Caught expected error: {e}")
    
    print("\n" + "=" * 50)
    print("Demo completed! Check the colored log output above.")
    print("Expected colors:")
    print("- Timestamps and 'ohtell.task': Grey")
    print("- 'Colored Log Demo', 'Success Task': Bold Green") 
    print("- 'Failure Task': Bold Red")
    print("- Log levels colored by severity")

if __name__ == "__main__":
    asyncio.run(main())