# 所有服务访问地址汇总

## 🎨 前端界面

| 服务名称 | 访问地址 | 说明 | 端口 |
|---------|---------|------|------|
| **Agent UI** | http://localhost:3200 | LangGraph Agent 主界面 | 3200 |
| **LightRAG WebUI** ⭐ | http://localhost:5173 | RAG 知识库前端（新增） | 5173 |

## 🚀 后端 API

| 服务名称 | 访问地址 | 说明 | 端口 |
|---------|---------|------|------|
| LangGraph API | http://localhost:2025 | 主后端 API | 2025 |
| LangGraph API 文档 | http://localhost:2025/docs | Swagger 文档 | 2025 |
| LangGraph Studio | http://localhost:2025/ui | 开发工具 | 2025 |
| LightRAG API | http://localhost:9621 | RAG 知识库 API | 9621 |
| LightRAG API 文档 | http://localhost:9621/docs | RAG API 文档 | 9621 |

## 💾 数据库服务

| 服务名称 | 连接地址 | 用户/密码 | 说明 | 端口 |
|---------|---------|----------|------|------|
| **MySQL** | localhost:3306 | root / root123456 | 关系数据库 | 3306 |
| PostgreSQL | localhost:5432 | postgres / postgres123 | PostgreSQL 数据库 | 5432 |
| Redis | localhost:6379 | password: redis123456 | 缓存服务 | 6379 |
| Milvus | localhost:19530 | - | 向量数据库 | 19530 |

## 🛠️ 管理工具

| 服务名称 | 访问地址 | 用户/密码 | 说明 | 端口 |
|---------|---------|----------|------|------|
| MinIO 控制台 | http://localhost:9001 | minioadmin / minioadmin123 | 对象存储管理 | 9001 |
| Attu (可选) | http://localhost:3000 | - | Milvus Web UI | 3000 |

---

## 📋 完整服务列表

### Docker Compose 部署（8-10个服务）

**核心服务** (默认启动 8 个):
1. ✅ Redis (6379)
2. ✅ Etcd + MinIO (Milvus 依赖)
3. ✅ Milvus (19530)
4. ✅ MySQL (3306) ⭐ 新增
5. ✅ LightRAG Server (9621)
6. ✅ **LightRAG WebUI (5173)** ⭐ 新增
7. ✅ LangGraph Server (2025)
8. ✅ Frontend UI (3200)

**可选服务** (使用 `--profile full` 启动):
- PostgreSQL (5432)
- Attu (3000) - Milvus UI

### 本地 PowerShell 启动（3-4个服务）

**基础启动** (`.\start_all.ps1`):
1. ✅ LightRAG Server (9621)
2. ✅ LangGraph Server (2025)

**完整启动** (`.\start_all.ps1 -All`):
1. ✅ LightRAG Server (9621)
2. ✅ **LightRAG WebUI (5173)** ⭐ 新增
3. ✅ LangGraph Server (2025)
4. ✅ Agent UI (3200)

---

## 🎯 快速访问指南

### 开发和调试
```
1. LightRAG WebUI (RAG 管理):     http://localhost:5173
   - 上传文档
   - 查看知识图谱
   - 测试 RAG 查询

2. Agent UI (Agent 交互):         http://localhost:3200
   - API Agent
   - TestCase Agent
   - UI Agent

3. LangGraph Studio (调试):       http://localhost:2025/ui
   - 查看 Agent 工作流
   - 调试 LangGraph
```

### API 开发
```
1. LangGraph API:                 http://localhost:2025/docs
2. LightRAG API:                  http://localhost:9621/docs
```

### 数据库管理
```
1. MySQL:                         localhost:3306
   用户: root
   密码: root123456

2. MinIO Console:                 http://localhost:9001
   用户: minioadmin
   密码: minioadmin123
```

---

## 🚀 启动命令快速参考

### Docker 方式
```bash
# 启动所有核心服务（包含 LightRAG WebUI）
docker compose up -d

# 启动完整服务
docker compose --profile full up -d

# 查看日志
docker compose logs -f lightrag-webui
```

### 本地 PowerShell 方式
```powershell
# 启动后端（LightRAG + LangGraph）
.\start_all.ps1

# 启动所有服务（包含前端）
.\start_all.ps1 -All

# 查看状态
.\start_all.ps1 -Status

# 停止服务
.\start_all.ps1 -Stop
```

---

## 📊 服务架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        前端层                                 │
├─────────────────────────────────────────────────────────────┤
│  Agent UI (3200)          LightRAG WebUI (5173) ⭐           │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                       应用层                                  │
├─────────────────────────────────────────────────────────────┤
│  LangGraph (2025)         LightRAG (9621)                    │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                       数据层                                  │
├─────────────────────────────────────────────────────────────┤
│  MySQL (3306)  PostgreSQL (5432)  Redis (6379)  Milvus (19530) │
└─────────────────────────────────────────────────────────────┘
```

---

## ⚠️ 重要提示

1. **端口检查**: 确保以下端口未被占用
   - 必需: 2025, 3200, 5173, 6379, 9621, 19530, 3306
   - 可选: 5432, 3000, 9001

2. **LightRAG WebUI** ⭐: 
   - 这是 RAG 知识库的专用前端界面
   - 支持文档上传、知识图谱可视化、RAG 查询测试
   - 与 LightRAG API (9621) 配套使用

3. **Agent UI**: 
   - LangGraph Agent 的交互界面
   - 用于测试和使用各种 AI Agent

4. **数据持久化**: 
   - Docker volumes 保存所有数据
   - 删除容器不会丢失数据

---

## 🎉 新增功能

✅ **LightRAG WebUI (端口 5173)**
- 📁 文档管理：上传、删除、查看文档
- 🔍 RAG 查询测试：实时测试检索效果
- 🕸️ 知识图谱可视化：查看实体和关系
- ⚙️ 配置管理：调整 RAG 参数
- 🌐 多语言支持：中文、英文等

✅ **MySQL 数据库 (端口 3306)**
- 🗄️ 关系数据库
- 📊 用于结构化数据存储
- 🔗 支持未来扩展功能

访问 http://localhost:5173 立即体验 LightRAG WebUI！

