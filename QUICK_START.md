# 🚀 快速开始指南

## 第一步：初始化配置

```bash
# Windows
.\init-env.ps1

# Linux/Mac
chmod +x init-env.sh && ./init-env.sh
```

这会创建两个 `.env` 文件：
- `anything-chat-rag/.env`
- `testing-agents-service/.env`

## 第二步：编辑配置文件

### 1. 编辑 `anything-chat-rag/.env`

```bash
# 如果使用 OpenAI
LLM_BINDING=openai
LLM_BINDING_HOST=https://api.openai.com/v1
LLM_BINDING_API_KEY=sk-your-openai-api-key

# 如果使用 Ollama（在 Docker 中）
LLM_BINDING=ollama
LLM_BINDING_HOST=http://ollama:11434

# Milvus 地址（Docker 部署用服务名）
MILVUS_URI=http://milvus:19530
```

### 2. 编辑 `testing-agents-service/.env`

```bash
# LLM 配置（同上）
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_MODEL=gpt-4o
OPENAI_BASE_URL=https://api.openai.com/v1

# 服务地址（Docker 部署用服务名）
LIGHTRAG_BASE_URL=http://lightrag:9621
MILVUS_URI=http://milvus:19530
REDIS_URI=redis://:redis123456@redis:6379/0

# 前端访问地址（浏览器用 localhost）
NEXT_PUBLIC_LANGGRAPH_URL=http://localhost:2025
```

## 第三步：启动服务

```bash
# 基础服务（推荐）
docker compose up -d

# 包含 Ollama（本地 LLM）
docker compose --profile ollama up -d

# 完整服务（包含 Attu、PostgreSQL、MySQL）
docker compose --profile full up -d
```

## 第四步：访问服务

启动后，在浏览器中访问：

| 服务 | 地址 | 说明 |
|------|------|------|
| **LightRAG WebUI** | http://localhost:5173 | 知识库管理 |
| **Agent Frontend** | http://localhost:3200 | AI Agent 界面 |
| **LightRAG API 文档** | http://localhost:9621/docs | API 文档 |

## 检查服务状态

```bash
# 查看所有服务状态
docker compose ps

# 查看日志
docker compose logs -f lightrag
docker compose logs -f langgraph

# 停止服务
docker compose down

# 停止并删除数据
docker compose down -v
```

## 常见问题

### Q: 服务启动失败？
```bash
# 查看详细日志
docker compose logs [服务名]

# 检查端口占用
netstat -ano | findstr :9621  # Windows
lsof -i :9621                 # Linux/Mac
```

### Q: 无法连接到 Milvus？
确保 `.env` 中使用服务名：`MILVUS_URI=http://milvus:19530`

### Q: 前端无法访问后端？
确保 `NEXT_PUBLIC_LANGGRAPH_URL=http://localhost:2025`（不是 `http://langgraph:2025`）

## 详细文档

- 📖 [完整访问指南](DOCKER_ACCESS_GUIDE.md)
- ⚙️ [配置说明](env.docker.example)

