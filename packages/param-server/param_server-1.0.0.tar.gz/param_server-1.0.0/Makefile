.PHONY : install install-dev test clean build docker-build docker-run stop server client

install:
	uv tool install -e .
	uv tool update-shell

# Testing
test:
	uv sync --extra dev
	uv run pytest tests/ -v

# Cleanup
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Build
build: clean
	uv build

# Docker operations
docker-build:
	docker build -f Dockerfile -t param-server:latest .

docker-run:
	docker-compose -f docker-compose.yml up -d param-server

docker-dev:
	docker-compose -f docker-compose.yml up -d param-server-dev

stop:
	docker-compose -f docker-compose.yml down

# Local development
server:
	uv run python -m param_server.server --config examples/config/params.yml --log-level DEBUG

server-bg:
	uv run python -m param_server.server --config examples/config/params.yml --log-level INFO &


