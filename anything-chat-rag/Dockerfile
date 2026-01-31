# LightRAG Server Dockerfile
FROM python:3.13-slim

WORKDIR /app

# Configure Debian mirror for better network access (use Aliyun mirror in China)
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources 2>/dev/null || \
    sed -i 's|http://deb.debian.org|http://mirrors.aliyun.com|g' /etc/apt/sources.list 2>/dev/null || true

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Configure pip to use mirror and increase timeout
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip config set global.timeout 300 && \
    pip config set global.retries 5

# Install uv for faster package installation
RUN pip install --no-cache-dir --timeout=300 uv || \
    (pip install --no-cache-dir --timeout=300 -i https://mirrors.aliyun.com/pypi/simple/ uv)

# Copy dependency files first for better caching
COPY requirements.txt ./
COPY setup.py ./

# Copy source code
COPY lightrag/ ./lightrag/
COPY raganything/ ./raganything/

# Install Python dependencies (with retry and timeout)
# 使用 pip 直接安装，避免 uv 可能的卡顿问题
RUN pip install --timeout=300 --retries=5 -r requirements.txt || \
    (pip install --timeout=300 --retries=5 -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt) || \
    (echo "尝试使用 uv..." && uv pip install --system -r requirements.txt)

# Install the package in editable mode
# 优先使用 pip，避免 uv 可能的卡顿问题
RUN pip install --timeout=300 --retries=5 -e . || \
    (pip install --timeout=300 --retries=5 -i https://mirrors.aliyun.com/pypi/simple/ -e .) || \
    (echo "尝试使用 uv..." && uv pip install --system -e .)

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

