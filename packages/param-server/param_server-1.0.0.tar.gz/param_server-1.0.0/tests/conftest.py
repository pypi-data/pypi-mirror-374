"""Test configuration and fixtures for parameter server tests."""

import pytest
import pytest_asyncio
import asyncio
import tempfile
import threading
import time
from pathlib import Path

from param_server.server import ParameterServer
from param_server.client import AsyncParameterClient
from param_server.store import ParameterStore


@pytest.fixture
def param_store():
    """Create a fresh parameter store for testing."""
    return ParameterStore()


@pytest.fixture
def temp_config_file():
    """Create a temporary YAML config file for testing."""
    config_content = """
test:
  string_param: "test_value"
  int_param: 42
  float_param: 3.14
  bool_param: true
  nested:
    deep_param: "deep_value"
    number: 100

camera:
  exposure: 0.033
  gain: 1.5
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        f.write(config_content)
        f.flush()
        yield f.name

    # Cleanup
    Path(f.name).unlink(missing_ok=True)


@pytest_asyncio.fixture
async def test_server():
    """Start a test parameter server."""
    server = ParameterServer(host="localhost", port=0)  # Use any available port

    # Start server in background
    server_task = asyncio.create_task(server.start())

    # Wait a bit for server to start
    await asyncio.sleep(0.1)

    # Get the actual port number
    actual_port = server.server.sockets[0].getsockname()[1]
    server.port = actual_port

    yield server

    # Cleanup
    await server.stop()
    server_task.cancel()
    try:
        await server_task
    except asyncio.CancelledError:
        pass


@pytest.fixture
async def async_client(test_server):
    """Create an async test client connected to test server."""
    server = test_server
    client = AsyncParameterClient(host="localhost", port=server.port)
    await client.connect()
    yield client
    await client.disconnect()


class ServerRunner:
    """Helper class to run server in a separate thread for sync tests."""

    def __init__(self, host="localhost", port=8889):
        self.host = host
        self.port = port
        self.server = None
        self.thread = None
        self.loop = None
        self._stop_event = threading.Event()

    def start(self):
        """Start server in background thread."""
        self.thread = threading.Thread(target=self._run_server)
        self.thread.daemon = True
        self.thread.start()

        # Wait for server to start
        time.sleep(0.2)

    def stop(self):
        """Stop the server."""
        if self.loop and self.server:
            self.loop.call_soon_threadsafe(lambda: asyncio.create_task(self.server.stop()))

        self._stop_event.set()

        if self.thread:
            self.thread.join(timeout=2.0)

    def _run_server(self):
        """Run server in thread."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        self.server = ParameterServer(self.host, self.port)

        try:
            self.loop.run_until_complete(self.server.start())
        except Exception:
            pass


@pytest.fixture
def sync_test_server():
    """Fixture for synchronous tests that need a running server."""
    runner = ServerRunner()
    runner.start()
    yield runner
    runner.stop()
