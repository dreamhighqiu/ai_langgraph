# AI LangGraph Monorepo

RAG + Agent 服务栈，包含 LightRAG、MCP Server、Deep Agents Service。

## 快速开始

```bash
# 初始化环境
./setup.sh

# 启动所有服务
./start_all.sh

# 查看服务状态
./start_all.sh --status

# 停止服务
./start_all.sh --stop
```

## 服务列表

| 服务 | 端口 | 说明 |
|------|------|------|
| LightRAG | 9621 | 知识库服务 |
| MCP Server | 8001 | RAG Anything |
| Deep Agents | 2025 | Agent 服务 |
| Frontend | 3000 | 前端 UI |

## 项目结构

```
ai_langGraph/
├── anything-chat-rag/          # LightRAG 知识库服务
├── mcp-server/                 # MCP Server
├── testing-deep-agents-service/ # Deep Agents 服务
├── testing-deep-agents-ui/     # 前端 UI
├── setup.sh                    # 环境初始化脚本
├── start_all.sh                # 服务启动脚本
└── pyproject.toml              # 统一依赖配置
```
