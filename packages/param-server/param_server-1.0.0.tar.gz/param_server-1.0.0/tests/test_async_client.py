"""Tests for async parameter client functionality."""

import pytest
import asyncio

from param_server.client import AsyncParameterClient


@pytest.mark.asyncio
class TestAsyncParameterClient:
    """Test cases for AsyncParameterClient."""

    async def test_async_connection(self, test_server):
        """Test async client connection and disconnection."""
        server = test_server
        client = AsyncParameterClient(host="localhost", port=server.port)

        assert not client.is_connected()

        await client.connect()
        assert client.is_connected()

        await client.disconnect()
        assert not client.is_connected()

    async def test_async_context_manager(self, test_server):
        """Test async client as context manager."""
        server = test_server

        async with AsyncParameterClient(host="localhost", port=server.port) as client:
            assert client.is_connected()
            assert await client.ping()

        assert not client.is_connected()

    async def test_async_basic_operations(self, test_server):
        """Test basic async get/set operations."""
        server = test_server

        async with AsyncParameterClient(host="localhost", port=server.port) as client:
            # Set parameters
            await client.set("/test/string", "hello")
            await client.set("/test/int", 42)
            await client.set("/test/float", 3.14)
            await client.set("/test/bool", True)

            # Get parameters
            assert await client.get("/test/string") == "hello"
            assert await client.get("/test/int") == 42
            assert await client.get("/test/float") == 3.14
            assert await client.get("/test/bool") is True

    async def test_concurrent_operations(self, test_server):
        """Test concurrent parameter operations."""
        server = test_server

        async with AsyncParameterClient(host="localhost", port=server.port) as client:
            # Set multiple parameters concurrently
            await asyncio.gather(
                client.set("/concurrent/param1", "value1"),
                client.set("/concurrent/param2", 42),
                client.set("/concurrent/param3", True),
                client.set("/concurrent/param4", 3.14),
            )

            # Get multiple parameters concurrently
            results = await asyncio.gather(
                client.get("/concurrent/param1"),
                client.get("/concurrent/param2"),
                client.get("/concurrent/param3"),
                client.get("/concurrent/param4"),
            )

            assert results == ["value1", 42, True, 3.14]

    async def test_async_parameter_listing(self, test_server):
        """Test async parameter listing functionality."""
        server = test_server

        async with AsyncParameterClient(host="localhost", port=server.port) as client:
            # Set up test parameters
            await asyncio.gather(
                client.set("/camera/exposure", 0.033),
                client.set("/camera/gain", 1.5),
                client.set("/robot/joint1", 0.0),
                client.set("/system/debug", True),
            )

            # Test listing all parameters
            all_params = await client.list_params()
            assert len(all_params) >= 4

            # Test listing with prefix
            camera_params = await client.list_params("/camera")
            assert len(camera_params) == 2

    async def test_async_error_handling(self, test_server):
        """Test async error handling for various scenarios."""
        server = test_server

        async with AsyncParameterClient(host="localhost", port=server.port) as client:
            # Test getting non-existent parameter
            with pytest.raises(KeyError):
                await client.get("/nonexistent/param")

            # Test deleting non-existent parameter
            with pytest.raises(KeyError):
                await client.delete("/nonexistent/param")

            # Test setting invalid type
            with pytest.raises(ValueError):
                await client.set("/test/invalid", [1, 2, 3])

    async def test_async_ping(self, test_server):
        """Test async ping functionality."""
        server = test_server

        async with AsyncParameterClient(host="localhost", port=server.port) as client:
            assert await client.ping() is True

    async def test_concurrent_clients(self, test_server):
        """Test multiple async clients accessing server simultaneously."""
        server = test_server

        async def client_worker(client_id):
            async with AsyncParameterClient(host="localhost", port=server.port) as client:
                # Each client sets and gets its own parameters
                tasks = []
                for i in range(10):
                    param_name = f"/async_client_{client_id}/param_{i}"
                    tasks.append(client.set(param_name, i * client_id))

                await asyncio.gather(*tasks)

                # Verify all parameters were set correctly
                get_tasks = []
                for i in range(10):
                    param_name = f"/async_client_{client_id}/param_{i}"
                    get_tasks.append(client.get(param_name))

                values = await asyncio.gather(*get_tasks)

                for i, value in enumerate(values):
                    assert value == i * client_id

                return "success"

        # Start multiple async clients
        results = await asyncio.gather(client_worker(1), client_worker(2), client_worker(3))

        # Verify all clients succeeded
        assert all(result == "success" for result in results)
