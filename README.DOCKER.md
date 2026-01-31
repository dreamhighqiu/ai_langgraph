# Docker Deployment Guide

Complete Docker Compose setup for AI LangGraph project.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- At least 8GB RAM
- 20GB free disk space

## Quick Start

1. **Copy environment file:**
   ```bash
   cp env.docker.example .env
   ```

2. **Edit `.env` file:**
   - Set `OPENAI_API_KEY` (required)
   - Adjust other settings as needed

3. **Start all services:**
   ```bash
   docker-compose up -d
   ```

4. **Check service status:**
   ```bash
   docker-compose ps
   ```

5. **View logs:**
   ```bash
   docker-compose logs -f langgraph
   ```

## Services

### Infrastructure Services

| Service | Port | Description |
|---------|------|-------------|
| Milvus | 19530 | Vector database |
| Attu | 3000 | Milvus Web UI |
| MySQL | 3306 | Relational database |
| PostgreSQL | 5432 | PostgreSQL with pgvector |
| Redis | 6379 | Cache and session store |
| MinIO | 9000/9001 | Object storage |
| Ollama | 11434 | Local LLM service |

### Application Services

| Service | Port | Description |
|---------|------|-------------|
| LightRAG | 9621 | RAG knowledge base server |
| LangGraph Server | 2025 | Main backend API |
| Frontend UI | 3200 | Next.js web interface |

## Access URLs

- **Frontend UI**: http://localhost:3200
- **LangGraph API**: http://localhost:2025
- **API Docs**: http://localhost:2025/docs
- **LangGraph Studio**: http://localhost:2025/ui
- **LightRAG API**: http://localhost:9621/docs
- **Milvus UI (Attu)**: http://localhost:3000
- **MinIO Console**: http://localhost:9001 (minioadmin/minioadmin123)

## Environment Variables

Key environment variables in `.env`:

- `OPENAI_API_KEY`: Required for LLM operations
- `OPENAI_MODEL`: OpenAI model name (default: gpt-4o)
- `OPENAI_BASE_URL`: OpenAI API endpoint
- `LIGHTRAG_BASE_URL`: LightRAG server URL
- `MILVUS_URI`: Milvus connection string
- `REDIS_PASSWORD`: Redis password

## Data Persistence

All data is persisted in Docker volumes:

- `lightrag_data`: RAG knowledge base
- `milvus_data`: Vector database data
- `mysql_data`: MySQL database
- `postgres_data`: PostgreSQL database
- `redis_data`: Redis persistence

## Development Mode

For development with hot reload:

1. Copy override example:
   ```bash
   cp docker-compose.override.yml.example docker-compose.override.yml
   ```

2. Start services:
   ```bash
   docker-compose up
   ```

## Troubleshooting

### Services not starting

1. Check logs:
   ```bash
   docker-compose logs [service-name]
   ```

2. Check resource usage:
   ```bash
   docker stats
   ```

3. Restart specific service:
   ```bash
   docker-compose restart [service-name]
   ```

### Port conflicts

Edit `docker-compose.yml` to change port mappings:
```yaml
ports:
  - "NEW_PORT:CONTAINER_PORT"
```

### Out of memory

Reduce services or increase Docker memory limit:
- Docker Desktop: Settings → Resources → Memory

## Building Images

Build all images:
```bash
docker-compose build
```

Build specific service:
```bash
docker-compose build langgraph
```

## Stopping Services

Stop all services:
```bash
docker-compose down
```

Stop and remove volumes (⚠️ deletes data):
```bash
docker-compose down -v
```

## Updating Services

1. Pull latest images:
   ```bash
   docker-compose pull
   ```

2. Rebuild and restart:
   ```bash
   docker-compose up -d --build
   ```

## Production Deployment

For production:

1. Use environment-specific `.env` file
2. Enable SSL/TLS (use reverse proxy like nginx)
3. Set strong passwords
4. Configure resource limits
5. Enable monitoring and logging
6. Use Docker secrets for sensitive data

## Support

For issues, check:
- Service logs: `docker-compose logs`
- Service health: `docker-compose ps`
- Docker system: `docker system df`

