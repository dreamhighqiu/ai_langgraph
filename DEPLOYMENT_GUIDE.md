# 🚀 最终部署指南

## 📋 最终部署使用的文件

### 1. **docker-compose.yml** ✅ （必需）
**位置：** 项目根目录  
**用途：** Docker Compose 主配置文件，定义所有服务和依赖关系  
**状态：** 已配置完成，可直接使用

### 2. **anything-chat-rag/.env** ⚠️ （必需，需要创建）
**位置：** `anything-chat-rag/.env`  
**用途：** LightRAG 服务和 WebUI 的环境变量配置  
**创建方式：**
```bash
# 从示例文件创建
cp anything-chat-rag/env.example anything-chat-rag/.env
```

**必须配置的项：**
- `LLM_BINDING_API_KEY` - LLM API Key（必需）
- `VL_BINDING_API_KEY` - 视觉模型 API Key（如果使用多模态）
- `EMBEDDING_BINDING_API_KEY` - 嵌入模型 API Key（如果使用）

**容器内访问地址（已自动配置，无需修改）：**
- `MILVUS_URI=http://milvus:19530` - 会被 docker-compose.yml 覆盖
- `REDIS_HOST=redis` - 会被 docker-compose.yml 覆盖
- `REDIS_PASSWORD=redis123456` - 会被 docker-compose.yml 覆盖

### 3. **testing-agents-service/.env** ⚠️ （必需，需要创建）
**位置：** `testing-agents-service/.env`  
**用途：** LangGraph Agent 和 Frontend 的环境变量配置  
**创建方式：**
```bash
# 从示例文件创建
cp testing-agents-service/env.example testing-agents-service/.env
```

**必须配置的项：**
- `OPENAI_API_KEY` - OpenAI API Key（必需）
- `OPENAI_MODEL` - 模型名称（如：gpt-4o）
- `OPENAI_BASE_URL` - API 基础 URL

**容器内访问地址（已自动配置，无需修改）：**
- `MILVUS_URI=http://milvus:19530` - 会被 docker-compose.yml 覆盖
- `LIGHTRAG_BASE_URL=http://lightrag:9621` - 会被 docker-compose.yml 覆盖
- `REDIS_URI=redis://:redis123456@redis:6379/0` - 会被 docker-compose.yml 覆盖

**前端访问地址（浏览器访问）：**
- `NEXT_PUBLIC_LANGGRAPH_URL=http://localhost:2025` - 会被 docker-compose.yml 覆盖

---

## 🔧 部署步骤

### 步骤 1: 创建环境变量文件

```bash
# Windows PowerShell
Copy-Item anything-chat-rag\env.example anything-chat-rag\.env
Copy-Item testing-agents-service\env.example testing-agents-service\.env

# Linux/Mac
cp anything-chat-rag/env.example anything-chat-rag/.env
cp testing-agents-service/env.example testing-agents-service/.env
```

### 步骤 2: 配置 API Keys

编辑 `anything-chat-rag/.env`：
```bash
# 必须配置
LLM_BINDING_API_KEY=your-openai-api-key-here
VL_BINDING_API_KEY=your-openai-api-key-here
EMBEDDING_BINDING_API_KEY=your-api-key-here  # 如果使用 OpenAI 嵌入模型
```

编辑 `testing-agents-service/.env`：
```bash
# 必须配置
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4o  # 或你使用的模型
OPENAI_BASE_URL=https://api.openai.com/v1  # 或你的 API 地址
```

### 步骤 3: 启动服务

```bash
# 基础服务（推荐）
docker compose up -d

# 查看服务状态
docker compose ps

# 查看日志
docker compose logs -f
```

### 步骤 4: 验证服务

访问以下地址验证服务是否正常：

- **LightRAG WebUI**: http://localhost:5173
- **Frontend UI**: http://localhost:3200
- **LightRAG API 文档**: http://localhost:9621/docs
- **LangGraph API**: http://localhost:2025

---

## ⚠️ 重要注意事项

### 1. Redis 端口修改

您已将 Redis 宿主机端口改为 `6380:6379`，这意味着：
- ✅ **容器内访问**：仍然使用 `redis:6379`（不受影响）
- ✅ **宿主机访问**：使用 `localhost:6380`（不是 6379）

**影响：**
- 容器内服务间通信不受影响（使用服务名 `redis:6379`）
- 如果从宿主机连接 Redis，需要使用端口 `6380`

### 2. 环境变量优先级

`docker-compose.yml` 中的 `environment` 会覆盖 `.env` 文件中的配置。

**当前配置：**
- `docker-compose.yml` 自动设置容器内访问地址（使用服务名）
- `.env` 文件用于配置 API Keys 和其他业务配置

### 3. 容器内访问地址规则

**✅ 正确（容器内访问）：**
```bash
MILVUS_URI=http://milvus:19530
LIGHTRAG_BASE_URL=http://lightrag:9621
REDIS_HOST=redis
```

**❌ 错误（容器内无法访问）：**
```bash
MILVUS_URI=http://localhost:19530
LIGHTRAG_BASE_URL=http://localhost:9621
REDIS_HOST=localhost
```

### 4. 浏览器访问地址规则

**✅ 正确（浏览器访问）：**
```bash
NEXT_PUBLIC_LANGGRAPH_URL=http://localhost:2025
```

**❌ 错误（浏览器无法访问）：**
```bash
NEXT_PUBLIC_LANGGRAPH_URL=http://langgraph:2025
```

---

## 📊 服务端口映射

| 服务 | 容器内端口 | 宿主机端口 | 访问地址 |
|------|-----------|-----------|---------|
| Redis | 6379 | **6380** | localhost:6380 |
| Milvus | 19530 | 19530 | localhost:19530 |
| LightRAG | 9621 | 9621 | localhost:9621 |
| LightRAG WebUI | 5173 | 5173 | localhost:5173 |
| LangGraph | 2025 | 2025 | localhost:2025 |
| Frontend | 3200 | 3200 | localhost:3200 |

---

## 🔍 故障排查

### 检查服务状态
```bash
docker compose ps
```

### 查看服务日志
```bash
# 所有服务
docker compose logs -f

# 特定服务
docker compose logs -f lightrag
docker compose logs -f langgraph
docker compose logs -f frontend
```

### 检查环境变量
```bash
# 检查容器内的环境变量
docker compose exec lightrag env | grep REDIS
docker compose exec langgraph env | grep REDIS
docker compose exec frontend env | grep NEXT_PUBLIC
```

### 测试服务连接
```bash
# 测试 Redis 连接
docker compose exec lightrag python -c "import redis; r = redis.Redis(host='redis', port=6379, password='redis123456'); print('Redis连接成功' if r.ping() else 'Redis连接失败')"

# 测试 Milvus 连接
docker compose exec lightrag curl -f http://milvus:19530/healthz

# 测试 LightRAG API
curl http://localhost:9621/docs

# 测试 LangGraph API
curl http://localhost:2025/ok
```

---

## 📝 完整部署检查清单

- [ ] 已创建 `anything-chat-rag/.env` 文件
- [ ] 已创建 `testing-agents-service/.env` 文件
- [ ] 已配置 `LLM_BINDING_API_KEY`（在 `anything-chat-rag/.env`）
- [ ] 已配置 `OPENAI_API_KEY`（在 `testing-agents-service/.env`）
- [ ] 已确认 `docker-compose.yml` 存在且配置正确
- [ ] 已启动服务：`docker compose up -d`
- [ ] 已验证所有服务正常运行：`docker compose ps`
- [ ] 已测试前端访问：http://localhost:3200
- [ ] 已测试 LightRAG WebUI：http://localhost:5173

---

## 🎯 快速部署命令

```bash
# 一键部署（假设已配置好 .env 文件）
docker compose up -d && docker compose ps && echo "部署完成！访问 http://localhost:3200"
```

---

## 📚 相关文件说明

- **docker-compose.yml** - 主配置文件，定义所有服务
- **anything-chat-rag/env.example** - LightRAG 配置模板
- **testing-agents-service/env.example** - LangGraph 配置模板
- **env.docker.example** - Docker 部署说明文档

---

## 🆘 常见问题

### Q: 服务启动失败？
A: 检查日志：`docker compose logs [服务名]`，确认 API Keys 已正确配置。

### Q: 前端无法连接后端？
A: 确认 `NEXT_PUBLIC_LANGGRAPH_URL=http://localhost:2025`（浏览器访问地址）。

### Q: Redis 连接失败？
A: 容器内使用 `redis:6379`（服务名），不是 `localhost:6379`。

### Q: 如何修改端口？
A: 修改 `docker-compose.yml` 中的 `ports` 配置，注意容器内端口不变。

---

**最终部署文件总结：**
1. ✅ `docker-compose.yml` - 已配置完成
2. ⚠️ `anything-chat-rag/.env` - 需要从 `env.example` 创建并配置
3. ⚠️ `testing-agents-service/.env` - 需要从 `env.example` 创建并配置

