# 启动脚本快速参考卡片

## 🚀 常用命令

```bash
# 启动所有服务
./start_all.sh --all

# 停止所有服务
./start_all.sh --stop

# 查看服务状态
./start_all.sh --status

# 重启所有服务
./start_all.sh --restart

# 更新依赖并重启
./start_all.sh --update
```

## 📦 单个服务操作

```bash
# 启动单个服务
./start_all.sh lightrag      # LightRAG Server (9621)
./start_all.sh mcp           # MCP Server (8001)
./start_all.sh langgraph     # LangGraph Server (2025)
./start_all.sh agent-ui      # Agent UI (3200)

# 停止单个服务
./start_all.sh --stop lightrag
./start_all.sh --stop mcp
./start_all.sh --stop langgraph
./start_all.sh --stop agent-ui

# 重启单个服务
./start_all.sh --restart lightrag
./start_all.sh --restart mcp
./start_all.sh --restart langgraph
./start_all.sh --restart agent-ui
```

## 🌐 服务访问地址

| 服务 | 地址 | 说明 |
|------|------|------|
| LightRAG API | http://localhost:9621/docs | API 文档 |
| MCP Server | http://localhost:8001/sse | MCP 端点 |
| LangGraph API | http://localhost:2025/docs | API 文档 |
| LangGraph Studio | http://localhost:2025/ui | Studio UI |
| Agent UI | http://localhost:3200 | 前端界面 |

## 📋 日志查看

```bash
# 查看所有日志（实时）
tail -f logs/*.log

# 查看特定服务日志
tail -f logs/lightrag.log
tail -f logs/mcp.log
tail -f logs/langgraph.log
tail -f logs/agent_ui.log
```

## 🔧 故障排除

```bash
# 1. 检查状态
./start_all.sh --status

# 2. 查看日志
tail -n 50 logs/[service].log

# 3. 更新依赖
./start_all.sh --update

# 4. 完全重启
./start_all.sh --stop
./start_all.sh --all
```

## 📝 服务端口

| 服务 | 端口 | 固定端口 |
|------|------|---------|
| LightRAG Server | 9621 | ✅ |
| MCP Server | 8001 | ✅ |
| LangGraph Server | 2025 | ✅ |
| Agent UI | 3200 | ✅ |

**注意：** 所有服务使用固定端口，端口被占用时会自动清理。

## ⚡ 快速工作流

### 首次启动
```bash
./start_all.sh --all
```

### 日常使用
```bash
# 启动
./start_all.sh --all

# 停止
./start_all.sh --stop
```

### 开发调试
```bash
# 1. 停止所有
./start_all.sh --stop

# 2. 启动单个服务
./start_all.sh lightrag

# 3. 查看日志
tail -f logs/lightrag.log

# 4. 调试完成后启动所有
./start_all.sh --all
```

### 更新后重启
```bash
./start_all.sh --update
```

---

**详细文档：** 查看 `START_ALL_MANUAL.md`

