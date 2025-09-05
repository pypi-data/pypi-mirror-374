# Parameter Server

Dead simple TCP-based parameter storage that actually works. No cap.

## Quick Start

```bash
# Install dependencies
make install

# (For development)
make install-dev

# Run server
make server
```

## Python Usage

```python
from param_server.client import AsyncParameterClient

async with AsyncParameterClient() as client:
    await client.set("/camera/exposure", 100)
    value = await client.get("/camera/exposure")
    print(f"Exposure: {value}")
```

## Production Setup

### Docker Compose (recommended)

```bash
# Start container
docker compose up -d

# Server runs on localhost:8888
```

## Configuration

Drop a YAML file with your defaults:

```yaml
camera:
  exposure: 100
  gain: 1.5
  fps: 30

network:
  timeout: 5000
  retries: 3
```

Load it: `--config your-config.yml`

## CLI Commands

```bash
# Basic operations
param-cli set /path/to/param value
param-cli get /path/to/param
param-cli delete /path/to/param
param-cli list --prefix /camera

# Live monitoring
param-cli watch /camera/exposure

# Health check
param-cli ping
```

## Client Libraries

### Async 
```python
from param_server.client import AsyncParameterClient

client = AsyncParameterClient("localhost", 8888)
await client.connect()
await client.set("/test", 123)
value = await client.get("/test")
await client.disconnect()
```

## Features

- Persistent connections (low latency)
- Auto-reconnection (handles network issues)
- Type support: str, int, float, bool
- Concurrent operations
- Tree-like parameter paths
- JSON/tree CLI output formats
- Docker ready

## Port Configuration

Default port is 8888. Change it:

```bash
# Server
param-server --port 9999

# Client
param-cli --port 9999 ping

# Python
AsyncParameterClient("localhost", 9999)
```

## Troubleshooting

### Connection refused
```bash
# Check if server is running
param-cli ping

# Check port
netstat -tlnp | grep 8888
```

### Permission denied
```bash
# Use different port
param-server --port 9999
```

### Docker issues
```bash
# Check logs
docker compose logs param-server

# Rebuild
docker compose build --no-cache
```

That's it. Simple as.

@themladypan