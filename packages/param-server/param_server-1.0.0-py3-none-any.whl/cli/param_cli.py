"""CLI interface for Parameter Server."""

import asyncio
import click
import json
import logging
import sys
from typing import Any
from param_server.client import AsyncParameterClient


def setup_logging(debug: bool = False) -> None:
    """Setup logging configuration."""
    level = logging.DEBUG if debug else logging.WARNING
    logging.basicConfig(level=level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


def format_value(value: Any) -> str:
    """Format parameter value for display."""
    if isinstance(value, str):
        return f'"{value}"'
    elif isinstance(value, bool):
        return str(value).lower()
    else:
        return str(value)


def parse_value(value_str: str) -> Any:
    """Parse string value to appropriate type."""
    # Try to parse as JSON first (handles strings, numbers, booleans)
    try:
        return json.loads(value_str)
    except json.JSONDecodeError:
        # If JSON parsing fails, treat as string
        return value_str


@click.group()
@click.option("--host", default="localhost", help="Parameter server host")
@click.option("--port", default=8888, type=int, help="Parameter server port")
@click.option("--timeout", default=5.0, type=float, help="Connection timeout")
@click.option("--debug", is_flag=True, help="Enable debug logging")
@click.pass_context
def cli(ctx, host, port, timeout, debug):
    """Parameter Server CLI tool."""
    setup_logging(debug)

    ctx.ensure_object(dict)
    ctx.obj["client_config"] = {"host": host, "port": port, "auto_reconnect": True}


async def async_get(client_config, path):
    """Async implementation of get command."""
    client = AsyncParameterClient(**client_config)
    try:
        async with client:
            value = await client.get(path)
            return f"{path} = {format_value(value)}"
    except ConnectionError as e:
        raise click.ClickException(f"Failed to connect to server: {e}")
    except KeyError as e:
        raise click.ClickException(str(e))
    except Exception as e:
        raise click.ClickException(str(e))


@cli.command()
@click.argument("path")
@click.pass_context
def get(ctx, path):
    """Get parameter value."""
    client_config = ctx.obj["client_config"]

    try:
        result = asyncio.run(async_get(client_config, path))
        click.echo(result)
    except click.ClickException as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


async def async_set(client_config, path, value):
    """Async implementation of set command."""
    client = AsyncParameterClient(**client_config)
    try:
        parsed_value = parse_value(value)
        async with client:
            await client.set(path, parsed_value)
            return f"Set {path} = {format_value(parsed_value)}"
    except ConnectionError as e:
        raise click.ClickException(f"Failed to connect to server: {e}")
    except ValueError as e:
        raise click.ClickException(str(e))
    except Exception as e:
        raise click.ClickException(str(e))


@cli.command()
@click.argument("path")
@click.argument("value")
@click.pass_context
def set(ctx, path, value):
    """Set parameter value."""
    client_config = ctx.obj["client_config"]

    try:
        result = asyncio.run(async_set(client_config, path, value))
        click.echo(result)
    except click.ClickException as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


async def async_delete(client_config, path):
    """Async implementation of delete command."""
    client = AsyncParameterClient(**client_config)
    try:
        async with client:
            await client.delete(path)
            return f"Deleted {path}"
    except ConnectionError as e:
        raise click.ClickException(f"Failed to connect to server: {e}")
    except KeyError as e:
        raise click.ClickException(str(e))
    except Exception as e:
        raise click.ClickException(str(e))


@cli.command()
@click.argument("path")
@click.pass_context
def delete(ctx, path):
    """Delete parameter."""
    client_config = ctx.obj["client_config"]

    try:
        result = asyncio.run(async_delete(client_config, path))
        click.echo(result)
    except click.ClickException as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


async def async_list(client_config, prefix, output_format):
    """Async implementation of list command."""
    client = AsyncParameterClient(**client_config)
    try:
        async with client:
            params = await client.list_params(prefix)

            if output_format == "json":
                # Get values for JSON output
                param_dict = {}
                for param in params:
                    try:
                        value = await client.get(param)
                        param_dict[param] = value
                    except Exception:
                        param_dict[param] = None

                return json.dumps(param_dict, indent=2)

            elif output_format == "tree":
                # Simple tree-like display
                if not params:
                    return "No parameters found"

                # Group by common prefixes
                tree_dict = {}
                for param in sorted(params):
                    parts = param.strip("/").split("/")
                    current = tree_dict
                    for part in parts[:-1]:
                        if part not in current:
                            current[part] = {}
                        current = current[part]

                    # Get the value for the leaf
                    try:
                        value = await client.get(param)
                        current[parts[-1]] = value
                    except Exception:
                        current[parts[-1]] = None

                def format_tree(data, indent=0):
                    lines = []
                    for key, value in data.items():
                        prefix_str = "  " * indent
                        if isinstance(value, dict):
                            lines.append(f"{prefix_str}{key}/")
                            lines.extend(format_tree(value, indent + 1))
                        else:
                            lines.append(f"{prefix_str}{key} = {format_value(value)}")
                    return lines

                return "\n".join(format_tree(tree_dict))

            else:  # list format
                if not params:
                    return "No parameters found"
                else:
                    return "\n".join(sorted(params))

    except ConnectionError as e:
        raise click.ClickException(f"Failed to connect to server: {e}")
    except Exception as e:
        raise click.ClickException(str(e))


@cli.command()
@click.option("--prefix", default="", help="Filter parameters by prefix")
@click.option(
    "--format", "output_format", default="list", type=click.Choice(["list", "tree", "json"]), help="Output format"
)
@click.pass_context
def list(ctx, prefix, output_format):
    """List parameters."""
    client_config = ctx.obj["client_config"]

    try:
        result = asyncio.run(async_list(client_config, prefix, output_format))
        click.echo(result)
    except click.ClickException as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


async def async_ping(client_config):
    """Async implementation of ping command."""
    client = AsyncParameterClient(**client_config)
    try:
        async with client:
            if await client.ping():
                return "Server is responding"
            else:
                raise click.ClickException("Server is not responding")
    except ConnectionError as e:
        raise click.ClickException(f"Failed to connect to server: {e}")


@cli.command()
@click.pass_context
def ping(ctx):
    """Ping the parameter server."""
    client_config = ctx.obj["client_config"]

    try:
        result = asyncio.run(async_ping(client_config))
        click.echo(result)
    except click.ClickException as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


async def async_watch(client_config, path):
    """Async implementation of watch command."""
    client = AsyncParameterClient(**client_config)
    try:
        async with client:
            click.echo(f"Watching {path} for changes (Ctrl+C to stop)...")
            last_value = None

            try:
                last_value = await client.get(path)
                click.echo(f"Initial value: {path} = {format_value(last_value)}")
            except KeyError:
                click.echo(f"Parameter {path} does not exist yet")

            while True:
                try:
                    current_value = await client.get(path)
                    if current_value != last_value:
                        click.echo(f"Changed: {path} = {format_value(current_value)}")
                        last_value = current_value
                except KeyError:
                    if last_value is not None:
                        click.echo(f"Deleted: {path}")
                        last_value = None

                await asyncio.sleep(0.01)  # Poll every 10ms

    except asyncio.CancelledError:
        click.echo("\nStopped watching")
    except ConnectionError as e:
        raise click.ClickException(f"Failed to connect to server: {e}")


@cli.command()
@click.argument("path")
@click.pass_context
def watch(ctx, path):
    """Watch parameter for changes (basic implementation)."""
    client_config = ctx.obj["client_config"]

    try:
        asyncio.run(async_watch(client_config, path))
    except KeyboardInterrupt:
        click.echo("\nStopped watching")
    except click.ClickException as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


def main():
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
