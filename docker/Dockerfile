# XFactor Bot - Automated Trading System
# https://gitlab-master.nvidia.com/cvanthin/000_trading

FROM python:3.11-slim

LABEL name="XFactor Bot"
LABEL version="0.1.0"
LABEL description="AI-Powered Automated Trading Bot"

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY pyproject.toml .

# Create directories
RUN mkdir -p logs data new_news/incoming new_news/processed new_news/failed

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose API port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

