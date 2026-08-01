# syntax=docker/dockerfile:1
# NewsMill application image (shared by Monitor and Worker services).

# ---- Build stage ----
# Use the official Python 3.12 slim image as the base.
FROM python:3.12-slim AS builder

# Metadata for the resulting image.
LABEL maintainer="NewsMill"

# Install UV - the package manager used by the project.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV \
    # Do not generate .pyc files.
    PYTHONDONTWRITEBYTECODE=1 \
    # Force output to be unbuffered so logs appear immediately.
    PYTHONUNBUFFERED=1 \
    # Install packages into a dedicated virtual environment.
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    # Use system Python for the created virtual environment.
    UV_PYTHON_INSTALL_DIR=/opt/uv-python \
    # Make the venv's python/pip available on PATH in the builder stage.
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Copy dependency manifests first to leverage Docker layer caching.
COPY pyproject.toml uv.lock README.md ./

# Install production dependencies only (skip the dev dependency group).
# --no-install-project avoids building the project before its source is copied.
RUN uv sync --frozen --no-dev --no-install-project

# Copy the application source code and configuration files.
COPY src/ ./src/
COPY newsfeeds.yaml ./

# Install the project itself now that the source is available.
RUN uv sync --frozen --no-dev

# Download the Russian SpaCy NER model used by the Worker service.
# Done in the builder stage where uv is available; the model installs into
# /opt/venv and is copied to the runtime stage with the venv.
RUN python -m spacy download ru_core_news_md

# ---- Runtime stage ----
FROM python:3.12-slim AS runtime

# Install curl for health checks (used by the compose healthcheck).
RUN apt-get update \
    && apt-get install --no-install-recommends -y curl \
    && rm -rf /var/lib/apt/lists/*

ENV \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Copy the pre-built virtual environment and app code from the builder stage.
COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /app/src /app/src
COPY --from=builder /app/newsfeeds.yaml /app/newsfeeds.yaml

# Default command runs the Monitor service (overridden for Worker in compose).
CMD ["uvicorn", "newsmill.monitor.app:app", "--host", "0.0.0.0", "--port", "8000"]