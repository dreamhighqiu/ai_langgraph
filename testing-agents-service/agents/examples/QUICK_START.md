# 快速开始指南

## 🚀 快速开始

### 1. 确保后端服务运行

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8080
```

### 2. 测试工具函数

```bash
cd backend
python -m app.agents.test_http_tools
```

### 3. 在前端使用智能体

1. 打开前端应用
2. 进入项目的测试用例页面
3. 点击 "AI 生成用例" 按钮
4. 在对话框中输入需求，例如：
   - "为用户登录功能生成 5 个测试用例"
   - "创建一个 BDD 格式的用户注册测试用例"
   - "批量生成购物车功能的测试用例"

## 📝 工具说明

### 1. create_test_case_tool - 创建单个测试用例

**用途**：创建一个测试用例

**参数**：
- `project_identifier`: 项目标识符（从上下文自动获取）
- `folder_id`: 文件夹 ID（从上下文自动获取）
- `name`: 测试用例名称（必填）
- `description`: 描述（可选）
- `priority`: 优先级（可选，默认 medium）
- `template`: 模板类型（可选，默认 test_case）
- `test_case_steps`: 测试步骤列表（可选）
- 其他字段...

**示例**：
```python
result = await create_test_case_tool(
    project_identifier="PROJ-001",
    folder_id="folder-uuid",
    name="用户登录功能测试",
    description="验证用户登录功能",
    priority="high",
    test_case_steps=[
        {"step": "打开登录页面", "result": "页面正常显示"},
        {"step": "输入用户名和密码", "result": "输入成功"},
        {"step": "点击登录按钮", "result": "成功登录"}
    ]
)
```

### 2. update_test_case_tool - 更新测试用例

**用途**：更新已有的测试用例

**参数**：
- `project_identifier`: 项目标识符（从上下文自动获取）
- `test_case_identifier`: 测试用例标识符（必填）
- 其他需要更新的字段（可选）

**示例**：
```python
result = await update_test_case_tool(
    project_identifier="PROJ-001",
    test_case_identifier="TC-1234",
    priority="critical",
    status="active",
    description="更新后的描述"
)
```

### 3. batch_create_test_cases_tool - 批量创建测试用例

**用途**：一次性创建多个测试用例

**参数**：
- `project_identifier`: 项目标识符（从上下文自动获取）
- `folder_id`: 文件夹 ID（从上下文自动获取）
- `test_cases`: 测试用例列表（必填）

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
```

**返回结果**：
```python
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

## 🎯 智能体使用场景

### 场景 1: 创建单个测试用例

**用户输入**：
```
为用户登录功能创建一个测试用例
```

**智能体行为**：
1. 分析需求
2. 调用 `create_test_case_tool`
3. 返回创建结果

### 场景 2: 批量创建测试用例

**用户输入**：
```
为用户登录功能生成 5 个测试用例，包括正常登录、错误密码、空用户名等场景
```

**智能体行为**：
1. 分析需求，识别需要创建多个测试用例
2. 设计 5 个测试用例
3. 调用 `batch_create_test_cases_tool`
4. 返回批量创建结果

### 场景 3: 创建 BDD 测试用例

**用户输入**：
```
创建一个 BDD 格式的用户注册测试用例
```

**智能体行为**：
1. 识别需要使用 BDD 模板
2. 调用 `create_test_case_tool`，设置 `template="test_case_bdd"`
3. 填写 `feature`、`scenario`、`background` 字段
4. 返回创建结果

## 🔧 配置

### API 基础 URL

在 `backend/app/agents/tools.py` 中：

```python
# API 基础 URL（默认使用本地地址）
API_BASE_URL = "http://localhost:8080"
API_PREFIX = settings.api_prefix  # /api/v2
```

**生产环境配置**：

建议从环境变量读取：

```python
import os

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8080")
```

## 📊 工作流程

```
用户输入
    ↓
智能体分析需求
    ↓
选择合适的工具
    ↓
构建请求参数（使用上下文中的 project_identifier 和 folder_id）
    ↓
调用工具函数
    ↓
工具函数发送 HTTP 请求
    ↓
FastAPI 接口处理请求
    ↓
返回结果
    ↓
智能体向用户报告结果
```

## 🧪 测试检查清单

- [ ] 后端服务正在运行（http://localhost:8080）
- [ ] 可以访问 API 文档（http://localhost:8080/docs）
- [ ] 测试创建单个测试用例
- [ ] 测试创建 BDD 测试用例
- [ ] 测试更新测试用例
- [ ] 测试批量创建测试用例
- [ ] 前端可以正常调用智能体
- [ ] 上下文信息正确传递

## 📚 相关文档

- `HTTP_TOOLS_REFACTORING.md` - 详细的重构文档
- `IMPLEMENTATION_SUMMARY_V2.md` - 实现总结
- `README.md` - 完整的功能文档
- `test_http_tools.py` - 测试文件

## ❓ 常见问题

### Q1: 工具调用失败，提示网络错误

**A**: 检查后端服务是否正在运行：
```bash
curl http://localhost:8080/api/v2/health
```

### Q2: 批量创建时部分失败

**A**: 查看返回结果中的 `results` 字段，每个测试用例的创建结果都会单独记录。

### Q3: 智能体没有使用上下文中的参数

**A**: 检查：
1. 前端是否正确传递了 context
2. 智能体的提示词是否包含上下文信息
3. 查看智能体的调用日志

## 🎉 开始使用

现在你可以开始使用新的工具了！

1. 启动后端服务
2. 打开前端应用
3. 在测试用例页面使用 AI 生成功能
4. 享受智能化的测试用例生成体验！

