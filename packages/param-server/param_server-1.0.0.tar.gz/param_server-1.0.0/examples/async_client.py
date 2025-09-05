#!/usr/bin/env python3
"""Async client example demonstrating asynchronous parameter operations."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from param_server.client import AsyncParameterClient


async def parameter_monitor(client: AsyncParameterClient, path: str, duration: int = 10):
    """Monitor a parameter for changes."""
    print(f"Monitoring {path} for {duration} seconds...")

    last_value = None
    start_time = asyncio.get_event_loop().time()

    while (asyncio.get_event_loop().time() - start_time) < duration:
        try:
            current_value = await client.get(path)
            if current_value != last_value:
                print(f"  {path} changed: {last_value} -> {current_value}")
                last_value = current_value
        except KeyError:
            if last_value is not None:
                print(f"  {path} was deleted")
                last_value = None
        except Exception as e:
            print(f"  Error monitoring {path}: {e}")

        await asyncio.sleep(0.1)  # Check every 100ms


async def parameter_updater(client: AsyncParameterClient, path: str, values: list, interval: float = 1.0):
    """Update a parameter with different values."""
    print(f"Updating {path} with values: {values}")

    for i, value in enumerate(values):
        await asyncio.sleep(interval)
        try:
            await client.set(path, value)
            print(f"  Set {path} = {value}")
        except Exception as e:
            print(f"  Error setting {path}: {e}")


async def demonstrate_async_operations():
    """Demonstrate asynchronous parameter operations."""
    print("Parameter Server - Async Client Example")
    print("=" * 42)

    # Create client with auto-reconnect enabled
    client = AsyncParameterClient(host="localhost", port=8888, auto_reconnect=True)

    try:
        await client.connect()
        print("Connected to parameter server")
        print("Note: Using persistent connection for all operations!")

        # Test basic operations
        print("\n1. Basic async operations...")

        await client.set("/async_test/counter", 0)
        await client.set("/async_test/name", "async_example")
        await client.set("/async_test/active", True)

        counter = await client.get("/async_test/counter")
        name = await client.get("/async_test/name")
        active = await client.get("/async_test/active")

        print(f"Counter: {counter}")
        print(f"Name: {name}")
        print(f"Active: {active}")

        # Test concurrent operations
        print("\n2. Concurrent parameter operations...")

        # Setup multiple parameters concurrently
        tasks = []
        for i in range(5):
            task = client.set(f"/async_test/param_{i}", i * 10)
            tasks.append(task)

        await asyncio.gather(*tasks)
        print("Set 5 parameters concurrently")

        # Get multiple parameters concurrently
        get_tasks = []
        for i in range(5):
            task = client.get(f"/async_test/param_{i}")
            get_tasks.append(task)

        values = await asyncio.gather(*get_tasks)
        print(f"Retrieved values: {values}")

        # Test monitoring and updating simultaneously
        print("\n3. Concurrent monitoring and updating...")

        # Create tasks for monitoring and updating
        monitor_task = asyncio.create_task(parameter_monitor(client, "/async_test/dynamic_param", duration=5))

        update_task = asyncio.create_task(
            parameter_updater(client, "/async_test/dynamic_param", [10, 20, 30, 40, 50], interval=1.0)
        )

        # Run both tasks concurrently
        await asyncio.gather(monitor_task, update_task)

        print("\n4. Bulk parameter listing...")

        # List parameters with different prefixes concurrently
        list_tasks = [
            client.list_params("/async_test"),
            client.list_params("/camera") if await client.ping() else asyncio.sleep(0),
            client.list_params("/system") if await client.ping() else asyncio.sleep(0),
        ]

        results = await asyncio.gather(*list_tasks, return_exceptions=True)

        for i, result in enumerate(results):
            if isinstance(result, list):
                prefix = ["/async_test", "/camera", "/system"][i]
                print(f"Parameters with prefix {prefix}: {len(result)} found")

        print("\n5. Error handling in async context...")

        # Test concurrent error handling
        error_tasks = [
            client.get("/non_existent_1"),
            client.get("/non_existent_2"),
            client.get("/async_test/counter"),  # This should succeed
        ]

        results = await asyncio.gather(*error_tasks, return_exceptions=True)

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"Task {i}: Error - {result}")
            else:
                print(f"Task {i}: Success - {result}")

        print("\n6. Cleanup...")

        # Delete test parameters
        async_params = await client.list_params("/async_test")
        delete_tasks = [client.delete(param) for param in async_params]
        await asyncio.gather(*delete_tasks, return_exceptions=True)
        print(f"Cleaned up {len(async_params)} test parameters")

        print("\nAsync client example completed successfully!")
        print("All operations used a single persistent connection with auto-reconnect!")

    except ConnectionError:
        print("Error: Could not connect to parameter server")
        print("Make sure the server is running:")
        print("  python -m param_server.server --config examples/config/params.yml")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.disconnect()


async def main():
    """Main async entry point."""
    await demonstrate_async_operations()


if __name__ == "__main__":
    asyncio.run(main())
