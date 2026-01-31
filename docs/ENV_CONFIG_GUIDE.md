# 环境变量配置完整说明

## 📋 概述

本文档详细说明了项目中所有环境变量的用途和配置方法。

根据代码分析，项目共需要配置 **60+ 个环境变量**，分为 10 大类。

## ✅ 配置检查清单

### 必需配置

- [ ] `OPENAI_API_KEY` - OpenAI API 密钥（主要LLM）
- [ ] `OPENAI_MODEL` - 使用的模型名称
- [ ] `OPENAI_BASE_URL` - API 端点地址

### 可选但推荐

- [ ] `DEEPSEEK_API_KEY` - DeepSeek API 密钥（用于 RAG）
- [ ] `DOUBAO_API_KEY` - 豆包 API 密钥（用于图片识别）
- [ ] `MILVUS_URI` - Milvus 向量数据库地址
- [ ] `EMBEDDING_HOST` - Ollama Embedding 服务地址

---

## 🎯 配置分类详解

### 1. LLM 配置（核心）⭐

#### OpenAI 配置（主要使用）

```bash
OPENAI_API_KEY=sk-proj-your-key...     # ✅ 必需
OPENAI_MODEL=gpt-5.2                   # ✅ 必需
OPENAI_BASE_URL=https://us.api.openai.com/v1  # ❌ 可选
```

**使用者**: ui_java_agent, ui_agent, api_agent, testcase_agent

#### DeepSeek 配置（备用/RAG专用）

```bash
DEEPSEEK_API_KEY=sk-your-key          # ❌ 可选
DEEPSEEK_MODEL=deepseek-chat          # ❌ 可选
```

**使用者**: rest_api_agent, data_agent, rag_anything MCP

**特点**: 131K tokens context window

#### 默认提供商

```bash
DEFAULT_LLM_PROVIDER=openai           # ❌ 可选，默认 openai
```

**可选值**: `openai`, `deepseek`, `anthropic`

---

### 2. RAG 和文档处理配置

#### RAG Anything 配置

```bash
# RAG 工作目录和解析器
RAG_WORKING_DIR=./rag_storage
RAG_PARSER=docling                     # 推荐：docling
RAG_PARSE_METHOD=auto

# RAG 功能开关
RAG_ENABLE_IMAGE=true
RAG_ENABLE_TABLE=true
RAG_ENABLE_EQUATION=true
RAG_LOAD_EXISTING=true
RAG_MAX_CONCURRENT=2
```

**使用者**: `mcp/rag_anything` MCP 服务器

#### LLM 配置（RAG MCP 专用）

```bash
LLM_PROVIDER=deepseek                 # RAG 使用的 LLM
LLM_MODEL=deepseek-chat
LLM_API_KEY=                          # 可复用 DEEPSEEK_API_KEY
LLM_BASE_URL=https://api.deepseek.com/v1
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=4096
```

**注意**: 这些配置**仅用于** RAG MCP 服务，不影响主 Agent

---

### 3. Embedding 配置

```bash
USE_OLLAMA_EMBEDDING=true
EMBEDDING_MODEL=qwen3-embedding:0.6b
EMBEDDING_HOST=http://localhost:11434  # ⚠️ 需要运行 Ollama
EMBEDDING_DIM=1024
```

**前置条件**:
```bash
# 安装 Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 启动 Ollama
ollama serve

# 拉取 Embedding 模型
ollama pull qwen3-embedding:0.6b
```

---

### 4. 向量存储配置

```bash
LIGHTRAG_VECTOR_STORAGE=milvus
VECTOR_STORAGE=milvus
MILVUS_URI=http://localhost:19530     # ⚠️ 需要运行 Milvus
MILVUS_DB_NAME=default
```

**启动 Milvus** (使用 Docker):
```bash
docker run -d --name milvus \
  -p 19530:19530 \
  -p 9091:9091 \
  milvusdb/milvus:latest
```

---

### 5. MCP 服务端点配置

```bash
# MCP 服务地址
RAG_QUERY_MCP_URL=http://127.0.0.1:8002/sse
RAG_ANYTHING_MCP_URL=http://localhost:8001/sse
PYTEST_MCP_URL=http://127.0.0.1:8004/sse
CHROME_MCP_URL=http://localhost:9222/sse
```

**说明**: 这些是 MCP 客户端连接的服务器地址

---

### 6. 豆包和视觉模型配置

```bash
# 豆包 API（用于图片识别和 PDF 多模态）
DOUBAO_API_KEY=your-doubao-key        # ❌ 可选

# Vision 模型配置（可选）
VISION_API_KEY=                       # 默认使用 LLM_API_KEY
VISION_BASE_URL=
VISION_MODEL=
VISION_PROVIDER=
```

**使用者**: `agents/testcase/pdf_processor.py`, `agents/pdf_processor.py`

---

### 7. Midscene MCP 配置

```bash
MIDSCENE_MODEL_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
MIDSCENE_MODEL_API_KEY=your-key
MIDSCENE_MODEL_NAME=doubao-seed-1-8-251215
MIDSCENE_MODEL_FAMILY=doubao-vision
MCP_SERVER_REQUEST_TIMEOUT=600000
```

**使用者**: `src/ui_automation/ui_demo/midscene_mcp_agent.py`

---

### 8. 测试执行配置

```bash
# 测试输出
TEST_OUTPUT_DIR=./test-output
PARALLEL_WORKERS=4
TEST_TIMEOUT=300

# Allure 报告
ALLURE_RESULTS_DIR=./allure-results
ALLURE_REPORT_DIR=./allure-report

# API 测试
OUTPUT_DIR=./api-test-reports

# MCP 服务端口
PYTEST_GENERATOR_PORT=8005
TEST_EXECUTOR_PORT=8004
RAG_SERVER_PORT=8002
```

---

### 9. LangGraph 服务配置

```bash
LANGGRAPH_PORT=2025
LANGGRAPH_API_URL=http://localhost:2025
```

**说明**: 启动 `langgraph dev` 时自动设置

---

### 10. 其他配置

```bash
# 日志
LOG_LEVEL=INFO                        # DEBUG, INFO, WARNING, ERROR

# PDF 多模态
ENABLE_PDF_MULTIMODAL=true

# RAG Anything 服务器
SERVER_HOST=0.0.0.0
SERVER_PORT=8001
SERVER_SSE_MODE=true
DEBUG=false

# 工作目录
API_WORKSPACE_ROOT=agents/api/workspace
UI_WORKSPACE_ROOT=agents/ui/workspace
UI_JAVA_WORKSPACE_ROOT=agents/ui_java/workspace
TESTCASE_WORKSPACE_ROOT=agents/testcase/workspace
```

---

## 🚀 快速配置指南

### 场景 1: 仅使用 OpenAI (最简单)

```bash
# 复制配置模板
cp env.example .env

# 只需配置这3个
OPENAI_API_KEY=sk-proj-your-key...
OPENAI_MODEL=gpt-5.2
OPENAI_BASE_URL=https://us.api.openai.com/v1
```

### 场景 2: 使用 RAG 功能

```bash
# OpenAI 配置
OPENAI_API_KEY=sk-proj-your-key...
OPENAI_MODEL=gpt-5.2

# DeepSeek 配置（用于 RAG）
DEEPSEEK_API_KEY=sk-your-deepseek-key

# 启动依赖服务
docker run -d milvusdb/milvus:latest -p 19530:19530
ollama serve

# Milvus 配置
MILVUS_URI=http://localhost:19530

# Embedding 配置
EMBEDDING_HOST=http://localhost:11434
```

### 场景 3: 完整配置（所有功能）

参考 `env.example` 文件的完整配置。

---

## ⚠️ 常见问题

### Q1: 哪些配置是必需的？

**A**: 最低要求：
```bash
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-5.2
OPENAI_BASE_URL=https://us.api.openai.com/v1
```

### Q2: 为什么有 LLM_API_KEY 和 OPENAI_API_KEY？

**A**: 
- `OPENAI_API_KEY` - 主 Agent 使用（通过 `config/llm_config.py`）
- `LLM_API_KEY` - RAG MCP 服务使用（可设置为不同的 key）
- 如果不设置 `LLM_API_KEY`，会自动回退到 `DEEPSEEK_API_KEY` 或 `OPENAI_API_KEY`

### Q3: 如何验证配置？

**A**:
```python
from config.llm_config import get_llm_info

info = get_llm_info()
print(f"Provider: {info['provider']}")
print(f"Model: {info['model']}")
print(f"API Key: {'✅ Configured' if info['api_key_configured'] else '❌ Missing'}")
```

### Q4: 端口被占用怎么办？

**A**: 修改对应的端口配置：
```bash
# 例如修改 LangGraph 端口
LANGGRAPH_PORT=3000

# 修改 RAG 服务端口
SERVER_PORT=8888
RAG_ANYTHING_MCP_URL=http://localhost:8888/sse
```

---

## 📊 配置项统计

| 类别 | 配置项数量 | 必需项 |
|------|-----------|--------|
| LLM 配置 | 12 | 3 |
| RAG 配置 | 18 | 0 |
| MCP 端点 | 4 | 0 |
| 向量存储 | 4 | 0 |
| 测试执行 | 10 | 0 |
| 视觉模型 | 9 | 0 |
| 服务器配置 | 6 | 0 |
| 工作目录 | 9 | 0 |
| **总计** | **72** | **3** |

---

## 🎯 最佳实践

1. **不要提交 .env 文件**
   ```bash
   # .gitignore 已包含
   .env
   .env.local
   .env.*.local
   ```

2. **使用 env.example 作为模板**
   ```bash
   cp env.example .env
   # 编辑 .env 填入实际值
   ```

3. **分环境配置**
   ```
   .env.development
   .env.production
   .env.test
   ```

4. **定期轮换 API Key**

5. **使用环境变量验证**
   ```bash
   # 检查关键配置
   [ -z "$OPENAI_API_KEY" ] && echo "❌ OPENAI_API_KEY not set"
   ```

---

**完整的环境变量配置指南！** ✅

参考文件: `env.example` - 包含所有配置项的示例值

