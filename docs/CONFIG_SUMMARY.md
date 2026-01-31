# 环境变量配置完整指南

## 📝 概述

项目已完成环境变量配置的**全面梳理和文档化**，共识别和配置了 **70+ 个环境变量**，分为 10 大类别。

## ✅ 已完成的工作

### 1. 配置文件更新

- ✅ **env.example** - 完整的环境变量配置模板（222 行）
  - 包含所有 70+ 个环境变量
  - 每个变量都有详细注释说明
  - 分类清晰，易于查找

- ✅ **settings.py** - 应用配置管理（已更新）
  - 添加 `extra="ignore"` 忽略不需要的环境变量
  - 支持 OpenAI, DeepSeek, Anthropic 三种 LLM 提供商
  - 包含所有工作目录配置

- ✅ **llm_config.py** - 统一 LLM 配置管理
  - `get_llm()` - 获取指定的 LLM 实例
  - `get_default_llm()` - 获取默认 LLM
  - `get_llm_info()` - 获取配置信息（用于验证）
  - 支持自定义 base_url 和其他参数

### 2. 配置验证工具

- ✅ **validate_config.py** - 自动化配置验证脚本
  - 验证必需的 LLM 配置
  - 检查 RAG 和 MCP 配置
  - 检测可选功能配置
  - 输出详细的验证报告

**运行方式**:
```bash
cd testing-agents-service
python -m config.validate_config
```

**输出示例**:
```
🚀 Starting Configuration Validation...
============================================================
🔍 Validating LLM Configuration...
   Provider: openai
   Model: gpt-5.2
   ✅ OPENAI_API_KEY is configured
   ✅ OPENAI_MODEL is configured
   Base URL: https://us.api.openai.com/v1

... (更多验证信息)

📊 Configuration Validation Summary
✅ No critical errors found
```

### 3. 详细文档

- ✅ **ENV_CONFIG_GUIDE.md** - 完整的配置指南（400+ 行）
  - 10 大配置类别详解
  - 每个变量的用途和说明
  - 快速配置指南（3 种场景）
  - 常见问题解答
  - 故障排除指南
  - 最佳实践

## 📊 配置变量统计

| 类别 | 变量数量 | 必需项 | 说明 |
|------|---------|--------|------|
| **LLM 配置** | 12 | 3 | OpenAI, DeepSeek, Anthropic |
| **RAG 配置** | 18 | 0 | 文档解析、Embedding、向量存储 |
| **MCP 端点** | 4 | 0 | RAG Query, RAG Anything, Pytest, Chrome |
| **向量存储** | 4 | 0 | Milvus 配置 |
| **测试执行** | 10 | 0 | 测试输出、Allure 报告、MCP 端口 |
| **视觉模型** | 9 | 0 | Doubao, Midscene, Vision |
| **服务器配置** | 6 | 0 | RAG Anything 服务器 |
| **工作目录** | 9 | 0 | API, UI, UI Java, TestCase |
| **日志和其他** | 2 | 0 | 日志级别、PDF 多模态 |
| **LangGraph** | 2 | 0 | 端口和 API URL |
| **总计** | **76** | **3** | |

## 🎯 必需配置（最小化启动）

只需配置这 3 个环境变量即可启动所有 Agent:

```bash
OPENAI_API_KEY=sk-proj-your-key...
OPENAI_MODEL=gpt-5.2
OPENAI_BASE_URL=https://us.api.openai.com/v1
```

## 🚀 配置场景

### 场景 1: 仅使用 OpenAI（最简单）

```bash
cp env.example .env
# 编辑 .env，只配置 OpenAI 相关的 3 个变量
```

### 场景 2: 使用 RAG 功能

需要额外配置:
- `DEEPSEEK_API_KEY` - 用于 RAG MCP 服务
- `MILVUS_URI` - 向量数据库地址
- `EMBEDDING_HOST` - Ollama Embedding 服务

### 场景 3: 完整功能

参考 `env.example` 文件的完整配置。

## 📁 相关文件位置

```
testing-agents-service/
├── env.example               # 配置模板（所有变量）
├── ENV_CONFIG_GUIDE.md       # 完整配置指南
├── config/
│   ├── settings.py           # 应用配置管理
│   ├── llm_config.py         # LLM 配置统一管理
│   ├── mcp_settings.py       # MCP 服务配置
│   ├── validate_config.py    # 配置验证工具
│   ├── LLM_CONFIG.md         # LLM 配置迁移说明
│   └── README_LLM.md         # LLM 配置 README
```

## 🔧 如何使用

### 1. 创建配置文件

```bash
cd testing-agents-service
cp env.example .env
```

### 2. 编辑配置

编辑 `.env` 文件，填入实际的 API Key 和其他配置值。

### 3. 验证配置

```bash
python -m config.validate_config
```

### 4. 启动服务

```bash
langgraph dev
```

## 🎓 代码使用示例

### 在 Agent 中使用 LLM 配置

```python
from config.llm_config import get_llm_model

# 获取默认 LLM（所有新 Agent 都应使用此方法）
model = get_llm_model()

# 在 DeepAgents 中使用
agent = create_agent(
    model=model,
    tools=tools,
    system_prompt=SYSTEM_PROMPT,
    middleware=[skills_middleware],
    backend=workspace_backend,
)
```

### 验证当前配置

```python
from config.llm_config import get_llm_info

info = get_llm_info()
print(f"Provider: {info['provider']}")
print(f"Model: {info['model']}")
print(f"API Key: {'✅ Configured' if info['api_key_configured'] else '❌ Missing'}")
```

## ⚠️ 注意事项

### 安全性

1. **不要提交 `.env` 文件到 Git**
   - 已添加到 `.gitignore`
   - 使用 `env.example` 作为模板

2. **API Key 保护**
   - 定期轮换 API Key
   - 使用环境变量或密钥管理服务

### 兼容性

1. **LLM API Key 复用**
   - `LLM_API_KEY`（用于 RAG MCP）会自动回退到 `DEEPSEEK_API_KEY` 或 `OPENAI_API_KEY`
   - Vision 配置会自动使用 LLM 配置

2. **端口冲突**
   - 确保配置的端口没有被占用
   - 检查防火墙设置

### 依赖服务

某些配置需要外部服务运行:

| 配置项 | 依赖服务 | 状态检查 |
|--------|---------|---------|
| `EMBEDDING_HOST` | Ollama | `curl http://localhost:11434` |
| `MILVUS_URI` | Milvus | `curl http://localhost:19530` |
| MCP 服务 | Node.js, Python | 项目已包含 |

## 📚 相关文档

- [ENV_CONFIG_GUIDE.md](./ENV_CONFIG_GUIDE.md) - 完整的环境变量配置指南
- [LLM_CONFIG.md](./config/LLM_CONFIG.md) - LLM 配置迁移说明
- [README_LLM.md](./config/README_LLM.md) - LLM 配置 README
- [env.example](./env.example) - 配置模板

## ✨ 新增功能

1. **统一 LLM 配置管理**
   - 所有 Agent 统一使用 `config/llm_config.py`
   - 支持多提供商切换（OpenAI, DeepSeek, Anthropic）
   - 自定义 base_url 支持

2. **配置验证工具**
   - 自动检测配置问题
   - 详细的验证报告
   - 警告和错误分级

3. **完整文档**
   - 详细的配置说明
   - 场景化配置指南
   - 故障排除帮助

## 🎉 总结

通过这次配置梳理，项目现在拥有:

- ✅ **完整的配置模板** (`env.example`)
- ✅ **统一的 LLM 管理** (`llm_config.py`)
- ✅ **自动化验证工具** (`validate_config.py`)
- ✅ **详细的文档** (`ENV_CONFIG_GUIDE.md`)
- ✅ **易于维护的结构**

所有环境变量都已文档化，配置过程简单明了！🚀

