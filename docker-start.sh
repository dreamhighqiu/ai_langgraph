#!/bin/bash
# Docker Compose Startup Script

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  AI LangGraph Docker Deployment${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Warning: .env file not found${NC}"
    echo "Creating .env from env.docker.example..."
    if [ -f env.docker.example ]; then
        cp env.docker.example .env
        echo -e "${YELLOW}Please edit .env file and set OPENAI_API_KEY${NC}"
    else
        echo -e "${RED}Error: env.docker.example not found${NC}"
        exit 1
    fi
fi

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed${NC}"
    exit 1
fi

# Use docker compose (v2) if available, otherwise docker-compose (v1)
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

echo "Starting services..."
$COMPOSE_CMD up -d

echo ""
echo -e "${GREEN}Services started!${NC}"
echo ""
echo "Access URLs:"
echo "  Frontend UI:     http://localhost:3200"
echo "  LangGraph API:   http://localhost:2025"
echo "  API Docs:        http://localhost:2025/docs"
echo "  LangGraph Studio: http://localhost:2025/ui"
echo "  LightRAG API:    http://localhost:9621/docs"
echo "  Milvus UI:       http://localhost:3000"
echo "  MinIO Console:   http://localhost:9001"
echo ""
echo "View logs: docker-compose logs -f [service-name]"
echo "Stop all:  docker-compose down"

