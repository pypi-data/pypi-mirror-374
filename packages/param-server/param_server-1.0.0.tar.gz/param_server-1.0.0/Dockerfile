FROM python:3.12-slim-trixie
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
# using trixie with ghcr because for preinstalled uv

# Set working directory
WORKDIR /app

# Prevents Python from writing .pyc files to disk - saves space
ENV PYTHONDONTWRITEBYTECODE=1 
# Ensures that Python output is sent straight to terminal (e.g. for logging) and not buffered
ENV PYTHONUNBUFFERED=1

# Copy project files first to leverage Docker cache
COPY pyproject.toml .
RUN uv sync

# Create directory for config files
RUN mkdir -p /app/config

# rest of the files goes here
COPY param_server/ ./param_server
COPY cli/ ./cli

# Expose the default port
EXPOSE 8888

# Default command using the virtual environment
CMD ["uv", "run", "-m", "param_server.server", "--host", "0.0.0.0", "--port", "8888"]
