# AI LangGraph Monorepo

AI 智能平台，整合 RAG + Agent + 测试管理。

## 快速开始

```bash
i

# 初始化环境
./setup.sh

# 启动所有后端服务
./start_all.sh

# 启动所有服务（包含前端）
./start_all.sh --all

# 查看服务状态
./start_all.sh --status

# 停止服务
./start_all.sh --stop


# 重启 LightRAG（配置变更后）
./start_all.sh --restart lightrag
```

## 整合架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI Platform Frontend                          │
│                    (Vue + Vite, :5174)                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌───────────────────────────────────────────────────────────┐   │
│  │              AI Platform Backend (:9999)                   │   │
│  │    ┌─────────────────────────────────────────────────┐    │   │
│  │    │           Unified Services API                   │    │   │
│  │    │  /api/v1/services/knowledge    知识库管理        │    │   │
│  │    │  /api/v1/services/milvus       向量数据库        │    │   │
│  │    │  /api/v1/services/minio        对象存储          │    │   │
│  │    │  /api/v1/services/agents       智能体列表        │    │   │
│  │    │  /api/v1/services/threads      对话线程          │    │   │
│  │    │  /api/v1/services/chat         聊天交互          │    │   │
│  │    └─────────────────────────────────────────────────┘    │   │
│  │    + 用户管理 / 项目管理 / 测试用例 / 报告 / ...          │   │
│  └───────────────────────────────────────────────────────────┘   │
│                              │                                    │
│              ┌───────────────┴───────────────┐                   │
│              ▼                               ▼                    │
│  ┌──────────────────────┐     ┌──────────────────────────┐       │
│  │  LangGraph Server    │     │    LightRAG Server       │       │
│  │  (智能体后端, :2025) │     │    (知识库, :9621)       │       │
│  │  - K6 性能测试 Agent │     │    - 文档上传            │       │
│  │  - 知识库 Agent      │     │    - 语义搜索            │       │
│  │  - 中断审批          │     │    - 知识图谱            │       │
│  └──────────────────────┘     └──────────────────────────┘       │
│                              │                                    │
│              ┌───────────────┴───────────────┐                   │
│              ▼                               ▼                    │
│  ┌──────────────────────┐     ┌──────────────────────────┐       │
│  │       Milvus         │     │         MinIO            │       │
│  │    (向量数据库)      │     │      (对象存储)          │       │
│  └──────────────────────┘     └──────────────────────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

## 服务列表

| 服务                 | 端口 | 说明                                 |
| -------------------- | ---- | ------------------------------------ |
| LightRAG Server      | 9621 | 知识库服务（文档、搜索、知识图谱）   |
| MCP Server           | 8001 | RAG Anything（MCP 协议服务）         |
| LangGraph Server     | 2025 | 智能体后端（Agent 执行）             |
| AI Platform Backend  | 9999 | 主后端服务（统一 API、用户、项目等） |
| AI Platform Frontend | 5174 | 前端 UI                              |

## 统一服务 API

整合了所有存储和数据服务到 `AI Platform Backend`：

- **知识库**: `/api/v1/services/knowledge/*`
- **Milvus**: `/api/v1/services/milvus/*`
- **MinIO**: `/api/v1/services/minio/*`
- **智能体**: `/api/v1/services/agents`
- **对话**: `/api/v1/services/threads`, `/api/v1/services/chat`
- **健康检查**: `/api/v1/services/health`

API 文档: http://localhost:9999/docs

## 前端功能

- **智能体聊天**: `/langgraph-agent` - LangGraph 智能体对话
- **多智能体**: `/multi-agent-chat` - 多智能体协作
- **项目管理**: `/projects` - 知识库、MinIO 管理
- **测试管理**: `/testcases` - 测试用例管理
- **AI 生成**: `/ai-platform` - AI 生成测试用例

## 项目结构

```
ai_langGraph/
├── autogen_study/
│   ├── app/                           # 主后端服务
│   │   ├── api/v1/
│   │   │   ├── unified_services/      # 统一服务模块
│   │   │   │   ├── milvus_service.py  # Milvus 服务
│   │   │   │   ├── minio_service.py   # MinIO 服务
│   │   │   │   ├── knowledge_service.py # 知识库服务
│   │   │   │   ├── langgraph_service.py # LangGraph 服务
│   │   │   │   └── routes.py          # API 路由
│   │   │   └── ...                    # 其他模块
│   │   └── ...
│   └── web/                           # 前端 UI
│       └── src/
│           ├── pages/AgentChat/       # 智能体聊天页面
│           └── ...
├── anything-chat-rag/                 # LightRAG 知识库服务
├── testing-deep-agents-service/       # LangGraph 智能体服务
├── setup.sh                           # 环境初始化
├── start_all.sh                       # 服务启动脚本
└── pyproject.toml                     # Python 依赖
```

## 开发说明

### 后端开发

```bash
# 单独启动 AI Platform Backend
cd autogen_study
uv run python run.py --port 9999
```

### 前端开发

```bash
# 单独启动前端
cd autogen_study/web
npm install
npm run dev
```

### 添加新的智能体

1. 在 `testing-deep-agents-service/src/` 创建新 Agent
2. 在 `graph.json` 注册
3. 重启 LangGraph Server
