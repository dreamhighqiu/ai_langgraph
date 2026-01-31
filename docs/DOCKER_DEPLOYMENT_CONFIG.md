# Docker Compose 部署配置说明

## 🎯 核心问题：Host 应该使用容器名还是 localhost？

**答案取决于访问场景**：

### 📦 场景 1: 容器内部访问（容器 → 容器）

**使用容器名（服务名）**

当一个容器需要访问另一个容器的服务时，必须使用 **Docker 服务名**。

#### 示例：

```bash
# ✅ 正确：容器内访问
MILVUS_URI=http://milvus:19530          # 不是 localhost
REDIS_HOST=redis                        # 不是 localhost
EMBEDDING_HOST=http://ollama:11434      # 不是 localhost
LIGHTRAG_BASE_URL=http://lightrag:9621  # 不是 localhost

# MCP 服务（容器间访问）
RAG_QUERY_MCP_URL=http://rag-query-mcp:8002/sse
RAG_ANYTHING_MCP_URL=http://rag-anything-mcp:8001/sse
PYTEST_MCP_URL=http://pytest-mcp:8004/sse
```

#### 原因：
Docker Compose 会创建一个名为 `ai_network` 的内部网络，所有容器都连接到这个网络。容器之间通过 **服务名** 进行 DNS 解析和通信。

---

### 💻 场景 2: 宿主机访问（宿主机 → 容器）

**使用 localhost 或 127.0.0.1**

当您在宿主机（本地开发机器）上运行服务，需要访问 Docker 容器中的服务时，使用 `localhost`。

#### 示例：

```bash
# ✅ 正确：宿主机访问
MILVUS_URI=http://localhost:19530       # 宿主机访问
REDIS_HOST=localhost                    # 宿主机访问
EMBEDDING_HOST=http://localhost:11434   # 宿主机访问

# MCP 服务（宿主机访问）
RAG_QUERY_MCP_URL=http://127.0.0.1:8002/sse
RAG_ANYTHING_MCP_URL=http://localhost:8001/sse
PYTEST_MCP_URL=http://127.0.0.1:8004/sse
```

#### 原因：
Docker 通过端口映射（port mapping）将容器端口暴露到宿主机，例如 `19530:19530` 表示容器的 19530 端口映射到宿主机的 19530 端口。

---

## 📋 Docker Compose 配置解析

### 容器服务映射表

| 服务名 | 容器名 | 宿主机端口 | 容器内访问地址 | 宿主机访问地址 |
|--------|--------|-----------|---------------|---------------|
| **redis** | redis | 6380 → 6379 | `redis:6379` | `localhost:6380` |
| **milvus** | milvus-standalone | 19530 | `milvus:19530` | `localhost:19530` |
| **ollama** | ollama | 11434 | `ollama:11434` | `localhost:11434` |
| **lightrag** | lightrag-server | 9621 | `lightrag:9621` | `localhost:9621` |
| **postgres** | postgres | 5432 | `postgres:5432` | `localhost:5432` |
| **mysql** | mysql | 3307 → 3306 | `mysql:3306` | `localhost:3307` |
| **rag-query-mcp** | rag-query-mcp | 8002 | `rag-query-mcp:8002` | `localhost:8002` |
| **rag-anything-mcp** | rag-anything-mcp | 8001 | `rag-anything-mcp:8001` | `localhost:8001` |
| **pytest-mcp** | pytest-mcp | 8004 | `pytest-mcp:8004` | `localhost:8004` |
| **langgraph** | langgraph-server | 2025 | `langgraph:2025` | `localhost:2025` |

---

## 🔧 配置文件对比

### 1. Docker 环境配置（容器内运行）

**适用场景**: 所有服务都运行在 Docker 容器中

```bash
# testing-agents-service/.env (Docker 部署)

# ========== 基础设施服务（使用容器名） ==========
MILVUS_URI=http://milvus:19530
MILVUS_DB_NAME=lightrag

REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=redis123456
REDIS_URI=redis://:redis123456@redis:6379/0

# ========== Ollama Embedding（使用容器名） ==========
EMBEDDING_HOST=http://ollama:11434
EMBEDDING_MODEL=qwen3-embedding:0.6b

# ========== LightRAG（使用容器名） ==========
LIGHTRAG_BASE_URL=http://lightrag:9621

# ========== MCP 服务（使用容器名） ==========
RAG_QUERY_MCP_URL=http://rag-query-mcp:8002/sse
RAG_ANYTHING_MCP_URL=http://rag-anything-mcp:8001/sse
PYTEST_MCP_URL=http://pytest-mcp:8004/sse

# ========== 数据库（使用容器名） ==========
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

MYSQL_HOST=mysql
MYSQL_PORT=3306
```

### 2. 本地开发配置（宿主机运行）

**适用场景**: Agent 在宿主机运行，依赖服务在 Docker 中

```bash
# testing-agents-service/.env (本地开发)

# ========== 基础设施服务（使用 localhost） ==========
MILVUS_URI=http://localhost:19530
MILVUS_DB_NAME=lightrag

REDIS_HOST=localhost
REDIS_PORT=6380                          # ⚠️ 注意：宿主机映射的端口
REDIS_PASSWORD=redis123456
REDIS_URI=redis://:redis123456@localhost:6380/0

# ========== Ollama Embedding（使用 localhost） ==========
EMBEDDING_HOST=http://localhost:11434
EMBEDDING_MODEL=qwen3-embedding:0.6b

# ========== LightRAG（使用 localhost） ==========
LIGHTRAG_BASE_URL=http://localhost:9621

# ========== MCP 服务（使用 localhost） ==========
RAG_QUERY_MCP_URL=http://127.0.0.1:8002/sse
RAG_ANYTHING_MCP_URL=http://localhost:8001/sse
PYTEST_MCP_URL=http://127.0.0.1:8004/sse

# ========== 数据库（使用 localhost） ==========
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

MYSQL_HOST=localhost
MYSQL_PORT=3307                          # ⚠️ 注意：宿主机映射的端口
```

---

## 🎨 Docker Compose 配置重点

### 环境变量覆盖机制

在 `docker-compose.yml` 中，通过 `environment` 字段可以覆盖 `.env` 文件中的配置：

```yaml
langgraph:
  env_file:
    - ./testing-agents-service/.env    # 加载基础配置
  environment:
    # Docker 内部网络地址覆盖 (优先级高于 .env 文件)
    - REDIS_URI=redis://:redis123456@redis:6379/0
    - LIGHTRAG_BASE_URL=http://lightrag:9621
    - MILVUS_URI=http://milvus:19530
    - EMBEDDING_HOST=http://ollama:11434
    # MCP 服务地址（容器内访问，使用服务名）
    - RAG_QUERY_MCP_URL=http://rag-query-mcp:8002/sse
    - RAG_ANYTHING_MCP_URL=http://rag-anything-mcp:8001/sse
    - PYTEST_MCP_URL=http://pytest-mcp:8004/sse
```

**优先级**: `docker-compose.yml environment` > `.env 文件`

---

## 🚀 推荐的配置策略

### 策略 1: 双配置文件（推荐）⭐

维护两个配置文件：

```
testing-agents-service/
├── .env.docker       # Docker 部署配置（使用容器名）
├── .env.local        # 本地开发配置（使用 localhost）
└── .env              # 符号链接或复制自上面两者之一
```

**使用方式**:

```bash
# Docker 部署
cp .env.docker .env
docker-compose up -d

# 本地开发
cp .env.local .env
langgraph dev
```

### 策略 2: 环境变量动态判断

在代码中自动检测运行环境：

```python
import os
import socket

def is_running_in_docker():
    """检测是否在 Docker 容器中运行"""
    return os.path.exists('/.dockerenv')

def get_service_host(service_name: str, local_port: int = None) -> str:
    """
    根据运行环境返回正确的服务地址
    
    Args:
        service_name: Docker 服务名（如 'milvus', 'redis'）
        local_port: 宿主机端口（如果不同于容器端口）
    """
    if is_running_in_docker():
        # 容器内：使用服务名
        return service_name
    else:
        # 宿主机：使用 localhost
        return "localhost"

# 使用示例
milvus_host = get_service_host("milvus")
milvus_uri = f"http://{milvus_host}:19530"

redis_host = get_service_host("redis")
redis_port = 6380 if not is_running_in_docker() else 6379
```

### 策略 3: 仅依赖 docker-compose.yml（简单）

**适用于纯 Docker 部署**

`.env` 文件只配置 API Key 等敏感信息，所有服务地址在 `docker-compose.yml` 中硬编码：

```yaml
# docker-compose.yml
environment:
  - MILVUS_URI=http://milvus:19530
  - REDIS_HOST=redis
  - EMBEDDING_HOST=http://ollama:11434
```

**优点**: 配置集中，不易出错  
**缺点**: 不适合本地开发

---

## ⚠️ 常见错误和解决方案

### 错误 1: 容器内使用 localhost

❌ **错误配置**:
```bash
# 在 docker-compose.yml 或容器内的 .env
MILVUS_URI=http://localhost:19530
```

**现象**: 连接被拒绝（Connection refused）

**原因**: 容器内的 `localhost` 指向容器自己，不是宿主机或其他容器

✅ **正确配置**:
```bash
MILVUS_URI=http://milvus:19530
```

---

### 错误 2: 宿主机使用容器名

❌ **错误配置**:
```bash
# 在宿主机运行 langgraph dev 时
MILVUS_URI=http://milvus:19530
```

**现象**: DNS 解析失败（Name resolution failed）

**原因**: 宿主机无法解析 Docker 内部的服务名

✅ **正确配置**:
```bash
MILVUS_URI=http://localhost:19530
```

---

### 错误 3: 端口混淆

❌ **错误配置**:
```bash
# 宿主机访问 Redis（端口映射是 6380:6379）
REDIS_PORT=6379  # 错误！应该用宿主机端口
```

**现象**: 连接失败

✅ **正确配置**:
```bash
# 宿主机访问
REDIS_PORT=6380

# 容器内访问
REDIS_PORT=6379
```

**端口映射说明**:
- `6380:6379` 表示：宿主机端口 6380 → 容器端口 6379
- 宿主机访问使用 `localhost:6380`
- 容器内访问使用 `redis:6379`

---

## 🧪 测试连接

### 测试容器间连接

进入任意容器测试：

```bash
# 进入 langgraph 容器
docker exec -it langgraph-server sh

# 测试 Milvus 连接（使用服务名）
curl http://milvus:19530/healthz

# 测试 Redis 连接
redis-cli -h redis -p 6379 -a redis123456 ping

# 测试 Ollama 连接
curl http://ollama:11434/api/version
```

### 测试宿主机连接

在宿主机终端测试：

```bash
# 测试 Milvus 连接（使用 localhost）
curl http://localhost:19530/healthz

# 测试 Redis 连接（注意端口 6380）
redis-cli -h localhost -p 6380 -a redis123456 ping

# 测试 Ollama 连接
curl http://localhost:11434/api/version

# 测试 MCP 服务
curl http://localhost:8001/sse
curl http://localhost:8002/sse
curl http://localhost:8004/sse
```

---

## 📚 配置检查清单

### Docker 部署检查清单

- [ ] 所有服务地址使用容器名（不是 localhost）
- [ ] 端口使用容器内部端口（不是宿主机映射端口）
- [ ] `docker-compose.yml` 中 `environment` 覆盖了关键配置
- [ ] 所有容器连接到同一网络（`ai_network`）
- [ ] 依赖服务健康检查正常

### 本地开发检查清单

- [ ] 所有服务地址使用 localhost
- [ ] 端口使用宿主机映射端口（如 Redis 6380, MySQL 3307）
- [ ] Docker 容器已启动（`docker-compose ps`）
- [ ] 端口映射正确（`docker-compose port <service> <port>`）
- [ ] 防火墙未阻止端口

---

## 📖 总结

| 场景 | Host 配置 | 端口配置 | 示例 |
|------|----------|---------|------|
| **容器 → 容器** | 使用服务名 | 容器端口 | `http://milvus:19530` |
| **宿主机 → 容器** | 使用 localhost | 宿主机端口 | `http://localhost:19530` |
| **外网 → 容器** | 使用服务器 IP | 宿主机端口 | `http://192.168.1.100:19530` |

**记住**: Docker Compose 创建了一个虚拟网络，容器之间通过服务名通信，宿主机通过 localhost + 端口映射访问。

---

## 🔗 相关文档

- [env.example](./env.example) - 环境变量配置模板
- [ENV_CONFIG_GUIDE.md](./ENV_CONFIG_GUIDE.md) - 环境变量详细说明
- [docker-compose.yml](../docker-compose.yml) - Docker Compose 配置文件

