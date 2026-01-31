# AI LangGraph 服务启动脚本使用手册

## 📖 目录

- [概述](#概述)
- [快速开始](#快速开始)
- [命令详解](#命令详解)
- [服务管理](#服务管理)
- [故障排除](#故障排除)
- [高级用法](#高级用法)

---

## 概述

`start_all.sh` 是一个跨平台（Windows/Linux/macOS）的统一服务启动脚本，用于管理 AI LangGraph 项目的所有服务。

### 支持的服务

| 服务名称 | 端口 | 描述 |
|---------|------|------|
| LightRAG Server | 9621 | RAG 知识图谱服务 |
| MCP Server | 8001 | Model Context Protocol 服务器 |
| LangGraph Server | 2025 | LangGraph API 服务器 |
| Agent UI | 3200 | 前端用户界面 |

### 功能特性

- ✅ **跨平台支持**：Windows (Git Bash)、Linux、macOS
- ✅ **自动依赖管理**：使用 `uv` 管理 Python 依赖
- ✅ **端口冲突处理**：自动检测并清理占用端口的进程
- ✅ **服务状态监控**：实时显示服务运行状态
- ✅ **日志管理**：所有服务日志统一管理
- ✅ **一键启动/停止**：支持批量操作

---

## 快速开始

### 前置要求

1. **安装 uv**（Python 包管理器）
   ```bash
   # Windows (PowerShell)
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   
   # Linux/macOS
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **安装 Node.js**（用于 Agent UI）
   - 推荐版本：Node.js 18+ 或 20+
   - 下载地址：https://nodejs.org/

3. **安装 Git Bash**（Windows 用户）
   - 下载地址：https://git-scm.com/downloads

### 首次启动

```bash
# 进入项目目录
cd /d/yunxia/ai_langgraph

# 启动所有服务
./start_all.sh --all
```

首次运行会自动：
- 创建 Python 虚拟环境
- 安装所有依赖
- 启动所有服务

---

## 命令详解

### 基本命令格式

```bash
./start_all.sh [选项] [服务名称]
```

### 主要选项

#### 1. `--all` 或 `-a`
启动所有服务

```bash
./start_all.sh --all
```

**功能：**
- 按顺序启动所有服务
- 自动检查端口占用并清理
- 显示每个服务的启动状态

**输出示例：**
```
================================================================
                      Starting Services
================================================================

[INFO] Starting LightRAG Server...
[OK] LightRAG Server started (PID: 1234, Port: 9621)
         API Docs: http://localhost:9621/docs

[INFO] Starting MCP Server...
[OK] MCP Server started (PID: 1235, Port: 8001)

...
```

#### 2. `--stop` 或 `-s`
停止所有服务

```bash
./start_all.sh --stop
```

**功能：**
- 停止所有运行中的服务
- 清理 PID 文件
- 释放所有端口

#### 3. `--status` 或 `-st`
查看服务状态

```bash
./start_all.sh --status
```

**输出示例：**
```
================================================================
                      Service Status
================================================================

  [*] LightRAG Server           RUNNING (Port: 9621)
  [*] MCP Server                RUNNING (Port: 8001)
  [ ] LangGraph Server          STOPPED (Port: 2025)
  [*] Agent UI                  RUNNING (Port: 3200)

================================================================
```

#### 4. `--restart` 或 `-r`
重启指定服务或所有服务

```bash
# 重启所有服务
./start_all.sh --restart

# 重启指定服务
./start_all.sh --restart lightrag
./start_all.sh --restart mcp
./start_all.sh --restart langgraph
./start_all.sh --restart agent-ui
```

#### 5. `--update` 或 `-u`
更新依赖并重启

```bash
./start_all.sh --update
```

**功能：**
- 强制更新所有 Python 依赖
- 重新安装 requirements.txt 中的包
- 重启所有服务

#### 6. `--help` 或 `-h`
显示帮助信息

```bash
./start_all.sh --help
```

---

## 服务管理

### 启动单个服务

```bash
# 启动 LightRAG Server
./start_all.sh lightrag

# 启动 MCP Server
./start_all.sh mcp

# 启动 LangGraph Server
./start_all.sh langgraph

# 启动 Agent UI
./start_all.sh agent-ui
```

### 停止单个服务

```bash
# 停止 LightRAG Server
./start_all.sh --stop lightrag

# 停止 MCP Server
./start_all.sh --stop mcp

# 停止 LangGraph Server
./start_all.sh --stop langgraph

# 停止 Agent UI
./start_all.sh --stop agent-ui
```

### 重启单个服务

```bash
# 重启 LightRAG Server
./start_all.sh --restart lightrag

# 重启 MCP Server
./start_all.sh --restart mcp

# 重启 LangGraph Server
./start_all.sh --restart langgraph

# 重启 Agent UI
./start_all.sh --restart agent-ui
```

---

## 服务访问地址

启动成功后，可以通过以下地址访问服务：

| 服务 | 地址 | 说明 |
|------|------|------|
| LightRAG API | http://localhost:9621/docs | Swagger API 文档 |
| MCP Server | http://localhost:8001/sse | MCP SSE 端点 |
| LangGraph API | http://localhost:2025/docs | LangGraph API 文档 |
| LangGraph Studio | http://localhost:2025/ui | LangGraph Studio UI |
| Agent UI | http://localhost:3200 | 前端用户界面 |

---

## 日志管理

### 日志文件位置

所有服务日志保存在 `logs/` 目录：

```
logs/
├── lightrag.log    # LightRAG Server 日志
├── mcp.log         # MCP Server 日志
├── langgraph.log   # LangGraph Server 日志
└── agent_ui.log    # Agent UI 日志
```

### 查看日志

```bash
# 查看所有日志（实时）
tail -f logs/*.log

# 查看特定服务日志
tail -f logs/lightrag.log
tail -f logs/mcp.log
tail -f logs/langgraph.log
tail -f logs/agent_ui.log

# 查看最近 100 行日志
tail -n 100 logs/lightrag.log
```

### Windows 用户（PowerShell）

```powershell
# 查看实时日志
Get-Content logs\lightrag.log -Wait -Tail 50

# 查看所有日志
Get-Content logs\*.log -Wait -Tail 50
```

---

## 故障排除

### 问题 1: 端口被占用

**症状：**
```
[!] Port 8001 is already in use (MCP Server)
```

**解决方案：**
脚本会自动尝试清理占用端口的进程。如果自动清理失败，可以手动清理：

**Windows:**
```powershell
# 查找占用端口的进程
netstat -ano | findstr :8001

# 终止进程（替换 PID 为实际进程 ID）
taskkill /F /PID <PID>
```

**Linux/macOS:**
```bash
# 查找占用端口的进程
lsof -ti:8001

# 终止进程
kill -9 $(lsof -ti:8001)
```

### 问题 2: 服务启动失败

**症状：**
```
[X] MCP Server failed to start, check log: logs/mcp.log
```

**解决方案：**
1. 查看日志文件获取详细错误信息
   ```bash
   tail -n 50 logs/mcp.log
   ```

2. 检查依赖是否安装
   ```bash
   ./start_all.sh --update
   ```

3. 检查虚拟环境
   ```bash
   # 重新创建虚拟环境
   rm -rf .venv
   ./start_all.sh --all
   ```

### 问题 3: 模块导入错误

**症状：**
```
ModuleNotFoundError: No module named 'xxx'
```

**解决方案：**
```bash
# 更新依赖
./start_all.sh --update

# 或手动安装
cd .venv
source bin/activate  # Windows: Scripts\activate
pip install -r ../requirements.txt
```

### 问题 4: 权限错误

**症状：**
```
Permission denied: ./start_all.sh
```

**解决方案：**
```bash
# 添加执行权限（Linux/macOS）
chmod +x start_all.sh

# Windows Git Bash 通常不需要此步骤
```

### 问题 5: uv 未安装

**症状：**
```
[X] uv is not installed!
```

**解决方案：**
```bash
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# 验证安装
uv --version
```

---

## 高级用法

### 自定义端口（不推荐）

如果需要修改服务端口，需要修改以下文件：

1. **修改 `start_all.sh`** 中的端口定义：
   ```bash
   # 在对应的服务启动函数中修改
   local port=8001  # 改为你想要的端口
   ```

2. **修改服务配置文件**：
   - LightRAG: `anything-chat-rag/.env`
   - MCP Server: `mcp-server/.env` 或配置
   - LangGraph: `testing-agents-service/testing-agents-service/.env`
   - Agent UI: `testing-deep-agents-ui/.env` 或环境变量

### 后台运行

脚本默认使用 `nohup` 在后台运行服务。如果需要在前台运行（用于调试），可以修改脚本或直接运行服务：

```bash
# 直接运行 LightRAG Server（前台）
cd anything-chat-rag
.venv/bin/python -m lightrag.api.lightrag_server
```

### 开发模式

对于开发调试，建议：

1. **使用单独的终端窗口**运行每个服务
2. **启用详细日志**：
   ```bash
   # 在 .env 文件中设置
   LOG_LEVEL=DEBUG
   VERBOSE=True
   ```

3. **使用热重载**（如果支持）：
   - Agent UI 使用 Next.js，支持热重载
   - LangGraph Server 使用 uvicorn，支持自动重载

### 生产环境部署

生产环境建议：

1. **使用进程管理器**（如 systemd、supervisor、PM2）
2. **配置反向代理**（如 Nginx）
3. **启用 HTTPS**
4. **配置日志轮转**
5. **设置资源限制**

示例 systemd 服务文件：

```ini
[Unit]
Description=AI LangGraph Services
After=network.target

[Service]
Type=forking
User=your-user
WorkingDirectory=/path/to/ai_langgraph
ExecStart=/path/to/ai_langgraph/start_all.sh --all
ExecStop=/path/to/ai_langgraph/start_all.sh --stop
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## 常用命令组合

### 完整重启流程

```bash
# 停止所有服务 → 更新依赖 → 启动所有服务
./start_all.sh --stop && ./start_all.sh --update && ./start_all.sh --all
```

### 检查并修复

```bash
# 检查状态 → 如果有问题则重启
./start_all.sh --status
./start_all.sh --restart
```

### 开发调试流程

```bash
# 1. 停止所有服务
./start_all.sh --stop

# 2. 启动单个服务进行调试
./start_all.sh lightrag

# 3. 在另一个终端查看日志
tail -f logs/lightrag.log

# 4. 调试完成后启动所有服务
./start_all.sh --all
```

---

## 环境变量

### Python 环境变量

脚本会自动设置以下环境变量：

- `PYTHONIOENCODING=utf-8` - 解决 Windows 编码问题
- `PYTHONPATH` - Python 模块搜索路径

### 服务特定环境变量

各服务的环境变量配置在对应的 `.env` 文件中：

- `anything-chat-rag/.env` - LightRAG 配置
- `mcp-server/.env` - MCP Server 配置
- `testing-agents-service/testing-agents-service/.env` - LangGraph 配置
- `testing-deep-agents-ui/.env` - Agent UI 配置（可选）

---

## 脚本内部机制

### 端口管理

1. **端口检查**：使用 `check_port()` 函数检测端口占用
2. **自动清理**：使用 `kill_port()` 函数清理占用端口的进程
3. **端口释放确认**：等待 2 秒并验证端口是否已释放

### 依赖管理

1. **依赖检查**：比较 `requirements.txt` 和 `.venv/.last_sync` 的时间戳
2. **自动更新**：如果 `requirements.txt` 更新，自动重新安装依赖
3. **强制更新**：使用 `--update` 标志强制更新

### 服务启动流程

1. 检查端口占用 → 清理（如需要）
2. 切换到服务目录
3. 设置环境变量
4. 后台启动服务（`nohup`）
5. 保存 PID 到 `pids/` 目录
6. 等待服务启动（最多 60-120 秒）
7. 验证端口是否监听

---

## 常见问题 FAQ

### Q: 为什么服务启动很慢？

A: 首次启动需要：
- 创建虚拟环境
- 安装依赖（可能需要几分钟）
- 初始化服务（LightRAG 需要初始化存储）

### Q: 如何查看服务是否真的在运行？

A: 使用以下命令：
```bash
# 查看状态
./start_all.sh --status

# 检查端口
netstat -an | grep :8001  # Windows
lsof -i :8001              # Linux/macOS

# 访问服务
curl http://localhost:8001/sse
```

### Q: 可以同时运行多个实例吗？

A: 不建议。每个服务使用固定端口，多个实例会冲突。如果需要多实例，需要：
1. 修改端口配置
2. 使用不同的工作空间（WORKSPACE 环境变量）

### Q: 如何备份服务数据？

A: 主要数据位置：
- LightRAG: `anything-chat-rag/rag_storage/`
- 日志: `logs/`
- 配置: 各服务的 `.env` 文件

### Q: Windows 上可以使用吗？

A: 可以。需要：
1. 安装 Git Bash
2. 在 Git Bash 中运行脚本
3. 确保已安装 uv 和 Node.js

---

## 更新日志

### v1.0.0 (当前版本)

- ✅ 跨平台支持（Windows/Linux/macOS）
- ✅ 自动端口冲突处理
- ✅ 依赖自动更新检查
- ✅ 服务状态监控
- ✅ 统一日志管理

---

## 技术支持

如遇到问题，请：

1. 查看日志文件：`logs/*.log`
2. 检查服务状态：`./start_all.sh --status`
3. 查看本文档的故障排除章节
4. 提交 Issue 到项目仓库

---

## 附录

### 服务端口列表

| 服务 | 端口 | 协议 | 说明 |
|------|------|------|------|
| LightRAG Server | 9621 | HTTP | REST API |
| MCP Server | 8001 | HTTP/SSE | MCP Protocol |
| LangGraph Server | 2025 | HTTP | LangGraph API |
| Agent UI | 3200 | HTTP | Next.js App |

### 目录结构

```
ai_langgraph/
├── start_all.sh              # 启动脚本
├── requirements.txt          # Python 依赖
├── pyproject.toml           # 项目配置
├── .venv/                   # Python 虚拟环境
├── logs/                    # 服务日志
├── pids/                    # 进程 ID 文件
├── anything-chat-rag/       # LightRAG 服务
├── mcp-server/             # MCP Server
├── testing-agents-service/  # LangGraph Server
└── testing-deep-agents-ui/  # Agent UI
```

---

**最后更新：** 2025-12-30  
**版本：** 1.0.0

