# MCP 集成说明

## 概述

本系统已集成 MCP (Model Context Protocol) 支持，可以安全地加载和使用各种 MCP 工具，而不影响现有的核心功能。

## 特性

✅ **可选集成**：MCP 功能完全可选，不影响现有功能  
✅ **安全失败**：如果 MCP 服务不可用，系统会优雅降级  
✅ **配置化**：通过配置文件管理 MCP 服务  
✅ **多服务支持**：可以同时连接多个 MCP 服务  

## 安装

### 1. 安装 MCP 适配器

```bash
# 使用虚拟环境的 Python
.venv\Scripts\python.exe -m pip install langchain-mcp-adapters
```

### 2. 配置 MCP 服务

编辑 `src/file_rag/mcp_config.py` 文件：

```python
MCP_SERVERS = {
    "chrome_mcp": {
        "enabled": True,  # 启用此服务
        "url": "http://127.0.0.1:12306/mcp",
        "transport": "streamable_http",
        "description": "Chrome 浏览器自动化工具"
    },
}
```

## 使用方法

### 方法 1：默认启用 MCP（推荐）

```python
from file_rag.main import build_multimodal_workflow

# 构建工作流，默认启用 MCP
app = build_multimodal_workflow()
```

### 方法 2：显式控制 MCP

```python
from file_rag.main import build_multimodal_workflow

# 启用 MCP
app = build_multimodal_workflow(enable_mcp=True)

# 或禁用 MCP
app = build_multimodal_workflow(enable_mcp=False)
```

### 方法 3：通过配置文件控制

编辑 `mcp_config.py`：

```python
MCP_SETTINGS = {
    "enable_mcp": False,  # 全局禁用 MCP
    "fail_silently": True,  # 失败时静默
}
```

## 配置选项

### MCP 服务配置

每个 MCP 服务支持以下配置：

```python
{
    "enabled": True,  # 是否启用此服务
    "url": "http://...",  # HTTP 传输的 URL
    "transport": "streamable_http",  # 传输方式
    "command": "npx",  # stdio 传输的命令
    "args": [...],  # 命令参数
    "env": {...},  # 环境变量
    "description": "服务描述"
}
```

### 传输方式

1. **streamable_http**：HTTP 传输（推荐用于远程服务）
   ```python
   {
       "url": "http://127.0.0.1:12306/mcp",
       "transport": "streamable_http"
   }
   ```

2. **stdio**：标准输入输出传输（用于本地进程）
   ```python
   {
       "command": "npx",
       "args": ["-y", "@modelcontextprotocol/server-filesystem"],
       "transport": "stdio"
   }
   ```

## 添加新的 MCP 服务

### 示例 1：文件系统 MCP

```python
MCP_SERVERS = {
    "filesystem_mcp": {
        "enabled": True,
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "E:/allowed/path"],
        "transport": "stdio",
        "description": "文件系统操作工具"
    }
}
```

### 示例 2：GitHub MCP

```python
MCP_SERVERS = {
    "github_mcp": {
        "enabled": True,
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-github"],
        "transport": "stdio",
        "env": {
            "GITHUB_PERSONAL_ACCESS_TOKEN": "your_token_here"
        },
        "description": "GitHub 操作工具"
    }
}
```

## 故障排除

### 问题 1：MCP 工具加载失败

**症状**：
```
[MCP] ⚠️ 加载 MCP 工具失败: ...
```

**解决方案**：
1. 检查 MCP 服务是否运行
2. 检查 URL 或命令是否正确
3. 检查网络连接
4. 查看详细错误信息

### 问题 2：langchain-mcp-adapters 未安装

**症状**：
```
[MCP] ⚠️ langchain-mcp-adapters 未安装
```

**解决方案**：
```bash
.venv\Scripts\python.exe -m pip install langchain-mcp-adapters
```

### 问题 3：MCP 服务连接超时

**解决方案**：
调整超时设置：
```python
MCP_SETTINGS = {
    "timeout": 60,  # 增加超时时间
}
```

## 安全性

### 1. 失败安全

默认情况下，MCP 加载失败不会影响主功能：

```python
MCP_SETTINGS = {
    "fail_silently": True,  # 失败时静默，不抛出异常
}
```

### 2. 禁用 MCP

如果不需要 MCP 功能，可以完全禁用：

```python
# 方法 1：配置文件
MCP_SETTINGS = {
    "enable_mcp": False,
}

# 方法 2：代码
app = build_multimodal_workflow(enable_mcp=False)
```

### 3. 选择性启用

只启用需要的服务：

```python
MCP_SERVERS = {
    "chrome_mcp": {
        "enabled": True,  # 启用
    },
    "filesystem_mcp": {
        "enabled": False,  # 禁用
    }
}
```

## 日志输出

系统会输出详细的 MCP 加载日志：

```
[MCP] 正在连接 chrome_mcp (Chrome 浏览器自动化工具)...
[MCP] ✓ 成功加载 5 个 MCP 工具
[MCP]   - navigate_to: Navigate to a URL...
[MCP]   - click_element: Click an element...
[MCP] 总共加载了 5 个 MCP 工具
```

## 最佳实践

1. **开发环境**：启用 MCP 进行测试
2. **生产环境**：根据需要选择性启用
3. **配置管理**：使用配置文件而不是硬编码
4. **错误处理**：保持 `fail_silently=True` 确保稳定性
5. **日志监控**：关注 MCP 加载日志

## 示例代码

### 完整示例

```python
from file_rag.main import build_multimodal_workflow
from langchain_core.messages import HumanMessage

# 构建工作流（自动加载 MCP 工具）
app = build_multimodal_workflow(enable_mcp=True)

# 使用工作流
result = app.invoke({
    "messages": [HumanMessage(content="你好")],
    "file_type": "",
    "extracted_content": ""
})

print(result['messages'][-1].content)
```

## 参考资源

- [LangChain MCP 文档](https://docs.langchain.com/oss/python/langchain/mcp)
- [MCP 官方文档](https://modelcontextprotocol.io/)
- [langchain-mcp-adapters GitHub](https://github.com/langchain-ai/langchain-mcp-adapters)

