# LightRAG Server Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv for faster package installation
RUN pip install --no-cache-dir uv

# Copy dependency files first for better caching
COPY requirements.txt ./
COPY pyproject.toml setup.py MANIFEST.in* ./

# Copy source code
COPY lightrag/ ./lightrag/
COPY raganything/ ./raganything/

# Install Python dependencies
RUN uv pip install --system -r requirements.txt || pip install -r requirements.txt

# Install the package in editable mode
RUN uv pip install --system -e . || pip install -e .

# Create directories
RUN mkdir -p /app/inputs /app/rag_storage

# Set environment
ENV PYTHONPATH=/app:$PYTHONPATH
ENV HOST=0.0.0.0
ENV PORT=9621

# Expose port
EXPOSE 9621

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:9621/docs || exit 1

# Default command - use lightrag-server CLI
CMD ["lightrag-server", "--host", "0.0.0.0", "--port", "9621"]

