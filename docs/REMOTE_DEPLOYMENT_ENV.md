# 远程部署环境变量读取指南

## 🎯 概述

本文档详细说明在远程 Docker 部署时，环境变量是如何被读取和使用的。

---

## 📋 环境变量加载机制

### 1. 加载优先级（从高到低）

```
1️⃣ docker-compose.yml environment 字段（最高优先级）
   ↓
2️⃣ docker-compose.yml env_file 引用的文件
   ↓
3️⃣ 系统环境变量（宿主机 export）
   ↓
4️⃣ Pydantic Settings 默认值（代码中定义）
```

### 2. 具体示例

```yaml
# docker-compose.yml
langgraph:
  env_file:
    - ./testing-agents-service/.env          # ← 第2优先级
  environment:
    - MILVUS_URI=http://milvus:19530         # ← 第1优先级（会覆盖 .env）
    - REDIS_URI=redis://:redis123456@redis:6379/0
```

**结果**: 即使 `.env` 文件中配置了 `MILVUS_URI=http://localhost:19530`，容器内最终使用的是 `http://milvus:19530`

---

## 🔧 Docker Compose 环境变量读取流程

### 流程图

```
┌─────────────────────────────────────────────┐
│  1. docker-compose.yml 解析                  │
│     - 读取 env_file 字段指定的文件           │
│     - 读取 environment 字段的变量            │
└────────────────┬────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────┐
│  2. 容器启动                                 │
│     - 将环境变量注入容器环境                 │
│     - environment 覆盖 env_file 中的同名变量 │
└────────────────┬────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────┐
│  3. Python 应用启动                          │
│     - start_server.py 执行                  │
│     - 调用 load_dotenv() 加载 .env          │
│     - 但容器注入的环境变量优先级更高         │
└────────────────┬────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────┐
│  4. Pydantic Settings 初始化                │
│     - 读取环境变量                           │
│     - 如未设置，使用默认值                   │
└─────────────────────────────────────────────┘
```

---

## 📁 配置文件结构

### 远程部署的文件布局

```
ai_langgraph/
├── docker-compose.yml                    # ← Docker 编排文件
├── anything-chat-rag/
│   └── .env                              # ← LightRAG 服务配置
└── testing-agents-service/
    ├── .env                              # ← 主配置文件（需要创建）
    ├── env.example                       # ← 配置模板
    ├── start_server.py                   # ← 服务启动脚本
    ├── config/
    │   ├── settings.py                   # ← Pydantic Settings
    │   ├── llm_config.py                 # ← LLM 配置管理
    │   └── mcp_settings.py               # ← MCP 配置管理
    └── agents/
        ├── ui_java/agent.py              # ← Agent 实现
        └── ...
```

---

## 🚀 远程部署步骤

### 步骤 1: 准备配置文件

#### 方法 A: 使用模板创建（推荐）

```bash
# 在远程服务器上
cd /path/to/ai_langgraph/testing-agents-service

# 复制模板
cp env.example .env

# 编辑配置文件
vim .env
```

#### 方法 B: 直接上传配置文件

```bash
# 在本地准备好 .env 文件，然后上传
scp .env user@remote:/path/to/ai_langgraph/testing-agents-service/
```

### 步骤 2: 配置环境变量

**重要**: 远程 Docker 部署时，`.env` 文件只需配置：

1. **敏感信息**（必需）
   ```bash
   OPENAI_API_KEY=sk-proj-your-key...
   OPENAI_MODEL=gpt-5.2
   OPENAI_BASE_URL=https://us.api.openai.com/v1
   
   DEEPSEEK_API_KEY=sk-your-deepseek-key
   DOUBAO_API_KEY=your-doubao-key
   ```

2. **服务地址会被 docker-compose.yml 自动覆盖**
   ```bash
   # ⚠️ 这些在 Docker 部署时会被覆盖，可以不用手动修改
   # docker-compose.yml 会自动设置为容器名
   MILVUS_URI=http://localhost:19530        # 会被覆盖为 http://milvus:19530
   REDIS_HOST=localhost                     # 会被覆盖为 redis
   EMBEDDING_HOST=http://localhost:11434    # 会被覆盖为 http://ollama:11434
   ```

### 步骤 3: 启动服务

```bash
cd /path/to/ai_langgraph

# 启动所有服务（基础 + LangGraph）
docker-compose up -d

# 或启动包含 Ollama 的完整服务
docker-compose --profile ollama up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f langgraph
```

---

## 🔍 环境变量读取详解

### 1. docker-compose.yml 中的配置

```yaml
langgraph:
  env_file:
    - ./testing-agents-service/.env    # ← 加载 .env 文件
  environment:
    # Docker 内部网络地址覆盖（优先级高于 .env）
    - LANGGRAPH_PORT=2025
    - LANGGRAPH_HOST=0.0.0.0
    - REDIS_URI=redis://:redis123456@redis:6379/0          # ← 覆盖
    - LIGHTRAG_BASE_URL=http://lightrag:9621               # ← 覆盖
    - MILVUS_URI=http://milvus:19530                       # ← 覆盖
    - MILVUS_DB_NAME=lightrag
    - LIGHTRAG_VECTOR_STORAGE=MilvusVectorDBStorage
    - EMBEDDING_HOST=http://ollama:11434                   # ← 覆盖
    # MCP 服务地址（容器内访问，使用服务名）
    - RAG_QUERY_MCP_URL=http://rag-query-mcp:8002/sse      # ← 覆盖
    - RAG_ANYTHING_MCP_URL=http://rag-anything-mcp:8001/sse # ← 覆盖
    - PYTEST_MCP_URL=http://pytest-mcp:8004/sse            # ← 覆盖
```

### 2. start_server.py 中的环境变量读取

```python
# start_server.py (第 42-50 行)
def setup_environment(port: int) -> None:
    # ...
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        try:
            from dotenv import load_dotenv
            
            # override=False 表示不覆盖已存在的环境变量
            # Docker 注入的环境变量优先级更高
            load_dotenv(env_file, override=False)  # ← 关键：不覆盖已有变量
            print("[OK] Loaded environment from .env")
        except ImportError:
            print("[WARN] python-dotenv not installed, skipping .env file")
```

**关键点**: `override=False` 确保 Docker 注入的环境变量（来自 `docker-compose.yml`）不会被 `.env` 文件覆盖。

### 3. Pydantic Settings 中的读取

```python
# config/settings.py
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",                    # ← 指定 .env 文件
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",                     # ← 忽略未定义的环境变量
    )
    
    # 字段定义
    openai_api_key: Optional[str] = None    # ← 从环境变量 OPENAI_API_KEY 读取
    openai_model: str = "gpt-4o"            # ← 默认值
```

**优先级**: 环境变量 > `.env` 文件 > 默认值

---

## 📊 环境变量传递示意图

### Docker 部署场景

```
┌─────────────────────────────────────────────────────┐
│  宿主机                                              │
│                                                     │
│  1. docker-compose.yml                             │
│     env_file: ./testing-agents-service/.env        │
│     environment:                                    │
│       - MILVUS_URI=http://milvus:19530             │
│       - OPENAI_API_KEY=${OPENAI_API_KEY}           │
│                                                     │
│  2. testing-agents-service/.env                    │
│     OPENAI_API_KEY=sk-proj-xxx                     │
│     MILVUS_URI=http://localhost:19530  ← 会被覆盖   │
└──────────────────┬──────────────────────────────────┘
                   │ docker-compose up
                   ↓
┌─────────────────────────────────────────────────────┐
│  容器内 (langgraph-server)                          │
│                                                     │
│  容器环境变量（已注入）:                             │
│  ✅ OPENAI_API_KEY=sk-proj-xxx    (来自 .env)      │
│  ✅ MILVUS_URI=http://milvus:19530 (来自 environment)│
│  ✅ REDIS_URI=redis://:redis123456@redis:6379/0    │
│                                                     │
│  ↓ 应用启动                                         │
│                                                     │
│  3. start_server.py                                │
│     load_dotenv(override=False)  ← 不覆盖已有变量   │
│                                                     │
│  4. config/settings.py                             │
│     读取环境变量 OPENAI_API_KEY                     │
│     读取环境变量 MILVUS_URI                         │
│                                                     │
│  ✅ 最终使用的值:                                   │
│     OPENAI_API_KEY=sk-proj-xxx                     │
│     MILVUS_URI=http://milvus:19530  ← Docker 注入的 │
└─────────────────────────────────────────────────────┘
```

---

## 🎯 最佳实践

### 1. 远程部署配置策略

#### ✅ 推荐做法

**`.env` 文件只配置敏感信息**:

```bash
# testing-agents-service/.env (远程部署)

# ========== 敏感信息（必需） ==========
OPENAI_API_KEY=sk-proj-your-actual-key
OPENAI_MODEL=gpt-5.2
OPENAI_BASE_URL=https://us.api.openai.com/v1

DEEPSEEK_API_KEY=sk-your-deepseek-key
DOUBAO_API_KEY=your-doubao-key

# ========== 服务地址（可选，会被 docker-compose.yml 覆盖） ==========
# 以下配置在 Docker 部署时会被自动覆盖为容器名
# 保留这些配置是为了本地开发时使用
MILVUS_URI=http://localhost:19530
REDIS_HOST=localhost
EMBEDDING_HOST=http://localhost:11434
```

**优点**:
- `.env` 文件保持简洁
- 服务地址由 `docker-compose.yml` 统一管理
- 便于维护和版本控制

#### ❌ 不推荐做法

在 `.env` 文件中手动配置所有容器名:

```bash
# ❌ 不推荐：在 .env 中手动配置容器名
MILVUS_URI=http://milvus:19530
REDIS_HOST=redis
# ...
```

**缺点**:
- 需要维护两份配置（.env 和 docker-compose.yml）
- 容易出错
- 不适合本地开发

### 2. 环境变量验证

#### 远程服务器上验证环境变量

```bash
# 进入容器
docker exec -it langgraph-server sh

# 查看环境变量
env | grep -E "OPENAI|MILVUS|REDIS|EMBEDDING"

# 验证服务连接
python3 -c "
from config.settings import settings
from config.llm_config import get_llm_info

print('Settings loaded:')
print(f'OpenAI API Key: {\"✅ Set\" if settings.openai_api_key else \"❌ Not set\"}')
print(f'OpenAI Model: {settings.openai_model}')
print(f'OpenAI Base URL: {settings.openai_base_url}')

llm_info = get_llm_info()
print(f'\nLLM Info:')
print(f'Provider: {llm_info[\"provider\"]}')
print(f'Model: {llm_info[\"model\"]}')
print(f'API Key Configured: {llm_info[\"api_key_configured\"]}')
"
```

### 3. 配置文件安全

#### 保护敏感信息

```bash
# 在服务器上设置文件权限
chmod 600 testing-agents-service/.env
chown root:root testing-agents-service/.env

# 或使用 Docker secrets (推荐生产环境)
docker secret create openai_api_key ./openai_key.txt
```

#### 使用环境变量而不是文件

```bash
# 方式 1: 在 docker-compose.yml 中使用宿主机环境变量
langgraph:
  environment:
    - OPENAI_API_KEY=${OPENAI_API_KEY}  # ← 从宿主机环境变量读取

# 方式 2: 启动时传入
OPENAI_API_KEY=sk-proj-xxx docker-compose up -d
```

---

## 🧪 测试环境变量配置

### 测试脚本

创建 `test_env.py`:

```python
#!/usr/bin/env python3
"""测试环境变量配置"""

import os
from config.settings import settings
from config.llm_config import get_llm_info

def test_env_vars():
    print("=" * 60)
    print("环境变量测试")
    print("=" * 60)
    
    # 测试关键环境变量
    tests = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "OPENAI_MODEL": os.getenv("OPENAI_MODEL"),
        "MILVUS_URI": os.getenv("MILVUS_URI"),
        "REDIS_URI": os.getenv("REDIS_URI"),
        "EMBEDDING_HOST": os.getenv("EMBEDDING_HOST"),
        "RAG_ANYTHING_MCP_URL": os.getenv("RAG_ANYTHING_MCP_URL"),
    }
    
    print("\n直接读取环境变量:")
    for key, value in tests.items():
        status = "✅" if value else "❌"
        print(f"{status} {key}: {value[:20] + '...' if value and len(value) > 20 else value}")
    
    print("\n通过 Pydantic Settings 读取:")
    print(f"✅ openai_api_key: {settings.openai_api_key[:20] + '...' if settings.openai_api_key else '❌ Not set'}")
    print(f"✅ openai_model: {settings.openai_model}")
    
    print("\n通过 LLM Config 读取:")
    llm_info = get_llm_info()
    print(f"Provider: {llm_info['provider']}")
    print(f"Model: {llm_info['model']}")
    print(f"API Key Configured: {'✅' if llm_info['api_key_configured'] else '❌'}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_env_vars()
```

### 运行测试

```bash
# 在容器内运行
docker exec -it langgraph-server python3 testing-agents-service/test_env.py

# 或在宿主机运行
cd testing-agents-service
python test_env.py
```

---

## 🔧 故障排除

### 问题 1: 环境变量未生效

**症状**: 修改了 `.env` 文件，但容器内仍使用旧值

**原因**: Docker Compose 不会自动重新加载环境变量

**解决方案**:

```bash
# 方法 1: 重启容器
docker-compose restart langgraph

# 方法 2: 重新创建容器
docker-compose up -d --force-recreate langgraph

# 方法 3: 完全重启
docker-compose down
docker-compose up -d
```

### 问题 2: 服务连接失败

**症状**: `Connection refused` 或 `Name resolution failed`

**诊断**:

```bash
# 检查容器内的环境变量
docker exec langgraph-server env | grep URI

# 应该看到容器名，而不是 localhost
# ✅ MILVUS_URI=http://milvus:19530
# ❌ MILVUS_URI=http://localhost:19530
```

**解决方案**: 确保 `docker-compose.yml` 中的 `environment` 字段正确配置了容器名

### 问题 3: API Key 未读取

**症状**: `AuthenticationError: Invalid API key`

**诊断**:

```bash
# 检查 .env 文件是否存在
ls -la testing-agents-service/.env

# 检查环境变量是否加载
docker exec langgraph-server printenv | grep OPENAI_API_KEY

# 检查配置验证
docker exec langgraph-server python3 -m config.validate_config
```

**解决方案**:

1. 确保 `.env` 文件存在且有正确的值
2. 检查 `docker-compose.yml` 中 `env_file` 路径正确
3. 重启容器加载新配置

---

## 📚 相关文档

- [DOCKER_DEPLOYMENT_CONFIG.md](./DOCKER_DEPLOYMENT_CONFIG.md) - Docker 部署配置详解
- [ENV_CONFIG_GUIDE.md](./ENV_CONFIG_GUIDE.md) - 环境变量完整指南
- [CONFIG_SUMMARY.md](./CONFIG_SUMMARY.md) - 配置总结
- [env.example](./env.example) - 配置模板

---

## 📝 快速参考

### 远程部署检查清单

- [ ] 创建 `testing-agents-service/.env` 文件
- [ ] 配置必需的 API Keys（OPENAI_API_KEY, DEEPSEEK_API_KEY 等）
- [ ] 确认 `docker-compose.yml` 中 `env_file` 路径正确
- [ ] 确认 `docker-compose.yml` 中 `environment` 配置使用容器名
- [ ] 启动服务: `docker-compose up -d`
- [ ] 验证环境变量: `docker exec langgraph-server env | grep OPENAI`
- [ ] 测试服务: `curl http://localhost:2025/ok`
- [ ] 运行配置验证: `docker exec langgraph-server python3 -m config.validate_config`

### 环境变量优先级总结

```
最高  ←  docker-compose.yml environment
  ↑
  |    docker-compose.yml env_file (.env)
  ↑
  |    系统环境变量 (export)
  ↑
最低  ←  代码默认值 (Pydantic Settings)
```

---

**远程 Docker 部署时，环境变量主要通过 `docker-compose.yml` 的 `env_file` 和 `environment` 字段注入容器，应用启动时自动读取！** 🚀

