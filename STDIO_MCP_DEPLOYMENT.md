# Stdio 模式 MCP 服务远程部署指南

## 📋 概述

除了 SSE 模式的 MCP 服务（rag-query-mcp, rag-anything-mcp, pytest-mcp），还有 **stdio 模式**的 MCP 服务，它们在 Agent 内部通过子进程启动。

---

## 🔍 Stdio 模式 MCP 服务列表

### 1. automation_quality (stdio)
- **功能**：API/浏览器自动化测试
- **启动方式**：Node.js 子进程
- **命令**：`node mcpServer.js`
- **位置**：`testing-agents-service/mcp/automation_quality/`

### 2. playwright (stdio)
- **功能**：Playwright UI 测试
- **启动方式**：npx 子进程
- **命令**：`npx -y @playwright/mcp@latest`
- **位置**：通过 npx 从 npm 安装

### 3. midscene (stdio)
- **功能**：Midscene 视觉模型服务
- **启动方式**：npx 子进程
- **命令**：`npx -y @midscene/web-bridge-mcp`
- **位置**：通过 npx 从 npm 安装

---

## ⚙️ 配置方式

### mcp_settings.py 配置

```python
# automation_quality
automation_quality_mcp_enabled: bool = True
automation_quality_mcp_command: str = "node"
automation_quality_mcp_args: list = [
    "testing-agents-service/mcp/automation_quality/mcpServer.js"
]

# playwright
playwright_mcp_command: str = "npx"
playwright_mcp_args: list = ["-y", "@playwright/mcp@latest"]

# midscene
midscene_mcp_command: str = "npx"
midscene_mcp_args: list = ["-y", "@midscene/web-bridge-mcp"]
```

---

## 🚀 启动机制

### 在 Agent 代码中启动

这些 stdio 模式的 MCP 服务由 `MultiServerMCPClient` 在 Agent 运行时自动启动：

**示例：rest_api_agent.py**
```python
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient({
    "automation-quality": mcp_settings.get_automation_quality_config()
})
```

**启动流程：**
1. Agent 初始化时创建 `MultiServerMCPClient`
2. `MultiServerMCPClient` 根据配置启动子进程
3. 通过 stdio（标准输入/输出）与 MCP 服务通信
4. Agent 关闭时自动终止子进程

---

## 🐳 Docker 远程部署配置

### 1. 确保 Node.js 在容器中可用

**Dockerfile.backend 需要包含 Node.js：**

```dockerfile
# 安装 Node.js（如果还没有）
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*
```

### 2. 安装 automation_quality 依赖

**在 Dockerfile.backend 中添加：**

```dockerfile
# 安装 automation_quality MCP 服务依赖
COPY testing-agents-service/mcp/automation_quality/ ./testing-agents-service/mcp/automation_quality/
WORKDIR /app/testing-agents-service/mcp/automation_quality
RUN npm install --production
WORKDIR /app
```

### 3. 环境变量配置（可选）

**在 docker-compose.yml 的 langgraph 服务中：**

```yaml
langgraph:
  environment:
    # automation_quality 环境变量
    - OUTPUT_DIR=/app/automation_reports
    - NODE_ENV=production
    # midscene 环境变量
    - MIDSCENE_MODEL_BASE_URL=${MIDSCENE_MODEL_BASE_URL:-https://ark.cn-beijing.volces.com/api/v3}
    - MIDSCENE_MODEL_API_KEY=${MIDSCENE_MODEL_API_KEY:-}
    - MIDSCENE_MODEL_NAME=${MIDSCENE_MODEL_NAME:-doubao-seed-1-8-251215}
```

---

## 📊 服务启动对比

### SSE 模式服务（独立容器）

```
┌─────────────────┐
│  rag-query-mcp  │ ← 独立容器，HTTP 访问
└─────────────────┘

┌─────────────────┐
│ rag-anything-mcp│ ← 独立容器，HTTP 访问
└─────────────────┘
```

**特点：**
- ✅ 独立进程，易于监控
- ✅ 可以单独重启
- ✅ 需要网络访问

### Stdio 模式服务（Agent 内部启动）

```
┌─────────────────┐
│  LangGraph      │
│   Agent         │
│                 │
│  ┌───────────┐  │
│  │automation │  │ ← 子进程，stdio 通信
│  │_quality   │  │
│  └───────────┘  │
│                 │
│  ┌───────────┐  │
│  │playwright │  │ ← 子进程，stdio 通信
│  └───────────┘  │
└─────────────────┘
```

**特点：**
- ✅ 由 Agent 管理生命周期
- ✅ 无需网络配置
- ⚠️ 随 Agent 启动/关闭
- ⚠️ 难以单独监控

---

## 🔧 部署检查清单

### 1. Node.js 环境

```bash
# 在容器内检查
docker compose exec langgraph node --version
docker compose exec langgraph npm --version
```

**应该看到：**
- Node.js 版本（建议 v18+）
- npm 版本

### 2. automation_quality 依赖

```bash
# 检查依赖是否安装
docker compose exec langgraph ls -la /app/testing-agents-service/mcp/automation_quality/node_modules
```

### 3. 测试启动

```bash
# 测试 automation_quality 是否可以启动
docker compose exec langgraph node /app/testing-agents-service/mcp/automation_quality/mcpServer.js --help
```

### 4. 检查 Agent 日志

```bash
# 查看 Agent 启动日志，确认 MCP 服务加载成功
docker compose logs langgraph | grep -i "mcp\|automation\|playwright"
```

---

## ⚠️ 常见问题

### 问题 1: Node.js 未安装

**错误信息：**
```
/bin/sh: 1: node: not found
```

**解决方案：**
在 `Dockerfile.backend` 中添加 Node.js 安装步骤。

### 问题 2: automation_quality 依赖未安装

**错误信息：**
```
Cannot find module 'json-rpc-2.0'
```

**解决方案：**
在 `Dockerfile.backend` 中添加 npm install 步骤。

### 问题 3: npx 命令失败

**错误信息：**
```
npx: command not found
```

**解决方案：**
确保 Node.js 版本包含 npm/npx（Node.js 5.2+ 自带 npx）。

### 问题 4: 权限问题

**错误信息：**
```
EACCES: permission denied
```

**解决方案：**
确保容器内用户有执行权限，或使用 `--unsafe-perm` 安装 npm 包。

---

## 📝 完整 Dockerfile.backend 示例

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖和 Node.js
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# 安装 uv
RUN pip install --no-cache-dir uv

# ... Python 依赖安装 ...

# 安装 automation_quality MCP 服务依赖
COPY testing-agents-service/mcp/automation_quality/ ./testing-agents-service/mcp/automation_quality/
WORKDIR /app/testing-agents-service/mcp/automation_quality
RUN npm install --production
WORKDIR /app

# ... 其他配置 ...
```

---

## 🎯 总结

### Stdio 模式 MCP 服务特点

1. **automation_quality**
   - ✅ 需要 Node.js 环境
   - ✅ 需要安装 npm 依赖
   - ✅ 由 Agent 自动启动

2. **playwright** 和 **midscene**
   - ✅ 需要 Node.js 和 npx
   - ✅ 通过 npx 自动下载安装
   - ✅ 由 Agent 自动启动

### 部署要求

- ✅ Dockerfile 中安装 Node.js
- ✅ 安装 automation_quality 的 npm 依赖
- ✅ 确保 npx 可用（用于 playwright 和 midscene）
- ✅ 配置必要的环境变量

### 与 SSE 模式服务的区别

| 特性 | SSE 模式 | Stdio 模式 |
|------|---------|-----------|
| 启动方式 | 独立容器 | Agent 子进程 |
| 通信方式 | HTTP/SSE | stdio |
| 管理方式 | docker compose | Agent 代码 |
| 监控方式 | docker logs | Agent 日志 |
| 重启方式 | docker restart | Agent 重启 |

---

## 🚀 快速验证

```bash
# 1. 检查 Node.js
docker compose exec langgraph node --version

# 2. 检查 automation_quality
docker compose exec langgraph node /app/testing-agents-service/mcp/automation_quality/mcpServer.js --help

# 3. 检查 npx
docker compose exec langgraph npx --version

# 4. 查看 Agent 日志
docker compose logs langgraph | grep -i mcp
```

