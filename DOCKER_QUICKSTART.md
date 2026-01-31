# Docker 快速启动指南

## 配置已完成 ✓

项目已配置使用 **OpenAI GPT-4o** 模型，已优化服务架构。

## 服务架构（优化版）

### 基础设施 (5个)
- Milvus + Etcd + MinIO - 向量数据库
- Redis - 缓存
- PostgreSQL - 数据库（可选，使用 `--profile full`）

### 应用服务 (3个)
- **LightRAG Server** (9621) - RAG 知识库
- **LangGraph Server** (2025) - 主后端 API
- **Frontend UI** (3200) - Next.js 前端

### 已移除服务
- ❌ Ollama - 使用远程 OpenAI API
- ❌ MySQL - 功能与 PostgreSQL 重复
- ❌ MCP Servers - 简化架构

## 快速启动

### Windows:

```powershell
# 1. 复制环境变量文件
Copy-Item env.docker.example .env

# 2. 启动所有服务（最小配置）
docker compose up -d

# 3. 或启动完整配置（包含可选服务）
docker compose --profile full up -d

# 4. 查看服务状态
docker compose ps

# 5. 查看日志
docker compose logs -f langgraph
```

### Linux/Mac:

```bash
# 1. 复制环境变量文件
cp env.docker.example .env

# 2. 启动所有服务（最小配置）
docker-compose up -d

# 3. 或启动完整配置（包含可选服务）
docker-compose --profile full up -d

# 4. 查看服务状态
docker-compose ps

# 5. 查看日志
docker-compose logs -f langgraph
```

## 访问地址

| 服务 | URL | 说明 |
|------|-----|------|
| 前端界面 | http://localhost:3200 | 主界面 |
| **LightRAG WebUI** | **http://localhost:5173** | **RAG 前端界面（新增）** |
| LangGraph API | http://localhost:2025 | 后端 API |
| API 文档 | http://localhost:2025/docs | Swagger 文档 |
| LangGraph Studio | http://localhost:2025/ui | 开发界面 |
| LightRAG API | http://localhost:9621/docs | RAG API 文档 |
| Milvus | 19530 | 向量数据库端口 |
| MySQL | 3306 | MySQL 数据库 |
| MinIO 控制台 | http://localhost:9001 | 对象存储管理 |
| Attu (可选) | http://localhost:3000 | Milvus UI（需要 --profile full） |

## 配置信息

API 密钥已配置在 `env.docker.example`:
- **OpenAI API Key**: 已设置
- **模型**: gpt-4o
- **API 端点**: https://us.api.openai.com/v1

## 常用命令

```bash
# 停止所有服务
docker compose down

# 重启服务
docker compose restart langgraph

# 查看资源使用
docker stats

# 清理（⚠️ 会删除数据）
docker compose down -v
```

## 服务启动顺序

1. 基础设施服务先启动（Redis, Milvus + Etcd + MinIO）
2. LightRAG Server 启动（依赖 Milvus 和 Redis）
3. LangGraph Server 启动（依赖 LightRAG）
4. Frontend UI 启动（依赖 LangGraph）

整个启动过程约需 **2-3 分钟**。

## 验证部署

```bash
# 等待所有服务启动
sleep 180

# 检查健康状态
curl http://localhost:2025/ok
curl http://localhost:9621/docs

# 访问前端
open http://localhost:3200  # Mac
start http://localhost:3200  # Windows
```

## 远程访问配置

### LightRAG WebUI 自动地址检测

前端已配置**自动检测服务器地址**，无需手动配置：

```bash
# 本地访问
http://localhost:5173
# 前端自动使用: http://localhost:9621

# 远程访问（服务器 IP: 192.168.1.100）
http://192.168.1.100:5173
# 前端自动使用: http://192.168.1.100:9621 ✅

# 域名访问
http://your-domain.com:5173
# 前端自动使用: http://your-domain.com:9621 ✅
```

### 手动指定 API 地址（可选）

如果需要指定特殊的 API 地址，编辑 `.env`：

```bash
# .env
LIGHTRAG_API_URL=http://your-server-ip:9621
```

**注意**: 大多数情况下不需要设置此变量，留空即可自动检测。

### 防火墙配置

确保开放必要端口：

```bash
# Ubuntu/Debian
sudo ufw allow 2024    # Frontend
sudo ufw allow 2025    # LangGraph API
sudo ufw allow 5173    # LightRAG WebUI
sudo ufw allow 9621    # LightRAG API

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=2024/tcp
sudo firewall-cmd --permanent --add-port=2025/tcp
sudo firewall-cmd --permanent --add-port=5173/tcp
sudo firewall-cmd --permanent --add-port=9621/tcp
sudo firewall-cmd --reload
```

## 故障排查

### 服务未启动
```bash
# 查看特定服务日志
docker compose logs langgraph
docker compose logs lightrag

# 重启服务
docker compose restart langgraph
```

### 端口冲突
如果端口被占用，编辑 `docker-compose.yml` 修改端口映射。

### 资源不足
确保 Docker 分配了至少 6GB RAM（最小配置）或 8GB RAM（推荐配置）。

### 服务无法连接
```bash
# 检查网络连接
docker compose exec langgraph ping lightrag

# 检查环境变量
docker compose exec langgraph env | grep OPENAI
```

## 数据持久化

所有数据存储在 Docker volumes:
- `redis_data` - Redis 缓存
- `milvus_data` - 向量数据
- `lightrag_data` - RAG 知识库
- `langgraph_data` - LangGraph 数据
- `postgres_data` - PostgreSQL 数据（可选）

删除容器不会丢失数据，除非使用 `docker compose down -v`。

## 资源要求

### 最小配置（默认启动）
- RAM: 6GB
- CPU: 2 核心
- 磁盘: 10GB
- 服务数: 7

### 完整配置（--profile full）
- RAM: 8-10GB
- CPU: 4 核心
- 磁盘: 20GB
- 服务数: 9

## 优化亮点

相比优化前：
- ✅ 服务数量减少 40%（13 → 7）
- ✅ 内存占用减少 40%（~10GB → ~6GB）
- ✅ 启动时间减少 40%（~5分钟 → ~3分钟）
- ✅ 架构更简洁，维护更容易

## 注意事项

- ⚠️ OpenAI API Key 已包含在配置中
- ✓ 已移除所有 MCP 服务器
- ✓ 使用 OpenAI GPT-4o 模型
- ✓ 支持中文和英文
- ✓ 已优化资源占用

## 更多信息

- 完整文档: `README.DOCKER.md`
- 优化报告: `OPTIMIZATION_REPORT.md`
- Docker 优化说明: `DOCKER_OPTIMIZATION.md`

