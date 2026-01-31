# Windows 本地开发快速启动指南

## 环境准备

### 1. 安装依赖
```powershell
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
.\.venv\Scripts\Activate.ps1

# 安装依赖
pip install -r requirements.txt

# 安装 LightRAG
pip install -e .\anything-chat-rag
```

### 2. 配置环境变量
`.env` 文件已创建，包含所有必要的配置。

## 启动服务

### 方式 1: 使用 PowerShell 脚本（推荐）

```powershell
# 启动后端服务（LightRAG + LangGraph）
.\start_all.ps1

# 启动所有服务（包括前端）
.\start_all.ps1 -All

# 查看服务状态
.\start_all.ps1 -Status

# 停止所有服务
.\start_all.ps1 -Stop
```

### 方式 2: 手动启动

#### 启动 LightRAG Server
```powershell
cd anything-chat-rag
python -m lightrag.api.lightrag_server
```
访问: http://localhost:9621/docs

#### 启动 LangGraph Server
```powershell
cd testing-agents-service
python start_server.py --port 2025
```
访问: http://localhost:2025/docs

#### 启动前端 UI
```powershell
cd testing-deep-agents-ui
npm install  # 首次运行
npm run dev
```
访问: http://localhost:3200

## Docker 部署

### 启动基础服务（推荐用于本地开发）
```powershell
# 启动核心服务：Redis, Milvus, LightRAG, LangGraph, Frontend
docker compose up -d

# 启动完整服务（包含 MySQL, PostgreSQL, Attu）
docker compose --profile full up -d

# 查看服务状态
docker compose ps

# 查看日志
docker compose logs -f langgraph

# 停止服务
docker compose down
```

### 访问地址

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端界面 | http://localhost:3200 | Agent UI |
| **LightRAG WebUI** | **http://localhost:5173** | **RAG 前端界面** |
| LangGraph API | http://localhost:2025 | 后端 API |
| API 文档 | http://localhost:2025/docs | Swagger |
| LangGraph Studio | http://localhost:2025/ui | 开发工具 |
| LightRAG API | http://localhost:9621/docs | RAG API |
| Milvus | localhost:19530 | 向量数据库 |
| MySQL | localhost:3306 | 关系数据库 |
| PostgreSQL | localhost:5432 | PostgreSQL |
| Redis | localhost:6379 | 缓存 |

## 数据库连接信息

### MySQL
```
Host: localhost
Port: 3306
User: root
Password: root123456
Database: ai_db
```

### PostgreSQL
```
Host: localhost
Port: 5432
User: postgres
Password: postgres123
Database: ai_db
```

## 故障排查

### 端口被占用
```powershell
# 查看端口占用
netstat -ano | findstr :2025

# 杀死进程
taskkill /F /PID <PID>
```

### 虚拟环境问题
```powershell
# 重新创建虚拟环境
Remove-Item -Recurse -Force .venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Docker 问题
```powershell
# 重启所有容器
docker compose restart

# 清理并重建
docker compose down -v
docker compose up -d --build
```

## 开发建议

### 本地开发推荐配置
1. **使用 PowerShell 脚本启动本地服务**（不需要 Docker）
   - 更快的启动速度
   - 更容易调试
   - 代码热重载

2. **使用 Docker 启动基础设施**
   ```powershell
   # 只启动 Redis, Milvus, MySQL
   docker compose up -d redis milvus mysql
   ```

3. **前端单独运行**
   ```powershell
   cd testing-deep-agents-ui
   npm run dev
   ```

### 生产部署推荐
```powershell
# 使用 Docker Compose 启动所有服务
docker compose --profile full up -d
```

## 常用命令

```powershell
# 检查 Python 环境
python --version

# 激活虚拟环境
.\.venv\Scripts\Activate.ps1

# 查看运行中的服务
.\start_all.ps1 -Status

# 查看日志
Get-Content logs\langgraph.log -Tail 50 -Wait

# Docker 服务管理
docker compose ps
docker compose logs -f
docker compose restart langgraph
```

## 注意事项

1. ⚠️ 确保端口未被占用：2025, 3200, 9621, 3306, 5432, 6379, 19530
2. ⚠️ 首次启动需要等待 2-3 分钟（Docker 镜像下载）
3. ⚠️ MySQL 和 PostgreSQL 数据持久化在 Docker volumes 中
4. ✅ OpenAI API Key 已配置在 `.env` 文件中
5. ✅ 所有密码都在 `.env` 文件中定义

## 下一步

1. 运行 `.\start_all.ps1` 启动本地服务
2. 或运行 `docker compose up -d` 启动 Docker 服务
3. 访问 http://localhost:3200 使用 Agent UI
4. 访问 http://localhost:2025/docs 查看 API 文档

