# LLM 配置环境变量传值详解

## 🎯 问题

`config/llm_config.py` 是如何通过 `.env` 文件获取配置的？

## 📊 配置流程图

```
.env 文件
   ↓
环境变量 (系统/进程)
   ↓
Pydantic Settings (settings.py)
   ↓
settings 对象
   ↓
llm_config.py 使用 settings
   ↓
Agent 调用 get_llm_model()
```

---

## 🔍 详细解析

### 步骤 1: `.env` 文件配置

**文件位置**: `testing-agents-service/.env`

```bash
# .env 文件内容
OPENAI_API_KEY=sk-proj-your-key...
OPENAI_MODEL=gpt-5.2
OPENAI_BASE_URL=https://us.api.openai.com/v1
DEFAULT_LLM_PROVIDER=openai
```

### 步骤 2: Pydantic Settings 自动读取

**文件**: `config/settings.py`

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """应用配置类"""
    
    model_config = SettingsConfigDict(
        env_file=".env",              # ← 指定读取 .env 文件
        env_file_encoding="utf-8",
        case_sensitive=False,         # ← 不区分大小写
        extra="ignore",
    )
   
    # 字段定义 - Pydantic 会自动从环境变量读取
    openai_api_key: Optional[str] = None        # ← 从 OPENAI_API_KEY 环境变量读取
    openai_model: str = "gpt-4o"                # ← 从 OPENAI_MODEL 读取，默认 gpt-4o
    openai_base_url: Optional[str] = None       # ← 从 OPENAI_BASE_URL 读取
    default_llm_provider: str = "openai"        # ← 从 DEFAULT_LLM_PROVIDER 读取
```

**关键机制**: Pydantic Settings 会自动：
1. 读取 `.env` 文件
2. 读取系统环境变量
3. 将环境变量值赋给对应的字段（字段名 `openai_api_key` 对应环境变量 `OPENAI_API_KEY`）

### 步骤 3: 创建 settings 单例

```python
@lru_cache
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()  # ← Pydantic 在这里读取环境变量

settings = get_settings()  # ← 全局单例对象
```

**执行时机**: 
- 当 `settings.py` 被导入时，`Settings()` 构造函数会被调用
- Pydantic 自动读取 `.env` 文件和环境变量
- 所有配置值被加载到 `settings` 对象中

### 步骤 4: llm_config.py 使用 settings

**文件**: `config/llm_config.py`

```python
from config.settings import settings  # ← 导入 settings 对象

def get_llm(provider: Optional[LLMProvider] = None, ...):
    """获取配置好的 LLM 实例"""
    
    # 确定使用的提供商
    if provider is None:
        provider = settings.default_llm_provider  # ← 从 settings 读取
    
    # 根据提供商配置 LLM
    if provider == "openai":
        model_name = model_name or settings.openai_model  # ← 从 settings 读取
        
        config_kwargs = {"temperature": temperature, **kwargs}
        
        if settings.openai_base_url:  # ← 从 settings 读取
            config_kwargs["base_url"] = settings.openai_base_url
        
        return init_chat_model(
            f"openai:{model_name}",
            **config_kwargs
        )
```

**关键点**: `llm_config.py` 直接使用 `settings` 对象的属性，这些属性的值来自 `.env` 文件。

### 步骤 5: Agent 使用 LLM

**文件**: `agents/ui_java/agent.py` (或任何 Agent)

```python
from config.llm_config import get_llm_model

# 调用函数获取 LLM（内部会读取 settings 的值）
model = get_llm_model()
```

---

## 🔧 实际运行示例

### 示例 1: 完整流程演示

**1. 创建 `.env` 文件**:
```bash
# testing-agents-service/.env
OPENAI_API_KEY=sk-proj-test123
OPENAI_MODEL=gpt-4o-mini
DEFAULT_LLM_PROVIDER=openai
```

**2. Python 运行时发生的事情**:

```python
# 当导入 settings 时
from config.settings import settings

# Pydantic 自动执行：
# 1. 读取 .env 文件
# 2. 解析环境变量 OPENAI_API_KEY=sk-proj-test123
# 3. 赋值: settings.openai_api_key = "sk-proj-test123"
# 4. 解析环境变量 OPENAI_MODEL=gpt-4o-mini
# 5. 赋值: settings.openai_model = "gpt-4o-mini"
# 6. 解析环境变量 DEFAULT_LLM_PROVIDER=openai
# 7. 赋值: settings.default_llm_provider = "openai"

print(settings.openai_api_key)      # 输出: sk-proj-test123
print(settings.openai_model)        # 输出: gpt-4o-mini
print(settings.default_llm_provider) # 输出: openai
```

**3. 使用 LLM 配置**:

```python
from config.llm_config import get_llm_model

# get_llm_model() 内部会：
# 1. 读取 settings.default_llm_provider  → "openai"
# 2. 读取 settings.openai_model         → "gpt-4o-mini"
# 3. 读取 settings.openai_api_key       → "sk-proj-test123"
# 4. 调用 init_chat_model("openai:gpt-4o-mini", api_key="sk-proj-test123")

model = get_llm_model()  # ✅ 成功创建 OpenAI LLM 实例
```

---

## 📝 环境变量命名规则

### Pydantic 自动映射规则

| Python 字段名 | 环境变量名 | 说明 |
|--------------|-----------|------|
| `openai_api_key` | `OPENAI_API_KEY` | 下划线转大写 |
| `openai_model` | `OPENAI_MODEL` | 下划线转大写 |
| `openai_base_url` | `OPENAI_BASE_URL` | 下划线转大写 |
| `default_llm_provider` | `DEFAULT_LLM_PROVIDER` | 下划线转大写 |
| `deepseek_api_key` | `DEEPSEEK_API_KEY` | 下划线转大写 |

**规则**: 
- Python 字段名使用小写 + 下划线（snake_case）
- 环境变量使用大写 + 下划线（UPPER_SNAKE_CASE）
- Pydantic 会自动匹配（因为设置了 `case_sensitive=False`）

---

## 🎯 配置优先级

Pydantic Settings 的读取优先级（从高到低）：

```
1. 构造函数传入的参数（最高）
   Settings(openai_model="gpt-4")
   
2. 系统环境变量
   export OPENAI_MODEL=gpt-4o
   
3. .env 文件
   OPENAI_MODEL=gpt-3.5
   
4. 字段默认值（最低）
   openai_model: str = "gpt-4o"
```

### 示例：优先级演示

```python
# .env 文件
OPENAI_MODEL=gpt-4o

# 系统环境变量（优先级更高）
export OPENAI_MODEL=gpt-5.2

# Python 代码
from config.settings import settings
print(settings.openai_model)  # 输出: gpt-5.2 （系统环境变量优先）
```

---

## 🧪 测试配置是否生效

### 方法 1: 直接打印 settings

```python
# test_config.py
from config.settings import settings

print("=== Settings 配置 ===")
print(f"OpenAI API Key: {settings.openai_api_key[:20] + '...' if settings.openai_api_key else 'Not Set'}")
print(f"OpenAI Model: {settings.openai_model}")
print(f"OpenAI Base URL: {settings.openai_base_url}")
print(f"Default Provider: {settings.default_llm_provider}")
```

运行：
```bash
cd testing-agents-service
python test_config.py
```

### 方法 2: 测试 LLM 初始化

```python
# test_llm.py
from config.llm_config import get_llm_model, get_llm_info

# 测试配置信息
info = get_llm_info()
print(f"Provider: {info['provider']}")
print(f"Model: {info['model']}")
print(f"API Key Configured: {info['api_key_configured']}")

# 测试模型初始化
try:
    model = get_llm_model()
    print(f"✅ LLM 初始化成功: {model}")
except Exception as e:
    print(f"❌ LLM 初始化失败: {e}")
```

运行：
```bash
cd testing-agents-service
python test_llm.py
```

### 方法 3: 使用配置验证工具

```bash
cd testing-agents-service
python -m config.validate_config
```

---

## 💡 常见问题

### Q1: 为什么修改 .env 文件后不生效？

**A**: 需要重启 Python 进程。

```bash
# 如果在运行 langgraph dev
Ctrl+C  # 停止
langgraph dev  # 重新启动

# 如果在 Docker 中
docker-compose restart langgraph
```

### Q2: 如何在运行时切换配置？

**A**: 通过环境变量覆盖：

```bash
# 方式 1: 命令行传入
OPENAI_MODEL=gpt-4-turbo python your_script.py

# 方式 2: 修改 .env 文件后重启

# 方式 3: 在代码中手动设置（不推荐）
import os
os.environ["OPENAI_MODEL"] = "gpt-4-turbo"
```

### Q3: 如何验证 .env 文件是否被读取？

**A**: 添加调试输出：

```python
# config/settings.py
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print(f"[Settings] Loaded: openai_model={self.openai_model}")  # ← 添加调试输出
```

### Q4: .env 文件在哪里？

**A**: 
- 开发环境: `testing-agents-service/.env` (需要手动创建)
- 参考模板: `testing-agents-service/env.example`

```bash
# 创建配置文件
cd testing-agents-service
cp env.example .env
vim .env  # 编辑填入实际值
```

---

## 📚 相关代码位置

| 文件 | 作用 | 关键内容 |
|------|------|----------|
| `config/settings.py` | 配置定义 | `Settings` 类，Pydantic 自动读取 `.env` |
| `config/llm_config.py` | LLM 配置管理 | 使用 `settings` 对象获取配置 |
| `.env` | 环境变量文件 | 实际配置值（需要创建） |
| `env.example` | 配置模板 | 所有可配置项的示例 |

---

## 🎯 总结

### 核心原理

```
.env 文件 
   ↓ (Pydantic 自动读取)
settings.py (Settings 类)
   ↓ (导入 settings 对象)
llm_config.py (get_llm_model 函数)
   ↓ (调用函数)
Agent 代码
```

### 关键点

1. **Pydantic Settings** 自动从 `.env` 文件和环境变量读取配置
2. **字段名映射**: Python 字段名（如 `openai_api_key`）自动映射到环境变量（如 `OPENAI_API_KEY`）
3. **单例模式**: `settings` 是全局单例，所有模块共享同一个配置实例
4. **优先级**: 系统环境变量 > .env 文件 > 字段默认值

### 使用步骤

1. 创建 `.env` 文件（从 `env.example` 复制）
2. 填入实际的配置值
3. 代码中导入 `get_llm_model()` 并调用
4. Pydantic 自动读取配置并创建 LLM 实例

---

**就是这么简单！Pydantic Settings 帮你自动完成了所有环境变量的读取和映射工作！** ✨

