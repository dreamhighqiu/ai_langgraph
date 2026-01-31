# HTTP 工具重构文档

## 📋 概述

本次重构将测试用例工具从直接调用 `TestCaseService` 改为通过 HTTP 接口调用，降低了耦合度，并新增了批量创建测试用例的功能。

## 🎯 重构目标

1. **降低耦合度**：工具函数不再直接依赖 `TestCaseService`、数据库会话等内部实现
2. **提高可维护性**：通过 HTTP 接口调用，工具函数与业务逻辑解耦
3. **增强功能**：新增批量创建测试用例的工具，提高效率
4. **统一接口**：所有工具都通过标准的 HTTP API 调用

## 🔄 主要变化

### 1. 依赖变化

**修改前**：
```python
from app.config.database import async_session_factory, MongoDB
from app.services.test_case_service import TestCaseService
from app.schemas.test_case import TestCaseCreate, TestCaseUpdate, TestStepCreate
from app.schemas.enums import Priority, TestCaseState, TestCaseType, TestCaseTemplate, AutomationStatus
```

**修改后**：
```python
from typing import Optional, Any
import httpx

from app.config.settings import settings
```

### 2. 新增辅助函数

#### `get_api_url(path: str) -> str`
构建完整的 API URL。

```python
def get_api_url(path: str) -> str:
    """构建完整的 API URL"""
    return f"{API_BASE_URL}{API_PREFIX}{path}"
```

#### `make_http_request(...) -> dict[str, Any]`
发送 HTTP 请求的通用函数，处理错误和异常。

```python
async def make_http_request(
    method: str,
    url: str,
    json_data: Optional[dict] = None,
    params: Optional[dict] = None,
) -> dict[str, Any]:
    """发送 HTTP 请求的通用函数"""
    # 使用 httpx 发送请求
    # 处理 HTTP 错误、网络错误等
```

### 3. 工具函数重构

#### `create_test_case_tool`

**修改前**：
- 直接创建数据库会话
- 调用 `TestCaseService.create_test_case()`
- 手动提交事务

**修改后**：
- 构建 HTTP 请求数据
- 调用 `POST /api/v2/folders/{folder_id}/test-cases`
- 返回 API 响应

**示例**：
```python
# 构建请求数据
request_data = {
    "name": name,
    "template": template,
    "priority": priority,
    # ...
}

# 发送 HTTP 请求
url = get_api_url(f"/folders/{folder_id}/test-cases")
response_data = await make_http_request(
    method="POST",
    url=url,
    json_data=request_data,
    params={"project_identifier": project_identifier},
)
```

#### `update_test_case_tool`

**修改前**：
- 直接创建数据库会话
- 调用 `TestCaseService.update_test_case()`
- 手动提交事务

**修改后**：
- 构建 HTTP 请求数据（只包含需要更新的字段）
- 调用 `PATCH /api/v2/test-cases/{test_case_identifier}`
- 返回 API 响应

**示例**：
```python
# 构建请求数据（只包含提供的字段）
request_data = {}
if name is not None:
    request_data["name"] = name
if priority is not None:
    request_data["priority"] = priority
# ...

# 发送 HTTP 请求
url = get_api_url(f"/test-cases/{test_case_identifier}")
response_data = await make_http_request(
    method="PATCH",
    url=url,
    json_data=request_data,
    params={"project_identifier": project_identifier},
)
```

### 4. 新增批量创建工具

#### `batch_create_test_cases_tool`

**功能**：一次性创建多个测试用例

**参数**：
- `project_identifier`: 项目标识符
- `folder_id`: 文件夹 ID
- `test_cases`: 测试用例列表（每个元素是一个包含测试用例信息的字典）

**实现方式**：
- 遍历测试用例列表
- 逐个调用 `create_test_case_tool`
- 收集每个测试用例的创建结果
- 返回统计信息（总数、成功数、失败数）

**示例**：
```python
result = await batch_create_test_cases_tool(
    project_identifier="PROJ-001",
    folder_id="folder-uuid",
    test_cases=[
        {
            "name": "测试用例1",
            "description": "描述1",
            "priority": "high",
            "test_case_steps": [...]
        },
        {
            "name": "测试用例2",
            "description": "描述2",
            "priority": "medium",
            "test_case_steps": [...]
        }
    ]
)

# 返回结果
{
    "success": True,
    "data": {
        "total": 2,
        "succeeded": 2,
        "failed": 0,
        "results": [...]
    },
    "message": "批量创建完成：成功 2 个，失败 0 个"
}
```

## 📊 对比分析

### 优点

1. **降低耦合度**
   - ✅ 工具函数不再依赖内部服务和数据库
   - ✅ 可以独立部署和测试
   - ✅ 更容易维护和扩展

2. **统一接口**
   - ✅ 所有工具都通过标准的 HTTP API 调用
   - ✅ 与前端使用相同的接口
   - ✅ 便于调试和监控

3. **增强功能**
   - ✅ 新增批量创建功能
   - ✅ 提高创建效率
   - ✅ 支持更复杂的场景

4. **更好的错误处理**
   - ✅ 统一的错误处理机制
   - ✅ 详细的错误信息
   - ✅ 网络错误和 HTTP 错误分别处理

### 缺点

1. **性能开销**
   - ⚠️ HTTP 调用比直接调用服务慢
   - ⚠️ 批量创建时需要多次 HTTP 请求

2. **依赖外部服务**
   - ⚠️ 需要后端 API 服务正在运行
   - ⚠️ 网络问题可能导致失败

### 解决方案

1. **性能优化**
   - 考虑在后端添加批量创建的 API 接口
   - 使用连接池复用 HTTP 连接

2. **可靠性提升**
   - 添加重试机制
   - 添加超时控制
   - 添加健康检查

## 🧪 测试

### 测试文件

`backend/app/agents/test_http_tools.py`

### 测试场景

1. ✅ 创建单个普通测试用例
2. ✅ 创建单个 BDD 测试用例
3. ✅ 更新测试用例
4. ✅ 批量创建测试用例

### 运行测试

```bash
cd backend
python -m app.agents.test_http_tools
```

**注意**：需要确保后端服务正在运行（http://localhost:8080）

## 📝 配置

### API 基础 URL

在 `backend/app/agents/tools.py` 中配置：

```python
# API 基础 URL（默认使用本地地址）
API_BASE_URL = "http://localhost:8080"  # 可以从环境变量读取
API_PREFIX = settings.api_prefix  # /api/v2
```

**建议**：从环境变量读取 API_BASE_URL，以支持不同的部署环境。

## 🚀 使用示例

### 智能体中使用

智能体会自动使用这些工具，无需手动调用。

### 手动调用

```python
from app.agents.tools import create_test_case_tool, batch_create_test_cases_tool

# 创建单个测试用例
result = await create_test_case_tool(
    project_identifier="PROJ-001",
    folder_id="folder-uuid",
    name="测试用例名称",
    # ...
)

# 批量创建测试用例
result = await batch_create_test_cases_tool(
    project_identifier="PROJ-001",
    folder_id="folder-uuid",
    test_cases=[...]
)
```

## 📚 相关文件

- `backend/app/agents/tools.py` - 工具函数实现
- `backend/app/agents/testcase_generator.py` - 智能体配置
- `backend/app/agents/test_http_tools.py` - 测试文件
- `backend/app/api/v2/test_cases.py` - HTTP API 接口

## 🎉 总结

本次重构成功实现了：

1. ✅ 降低了工具函数与内部服务的耦合度
2. ✅ 统一了接口调用方式（HTTP API）
3. ✅ 新增了批量创建测试用例的功能
4. ✅ 提供了完整的测试和文档

下一步可以考虑：
- 在后端添加批量创建的 API 接口以提高性能
- 添加重试机制和超时控制
- 从环境变量读取 API_BASE_URL

