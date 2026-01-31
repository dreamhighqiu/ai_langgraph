# Docker Compose 优化说明

## 变更内容

### 移除的服务

1. **Ollama** (端口 11434)
   - 原因: 使用远程 OpenAI API，不需要本地 LLM
   - 节省: ~4GB RAM

2. **MySQL** (端口 3306)
   - 原因: 与 PostgreSQL 功能重复，LangGraph 使用 SQLite
   - 节省: ~500MB RAM

3. **MCP 服务器** (端口 8001, 8002, 8004)
   - 原因: 简化架构，Agent 直接调用 LightRAG API
   - 节省: ~300MB RAM x 3

### 保留的核心服务

#### 必需服务 (7个)
1. **Redis** (6379) - 缓存和会话存储
2. **Milvus** (19530) - 向量数据库
3. **Etcd** (2379) - Milvus 依赖
4. **MinIO** (9000/9001) - Milvus 对象存储
5. **LightRAG** (9621) - RAG 知识库服务
6. **LangGraph** (2025) - 主后端 API
7. **Frontend** (3200) - Web UI

#### 可选服务 (使用 profiles)
1. **PostgreSQL** (5432) - 高级功能数据库
   ```bash
   docker compose --profile full up -d
   ```

2. **Attu** (3000) - Milvus Web UI
   ```bash
   docker compose --profile full up -d
   ```

## 启动方式

### 默认启动（推荐）
```bash
# 最小配置，启动核心服务
docker compose up -d
```

### 完整启动
```bash
# 包含所有可选服务
docker compose --profile full up -d
```

### 部分启动
```bash
# 只启动基础设施
docker compose up -d redis milvus etcd minio

# 只启动应用服务
docker compose up -d lightrag langgraph frontend
```

## 资源要求

### 最小配置
- RAM: 4-6GB
- CPU: 2 核心
- 磁盘: 10GB

### 推荐配置
- RAM: 8GB
- CPU: 4 核心
- 磁盘: 20GB

### 完整配置（包含可选服务）
- RAM: 10-12GB
- CPU: 4-8 核心
- 磁盘: 30GB

## 环境变量

必需设置：
```env
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o
OPENAI_BASE_URL=https://us.api.openai.com/v1
```

## 验证部署

```bash
# 检查服务状态
docker compose ps

# 查看日志
docker compose logs -f langgraph

# 健康检查
curl http://localhost:2025/ok
curl http://localhost:9621/docs
curl http://localhost:3200
```

## 故障排查

### 服务无法启动
```bash
# 查看特定服务日志
docker compose logs [service-name]

# 重启服务
docker compose restart [service-name]
```

### 端口冲突
编辑 `docker-compose.yml` 修改端口映射：
```yaml
ports:
  - "NEW_PORT:CONTAINER_PORT"
```

### 内存不足
1. 停止可选服务
2. 增加 Docker 内存限制
3. 使用最小配置启动

## 优化效果

| 指标 | 优化前 | 优化后 | 改善 |
|------|--------|--------|------|
| 服务数量 | 13 | 7-9 | -40% |
| 内存占用 | ~10GB | ~6GB | -40% |
| 启动时间 | ~5 分钟 | ~3 分钟 | -40% |
| 复杂度 | 高 | 中 | ↓↓ |

