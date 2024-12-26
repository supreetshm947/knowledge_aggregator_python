# Use slim image as base
FROM python:3.12-slim

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.2 \
    POETRY_VIRTUALENVS_IN_PROJECT=true

# Set working directory
WORKDIR /app

# Install dependencies
#RUN apt-get update && \
#    apt-get install -y --no-install-recommends \
#    build-essential \
#    curl && \
#    curl -sSL https://install.python-poetry.org | python3 && \
#    apt-get clean && \
#    rm -rf /var/lib/apt/lists/*

RUN pip install poetry

# Copy Poetry files
COPY pyproject.toml poetry.lock ./

# Install project dependencies
RUN poetry install --no-root --only main

# Copy application code
COPY app/ .

# Expose port
EXPOSE 8000

# Default command
CMD ["poetry", "run", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
