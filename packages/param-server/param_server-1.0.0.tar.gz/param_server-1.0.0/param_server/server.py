"""TCP Parameter Server implementation."""

import asyncio
import json
import logging
import signal
import sys
import argparse
from pathlib import Path
from typing import Any, Dict, Optional
from .store import ParameterStore


logger = logging.getLogger(__name__)


class ParameterServer:
    """TCP-based parameter server."""

    def __init__(self, host: str = "localhost", port: int = 8888):
        self.host = host
        self.port = port
        self.store = ParameterStore()
        self.server: Optional[asyncio.Server] = None
        self.clients: Dict[str, asyncio.StreamWriter] = {}

    async def start(self, config_file: Optional[str] = None) -> None:
        """Start the parameter server.

        Args:
            config_file: Optional YAML config file to load on startup
        """
        # Load initial configuration if provided
        if config_file:
            try:
                self.store.load_from_yaml(config_file)
                logger.info(f"Loaded configuration from {config_file}")
            except Exception as e:
                logger.error(f"Failed to load config file {config_file}: {e}")

        # Start the server
        self.server = await asyncio.start_server(self._handle_client, self.host, self.port)

        addr = self.server.sockets[0].getsockname()
        logger.info(f"Parameter server started on {addr[0]}:{addr[1]}")

        # Serve forever
        async with self.server:
            await self.server.serve_forever()

    async def stop(self) -> None:
        """Stop the parameter server."""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            logger.info("Parameter server stopped")

    async def _handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        """Handle incoming client connections."""
        client_addr = writer.get_extra_info("peername")
        client_id = f"{client_addr[0]}:{client_addr[1]}"

        logger.info(f"Client connected: {client_id}")
        self.clients[client_id] = writer

        try:
            while True:
                # Read message length (4 bytes)
                length_data = await reader.readexactly(4)
                message_length = int.from_bytes(length_data, byteorder="big")

                # Read the actual message
                message_data = await reader.readexactly(message_length)
                message = json.loads(message_data.decode("utf-8"))

                # Process the message
                response = await self._process_message(message)

                # Send response
                response_data = json.dumps(response).encode("utf-8")
                response_length = len(response_data).to_bytes(4, byteorder="big")

                writer.write(response_length)
                writer.write(response_data)
                await writer.drain()

        except asyncio.IncompleteReadError:
            logger.info(f"Client disconnected: {client_id}")

        except Exception as e:
            logger.error(f"Error handling client {client_id}: {e}", exc_info=True)

        finally:
            if client_id in self.clients:
                del self.clients[client_id]
            writer.close()
            try:
                await writer.wait_closed()
            except ConnectionResetError:
                logger.debug(f"Client {client_id} connection already reset")

    async def _process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming message from client."""
        try:
            command = message.get("command")
            path = message.get("path", "")

            if command == "get":
                try:
                    value = self.store.get(path)
                    return {"status": "success", "value": value}
                except KeyError:
                    return {"status": "error", "message": f"Parameter not found: {path}"}

            elif command == "set":
                value = message.get("value")
                try:
                    self.store.set(path, value)
                    return {"status": "success"}
                except (ValueError, TypeError) as e:
                    return {"status": "error", "message": str(e)}

            elif command == "delete":
                try:
                    self.store.delete(path)
                    # Notify other clients about the deletion
                    # await self._broadcast_deletion(path)
                    return {"status": "success"}
                except KeyError:
                    return {"status": "error", "message": f"Parameter not found: {path}"}

            elif command == "list":
                prefix = message.get("prefix", "")
                try:
                    params = self.store.list_params(prefix)
                    return {"status": "success", "parameters": params}
                except Exception as e:
                    return {"status": "error", "message": str(e)}

            elif command == "ping":
                return {"status": "success", "message": "pong"}

            else:
                return {"status": "error", "message": f"Unknown command: {command}"}

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {"status": "error", "message": "Internal server error"}

    async def _broadcast_change(self, path: str, value: Any) -> None:
        """Broadcast parameter change to all clients."""
        notification = {"type": "parameter_changed", "path": path, "value": value}
        await self._broadcast_notification(notification)

    async def _broadcast_deletion(self, path: str) -> None:
        """Broadcast parameter deletion to all clients."""
        notification = {"type": "parameter_deleted", "path": path}
        await self._broadcast_notification(notification)

    async def _broadcast_notification(self, notification: Dict[str, Any]) -> None:
        """Send notification to all connected clients."""
        if not self.clients:
            return

        message_data = json.dumps(notification).encode("utf-8")
        message_length = len(message_data).to_bytes(4, byteorder="big")

        # Send to all clients (fire and forget)
        disconnected_clients = []

        for client_id, writer in self.clients.items():
            try:
                writer.write(message_length)
                writer.write(message_data)
                await writer.drain()
            except Exception as e:
                logger.warning(f"Failed to send notification to {client_id}: {e}")
                disconnected_clients.append(client_id)

        # Clean up disconnected clients
        for client_id in disconnected_clients:
            if client_id in self.clients:
                del self.clients[client_id]


def setup_logging(level: str = "INFO") -> None:
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


async def main_async() -> None:
    """Main async function."""
    parser = argparse.ArgumentParser(description="Parameter Server")
    parser.add_argument("--host", default="localhost", help="Server host (default: localhost)")
    parser.add_argument("--port", type=int, default=8888, help="Server port (default: 8888)")
    parser.add_argument("--config", help="YAML configuration file to load on startup")
    parser.add_argument(
        "--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="Log level (default: INFO)"
    )

    args = parser.parse_args()

    setup_logging(args.log_level)

    server = ParameterServer(args.host, args.port)

    # Setup signal handlers for graceful shutdown
    loop = asyncio.get_event_loop()

    def signal_handler():
        logger.info("Received shutdown signal")
        asyncio.create_task(server.stop())

    for sig in [signal.SIGTERM, signal.SIGINT]:
        loop.add_signal_handler(sig, signal_handler)

    try:
        await server.start(args.config)

    except KeyboardInterrupt:
        logger.info("Server interrupted")

    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


def main() -> None:
    """Main entry point."""
    try:
        asyncio.run(main_async())

    except KeyboardInterrupt:
        logger.info("Server stopped")


if __name__ == "__main__":
    main()
