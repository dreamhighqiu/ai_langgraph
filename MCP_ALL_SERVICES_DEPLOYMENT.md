# 所有 MCP 服务远程部署完整指南

## 📋 MCP 服务分类

### SSE 模式服务（独立容器）✅ 已配置

| 服务 | 端口 | 容器名 | 状态 |
|------|------|--------|------|
| rag-query-mcp | 8002 | rag-query-mcp | ✅ 已配置 |
| rag-anything-mcp | 8001 | rag-anything-mcp | ✅ 已配置 |
| pytest-mcp | 8004 | pytest-mcp | ✅ 已配置 |

### Stdio 模式服务（Agent 内部启动）✅ 已配置

| 服务 | 启动方式 | 位置 | 状态 |
|------|---------|------|------|
| automation_quality | node mcpServer.js | testing-agents-service/mcp/automation_quality/ | ✅ 已配置 |
| playwright | npx @playwright/mcp@latest | npm 包 | ✅ 已配置 |
| midscene | npx @midscene/web-bridge-mcp | npm 包 | ✅ 已配置 |

---

## 🚀 SSE 模式服务部署（独立容器）

### 已完成的配置

**docker-compose.yml 中已添加：**

```yaml
services:
  # RAG Query MCP Service
  rag-query-mcp:
    ports: ["8002:8002"]
    command: python -m mcp.rag_query.server --sse --port 8002
    
  # RAG Anything MCP Service
  rag-anything-mcp:
    ports: ["8001:8001"]
    command: python -m mcp.rag_anything.server --sse --port 8001
    
  # Pytest MCP Service
  pytest-mcp:
    ports: ["8004:8004"]
    command: python -m mcp.pytest_mcp.server --sse --port 8004
```

**启动方式：**
```bash
docker compose up -d rag-query-mcp rag-anything-mcp pytest-mcp
```

---

## 🔧 Stdio 模式服务部署（Agent 内部）

### 1. automation_quality

**配置位置：** `testing-agents-service/config/mcp_settings.py`

```python
automation_quality_enabled: bool = True
automation_quality_command: str = "node"
automation_quality_server_path: str = "mcp/automation_quality/mcpServer.js"
```

**启动方式：**
- 由 `MultiServerMCPClient` 在 Agent 初始化时自动启动
- 通过 stdio 与 Agent 通信

**Docker 部署要求：**
- ✅ Node.js 已安装（Dockerfile.backend 已更新）
- ✅ npm 依赖已安装（Dockerfile.backend 已更新）

### 2. playwright

**配置位置：** `testing-agents-service/config/mcp_settings.py`

```python
playwright_mcp_command: str = "npx"
playwright_mcp_args: list = ["-y", "@playwright/mcp@latest"]
```

**启动方式：**
- 由 `MultiServerMCPClient` 在 Agent 初始化时自动启动
- 通过 npx 自动下载并运行
- 通过 stdio 与 Agent 通信

**Docker 部署要求：**
- ✅ Node.js 和 npx 已安装（Dockerfile.backend 已更新）
- ✅ 首次运行时会自动下载包

### 3. midscene

**配置位置：** `testing-agents-service/config/mcp_settings.py`

```python
midscene_mcp_command: str = "npx"
midscene_mcp_args: list = ["-y", "@midscene/web-bridge-mcp"]
```

**启动方式：**
- 由 `MultiServerMCPClient` 在 Agent 初始化时自动启动
- 通过 npx 自动下载并运行
- 通过 stdio 与 Agent 通信

**Docker 部署要求：**
- ✅ Node.js 和 npx 已安装（Dockerfile.backend 已更新）
- ✅ 首次运行时会自动下载包

---

## 📊 服务启动流程对比

### SSE 模式服务启动流程

```
1. docker compose up -d
   ↓
2. Docker 启动独立容器
   ↓
3. 容器内运行 Python 模块
   ↓
4. 监听 HTTP 端口
   ↓
5. Agent 通过 HTTP 访问
```

### Stdio 模式服务启动流程

```
1. Agent 初始化
   ↓
2. MultiServerMCPClient 创建
   ↓
3. 根据配置启动子进程（node/npx）
   ↓
4. 通过 stdio 通信
   ↓
5. Agent 关闭时自动终止子进程
```

---

## 🐳 Dockerfile.backend 更新

### 已添加的配置

```dockerfile
# 1. 安装 Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs

# 2. 安装 automation_quality 依赖
WORKDIR /app/testing-agents-service/mcp/automation_quality
RUN if [ -f "package.json" ]; then npm install --production; fi
WORKDIR /app
```

---

## ✅ 部署检查清单

### SSE 模式服务

- [x] docker-compose.yml 中已定义服务
- [x] 服务依赖关系已配置
- [x] 健康检查已配置
- [x] 环境变量已配置

### Stdio 模式服务

- [x] Node.js 已在 Dockerfile 中安装
- [x] automation_quality 依赖已安装
- [x] npx 可用（Node.js 自带）
- [x] mcp_settings.py 配置正确

---

## 🔍 验证步骤

### 1. 检查 Node.js 环境

```bash
docker compose exec langgraph node --version
docker compose exec langgraph npm --version
docker compose exec langgraph npx --version
```

### 2. 检查 automation_quality

```bash
# 检查文件是否存在
docker compose exec langgraph ls -la /app/testing-agents-service/mcp/automation_quality/mcpServer.js

# 检查依赖是否安装
docker compose exec langgraph ls -la /app/testing-agents-service/mcp/automation_quality/node_modules

# 测试启动（应该显示帮助信息）
docker compose exec langgraph node /app/testing-agents-service/mcp/automation_quality/mcpServer.js --help
```

### 3. 检查 SSE 模式服务

```bash
# 检查服务状态
docker compose ps | grep mcp

# 测试连接
docker compose exec langgraph curl -f http://rag-query-mcp:8002/sse
docker compose exec langgraph curl -f http://rag-anything-mcp:8001/sse
docker compose exec langgraph curl -f http://pytest-mcp:8004/sse
```

### 4. 检查 Agent 日志

```bash
# 查看 Agent 启动日志，确认 MCP 工具加载成功
docker compose logs langgraph | grep -i "mcp\|automation\|playwright\|midscene"
```

---

## 📝 环境变量配置

### docker-compose.yml 中的环境变量

```yaml
langgraph:
  environment:
    # SSE 模式服务地址（容器内访问）
    - RAG_QUERY_MCP_URL=http://rag-query-mcp:8002/sse
    - RAG_ANYTHING_MCP_URL=http://rag-anything-mcp:8001/sse
    - PYTEST_MCP_URL=http://pytest-mcp:8004/sse
    
    # Stdio 模式服务环境变量（可选）
    - OUTPUT_DIR=/app/automation_reports
    - NODE_ENV=production
    - MIDSCENE_MODEL_BASE_URL=${MIDSCENE_MODEL_BASE_URL:-https://ark.cn-beijing.volces.com/api/v3}
    - MIDSCENE_MODEL_API_KEY=${MIDSCENE_MODEL_API_KEY:-}
```

---

## 🎯 总结

### SSE 模式服务（3个）

1. **rag-query-mcp** - 独立容器，端口 8002
2. **rag-anything-mcp** - 独立容器，端口 8001
3. **pytest-mcp** - 独立容器，端口 8004

**管理方式：**
- 通过 `docker compose` 管理
- 独立启动、停止、重启
- 可以单独查看日志

### Stdio 模式服务（3个）

1. **automation_quality** - Agent 子进程，Node.js
2. **playwright** - Agent 子进程，npx
3. **midscene** - Agent 子进程，npx

**管理方式：**
- 由 Agent 代码自动管理
- 随 Agent 启动/关闭
- 日志在 Agent 日志中

### 部署要求

- ✅ Node.js 已安装（Dockerfile.backend）
- ✅ automation_quality 依赖已安装（Dockerfile.backend）
- ✅ SSE 服务已在 docker-compose.yml 中配置
- ✅ 环境变量已配置

### 快速启动

```bash
# 启动所有服务（包括 SSE 和 stdio 模式）
docker compose up -d

# 查看所有服务状态
docker compose ps

# 查看日志
docker compose logs -f langgraph
```

---

## 🚀 所有服务已配置完成！

所有 MCP 服务（SSE 模式和 stdio 模式）的部署配置已完成，可以正常使用！

