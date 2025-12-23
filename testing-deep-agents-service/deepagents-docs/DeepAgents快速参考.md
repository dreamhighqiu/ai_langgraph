# DeepAgents 快速参考指南 ⚡

## 快速开始

```python
from deepagents import create_deep_agent

# 最简单的开始
agent = create_deep_agent(
    system_prompt="你是一个智能助手"
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "你好"}]
})
```

## 核心参数速查

### create_deep_agent 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `model` | str \| BaseChatModel | Claude Sonnet 4.5 | AI 模型 |
| `tools` | Sequence[BaseTool] | None | 自定义工具列表 |
| `system_prompt` | str | None | 系统提示词 |
| `middleware` | Sequence[AgentMiddleware] | () | 额外的中间件 |
| `subagents` | list[SubAgent] | None | 子智能体列表 |
| `store` | BaseStore | None | 长期记忆存储 |
| `backend` | BackendProtocol | StateBackend | 文件存储后端 |
| `interrupt_on` | dict | None | 人机交互配置 |
| `checkpointer` | Checkpointer | None | 会话检查点 |
| `debug` | bool | False | 调试模式 |

## 默认工具速查

### FilesystemMiddleware 提供的工具

| 工具 | 功能 | 示例 |
|------|------|------|
| `ls(path)` | 列出目录 | `ls("/data/")` |
| `read_file(path)` | 读取文件 | `read_file("/config.json")` |
| `write_file(path, content)` | 创建文件 | `write_file("/new.txt", "内容")` |
| `edit_file(path, old, new)` | 编辑文件 | `edit_file("/file.txt", "old", "new")` |
| `glob(pattern)` | 查找文件 | `glob("**/*.py")` |
| `grep(pattern, glob)` | 搜索内容 | `grep("TODO", glob="*.py")` |
| `execute(command)` | 执行命令 | `execute("pytest")` |

### SubAgentMiddleware 提供的工具

| 工具 | 功能 | 示例 |
|------|------|------|
| `task(instruction, agent_name)` | 启动子智能体 | `task("研究主题", "general-purpose")` |

## Backend 类型速查

### 对比表

| Backend | 存储位置 | 持久化 | 跨会话 | 执行命令 | 使用场景 |
|---------|---------|--------|--------|---------|---------|
| **StateBackend** | Agent State | ✅ | ❌ | ❌ | 临时文件、单会话 |
| **StoreBackend** | LangGraph Store | ✅ | ✅ | ❌ | 长期记忆、跨会话 |
| **SandboxBackend** | 沙箱环境 | ✅ | ✅ | ✅ | 代码执行、测试 |
| **CompositeBackend** | 混合 | ✅ | ✅ | ✅ | 企业级应用 |

### 代码示例

```python
from deepagents.backends import StateBackend, StoreBackend, CompositeBackend
from langgraph.store.memory import InMemoryStore

# StateBackend（默认）
agent = create_deep_agent()

# StoreBackend
agent = create_deep_agent(
    backend=lambda rt: StoreBackend(rt),
    store=InMemoryStore()
)

# CompositeBackend（推荐）
composite = CompositeBackend(
    default=lambda rt: StateBackend(rt),
    routes={
        "/memories/": lambda rt: StoreBackend(rt),
        "/cache/": lambda rt: StateBackend(rt),
    }
)
agent = create_deep_agent(
    backend=composite,
    store=InMemoryStore()
)
```

## 子智能体配置速查

### SubAgent 定义

```python
subagent = {
    "name": "agent-name",              # 必需：唯一标识
    "description": "用途描述",          # 必需：主 Agent 根据此决定是否调用
    "system_prompt": "系统提示词",      # 必需：子智能体的行为指令
    "tools": [tool1, tool2],           # 可选：额外工具
    "model": "gpt-4",                  # 可选：使用不同模型
    "middleware": [middleware],        # 可选：额外中间件
}
```

### 常用子智能体模板

```python
# 代码审查专家
code_reviewer = {
    "name": "code-reviewer",
    "description": "代码审查专家，审查代码质量和安全性",
    "system_prompt": "你是代码审查专家，关注代码质量、安全性和最佳实践。",
}

# 文档编写专家
doc_writer = {
    "name": "doc-writer",
    "description": "技术文档编写专家",
    "system_prompt": "你是技术文档专家，生成清晰、专业的文档。",
}

# 测试工程师
test_engineer = {
    "name": "test-engineer",
    "description": "测试工程师，编写和执行测试",
    "system_prompt": "你是测试工程师，编写全面的单元测试和集成测试。",
}

# 研究分析师
research_analyst = {
    "name": "research-analyst",
    "description": "研究分析专家，深度研究复杂主题",
    "system_prompt": "你是研究分析专家，擅长收集信息、分析数据并生成报告。",
}
```

## 人机交互配置速查

### 配置方式

```python
from langchain.agents.middleware import InterruptOnConfig

# 方式 1: 简单配置（布尔值）
interrupt_on = {
    "execute": True,      # 执行命令前中断
    "write_file": True,   # 写文件前中断
    "edit_file": True,    # 编辑文件前中断
}

# 方式 2: 详细配置
interrupt_on = {
    "execute": InterruptOnConfig(
        interrupt_before=True,   # 执行前中断
        interrupt_after=False,   # 执行后不中断
    ),
    "write_file": InterruptOnConfig(
        interrupt_before=True,
        interrupt_after=True,    # 执行后也中断（查看结果）
    ),
}
```

### 使用示例

```python
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
agent = create_deep_agent(
    checkpointer=checkpointer,
    interrupt_on={"execute": True}
)

config = {"configurable": {"thread_id": "session-1"}}

# 第一步：发起请求（会中断）
result = agent.invoke({
    "messages": [{"role": "user", "content": "删除所有日志"}]
}, config=config)

# 第二步：批准执行
result = agent.invoke(None, config=config)
```

## 常用配置模板

### 1. 开发环境配置

```python
agent = create_deep_agent(
    debug=True,  # 开启调试
    system_prompt="你是开发助手"
)
```

### 2. 生产环境配置

```python
from langgraph.checkpoint.memory import MemorySaver

agent = create_deep_agent(
    checkpointer=MemorySaver(),
    interrupt_on={
        "execute": True,
        "write_file": True,
        "edit_file": True,
    },
    debug=False,
    system_prompt="你是生产环境助手"
)
```

### 3. 企业级配置（完整）

```python
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from langgraph.store.memory import InMemoryStore
from langgraph.checkpoint.memory import MemorySaver

store = InMemoryStore()
checkpointer = MemorySaver()

composite_backend = CompositeBackend(
    default=lambda rt: StateBackend(rt),
    routes={
        "/memories/": lambda rt: StoreBackend(rt),
        "/projects/": lambda rt: StoreBackend(rt),
    }
)

agent = create_deep_agent(
    backend=composite_backend,
    store=store,
    checkpointer=checkpointer,
    subagents=[code_reviewer, doc_writer, test_engineer],
    interrupt_on={
        "execute": True,
        "write_file": True,
        "edit_file": True,
    },
    debug=False,
    system_prompt="你是企业级 AI 助手"
)
```

## 最佳实践清单

### ✅ 推荐做法

- ✅ 使用 CompositeBackend 组合不同存储策略
- ✅ 为敏感操作配置 interrupt_on
- ✅ 使用子智能体隔离复杂任务
- ✅ 将长期记忆存储在 /memories/ 路径
- ✅ 开发时开启 debug 模式
- ✅ 生产环境使用 Checkpointer 持久化状态

### ❌ 避免做法

- ❌ 不要在简单任务中使用子智能体
- ❌ 不要在生产环境关闭所有 interrupt_on
- ❌ 不要混用不同的 Store 实例
- ❌ 不要在没有 Checkpointer 时使用 interrupt_on
- ❌ 不要忘记为 StoreBackend 提供 store 参数

## 故障排查

### 问题 1: 子智能体没有被调用

**原因**: description 不够清晰，主 Agent 不知道何时调用

**解决**:
```python
# ❌ 不好的 description
"description": "一个助手"

# ✅ 好的 description
"description": "代码审查专家，在完成代码编写后自动审查代码质量和安全性"
```

### 问题 2: 文件跨会话无法访问

**原因**: 使用了 StateBackend（不跨会话）

**解决**:
```python
# 使用 StoreBackend 或 CompositeBackend
agent = create_deep_agent(
    backend=lambda rt: StoreBackend(rt),
    store=InMemoryStore()
)
```

### 问题 3: interrupt_on 不生效

**原因**: 没有提供 Checkpointer

**解决**:
```python
from langgraph.checkpoint.memory import MemorySaver

agent = create_deep_agent(
    checkpointer=MemorySaver(),  # 必需
    interrupt_on={"execute": True}
)
```

## 更多资源

- 📖 [完整文档](DeepAgents框架深度解析.md)
- 💻 [示例代码](DeepAgents示例代码.py)
- 🔗 [LangGraph 文档](https://langchain-ai.github.io/langgraph/)

