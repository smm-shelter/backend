FROM python:3.12-alpine AS base

WORKDIR /backend

# README.md needed to hatchling build
COPY pyproject.toml uv.lock README.md .
RUN	pip install uv --no-cache
RUN	uv sync --no-cache

COPY . .

CMD ["uv", "run", "granian", "--interface", "asgi", "src/app.py", "--log", "--host", "0.0.0.0"]

