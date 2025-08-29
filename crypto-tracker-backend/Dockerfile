# Multi-stage Dockerfile for Flask Backend
FROM python:3.11-slim AS builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Create virtual environment and install dependencies
RUN python -m venv venv
RUN . venv/bin/activate && pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim AS production

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/venv venv/

# Copy application code
COPY . .

# Create necessary directories and set permissions
RUN mkdir -p instance && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD ./venv/bin/python -c "import requests; requests.get('http://localhost:5000/health', timeout=5)" || exit 1

# Start the application with better configuration
CMD ["./venv/bin/gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--timeout", "120", "--max-requests", "1000", "--max-requests-jitter", "100", "app:app"]