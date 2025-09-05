#!/usr/bin/env python3
"""Demonstration of persistent connection benefits."""

import time
import sys
import asyncio
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from param_server.client import AsyncParameterClient


async def benchmark_async_client():
    """Benchmark asynchronous client with persistent connection."""
    print("\nAsynchronous Client Performance Test")
    print("=" * 42)

    client = AsyncParameterClient(host="localhost", port=8888, auto_reconnect=True)

    try:
        # Connect once
        start_time = time.time()
        await client.connect()
        connect_time = time.time() - start_time
        print(f"Initial connection time: {connect_time:.4f}s")

        # Perform many operations using the same connection
        num_operations = 100
        print(f"\nPerforming {num_operations} operations...")

        start_time = time.time()
        for i in range(num_operations):
            # These operations will reuse the existing connection
            await client.set(f"/async_benchmark/test_{i}", i)
            value = await client.get(f"/async_benchmark/test_{i}")
            assert value == i

        total_time = time.time() - start_time
        avg_time_per_op = total_time / (num_operations * 2)  # set + get = 2 ops

        print(f"Total time for {num_operations * 2} operations: {total_time:.4f}s")
        print(f"Average time per operation: {avg_time_per_op * 1000:.2f}ms")
        print(f"Operations per second: {(num_operations * 2) / total_time:.1f}")

        # Test concurrent operations
        print("\nTesting concurrent operations...")

        concurrent_ops = 20
        start_time = time.time()

        # Perform concurrent sets
        set_tasks = [client.set(f"/concurrent/test_{i}", i) for i in range(concurrent_ops)]
        await asyncio.gather(*set_tasks)

        # Perform concurrent gets
        get_tasks = [client.get(f"/concurrent/test_{i}") for i in range(concurrent_ops)]
        values = await asyncio.gather(*get_tasks)

        concurrent_time = time.time() - start_time
        print(f"Concurrent operations time: {concurrent_time:.4f}s")
        print(f"Concurrent ops/sec: {(concurrent_ops * 2) / concurrent_time:.1f}")

        # Verify results
        for i, value in enumerate(values):
            assert value == i

        # Clean up
        delete_tasks = [client.delete(f"/async_benchmark/test_{i}") for i in range(num_operations)]
        delete_tasks.extend([client.delete(f"/concurrent/test_{i}") for i in range(concurrent_ops)])
        await asyncio.gather(*delete_tasks, return_exceptions=True)

        print("✓ Async client test completed successfully")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.disconnect()


async def demonstrate_auto_reconnection():
    """Demonstrate auto-reconnection feature."""
    print("\nAuto-Reconnection Demonstration")
    print("=" * 35)

    async with AsyncParameterClient(host="localhost", port=8888, auto_reconnect=True) as client:
        try:
            # Initial connection already done in __aenter__
            print("✓ Initial connection established")

            # Perform some operations
            await client.set("/reconnect_test/value", 42)
            value = await client.get("/reconnect_test/value")
            print(f"✓ Set and retrieved value: {value}")

            # Simulate connection loss by manually disconnecting
            print("\n⚠ Simulating connection loss...")
            await client.disconnect()

            # Try to perform operations - should auto-reconnect
            print("Attempting operations after disconnect...")
            await client.set("/reconnect_test/value", 100)
            value = await client.get("/reconnect_test/value")
            print(f"✓ Auto-reconnected and retrieved value: {value}")

            # Clean up
            await client.delete("/reconnect_test/value")
            print("✓ Auto-reconnection test completed successfully")

        except Exception as e:
            print(f"Error: {e}")


async def main():
    """Main demonstration function."""
    print("Parameter Server - Persistent Connection Demo")
    print("=" * 45)
    print("This demo shows the performance benefits of persistent connections")
    print("and automatic reconnection features.\n")

    try:
        await benchmark_async_client()
        await demonstrate_auto_reconnection()

        print("\n" + "=" * 45)
        print("Demo completed successfully!")
        print("\nKey improvements:")
        print("• Persistent connections reduce latency")
        print("• Auto-reconnection improves reliability")
        print("• Better performance for multiple operations")
        print("• Graceful handling of connection issues")

    except ConnectionError:
        print("Error: Could not connect to parameter server")
        print("Make sure the server is running:")
        print("  python -m param_server.server --config examples/config/params.yml")
    except Exception as e:
        print(f"Demo failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
