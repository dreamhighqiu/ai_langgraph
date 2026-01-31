# 测试用例生成智能体

## 概述

测试用例生成智能体是一个基于 LangChain 的 AI 智能体，能够根据需求文档、用户故事或功能描述自动生成高质量的测试用例。

## 功能特性

- ✅ 自动分析需求并生成测试用例
- ✅ 支持普通测试用例和 BDD 测试用例两种格式
- ✅ 覆盖正常流程、异常流程、边界条件等多种场景
- ✅ 自动设置合理的优先级和测试类型
- ✅ 支持测试用例的创建和更新
- ✅ 智能添加标签和分类

## 架构设计

```
┌─────────────────────────────────────────────────────────┐
│                  测试用例生成智能体                        │
│                (testcase_generator.py)                   │
└─────────────────────────────────────────────────────────┘
                            │
                            │ 使用
                            ▼
┌─────────────────────────────────────────────────────────┐
│                      工具集 (tools.py)                    │
├─────────────────────────────────────────────────────────┤
│  • create_test_case_tool - 创建测试用例                   │
│  • update_test_case_tool - 更新测试用例                   │
└─────────────────────────────────────────────────────────┘
                            │
                            │ 调用
                            ▼
┌─────────────────────────────────────────────────────────┐
│              测试用例服务 (TestCaseService)                │
│                (test_case_service.py)                    │
└─────────────────────────────────────────────────────────┘
                            │
                            │ 访问
                            ▼
┌─────────────────────────────────────────────────────────┐
│                  测试用例 API 接口                         │
│                  (test_cases.py)                         │
│  • POST /projects/{id}/folders/{id}/test-cases          │
│  • PATCH /projects/{id}/test-cases/{id}                 │
└─────────────────────────────────────────────────────────┘
```

## 工具说明

### 1. create_test_case_tool

创建新的测试用例。

**参数**：
- `project_identifier` (必填): 项目标识符，如 'PROJ-001'
- `folder_id` (必填): 文件夹 UUID
- `name` (必填): 测试用例名称
- `description` (可选): 测试用例描述
- `preconditions` (可选): 前置条件
- `priority` (可选): 优先级 (critical/high/medium/low)
- `status` (可选): 状态 (draft/active/in_review/rejected/outdated)
- `case_type` (可选): 测试类型
- `template` (可选): 模板类型 (test_case/test_case_bdd)
- `test_case_steps` (可选): 测试步骤列表（普通测试用例）
- `feature` (可选): BDD Feature（BDD 测试用例）
- `scenario` (可选): BDD Scenario（BDD 测试用例）
- 其他字段...

**返回**：
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "identifier": "TC-1234",
    "name": "测试用例名称",
    "priority": "high",
    "status": "draft",
    "created_at": "2024-01-01T00:00:00"
  },
  "message": "测试用例 TC-1234 创建成功"
}
```

### 2. update_test_case_tool

更新现有测试用例。

**参数**：
- `project_identifier` (必填): 项目标识符
- `test_case_identifier` (必填): 测试用例标识符，如 'TC-1234'
- 其他字段均为可选，只更新提供的字段

**返回**：
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "identifier": "TC-1234",
    "name": "更新后的名称",
    "version": 2,
    "updated_at": "2024-01-01T00:00:00"
  },
  "message": "测试用例 TC-1234 更新成功"
}
```

## 使用示例

### 示例 1: 基本使用

```python
import asyncio
from app.agents.testcase_generator import testcase_generator_agent, TestCaseGeneratorContext

async def main():
    # 设置上下文
    context = TestCaseGeneratorContext(
        project_identifier="PROJ-001",
        folder_id="123e4567-e89b-12d3-a456-426614174000",
        current_user_id="00000000-0000-0000-0000-000000000001"
    )
    
    # 用户需求
    user_input = """
    请为用户登录功能生成测试用例。
    
    功能描述：
    - 用户可以使用用户名和密码登录系统
    - 支持记住密码功能
    - 登录失败3次后锁定账号
    - 支持找回密码功能
    """
    
    # 调用智能体
    result = await testcase_generator_agent.ainvoke({
        "messages": [{"role": "user", "content": user_input}],
        "context": context
    })
    
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

### 示例 2: 生成 BDD 测试用例

```python
user_input = """
请使用 BDD 格式为购物车功能生成测试用例。

场景：
1. 用户添加商品到购物车
2. 用户修改购物车商品数量
3. 用户删除购物车商品
"""

# 智能体会自动识别并使用 BDD 模板
```

## 最佳实践

### 1. 提供清晰的需求描述

✅ 好的需求描述：
```
请为用户注册功能生成测试用例。

功能要求：
- 用户名长度 6-20 个字符
- 密码长度 8-20 个字符，必须包含字母和数字
- 邮箱格式验证
- 手机号格式验证
- 注册成功后自动登录
```

❌ 不好的需求描述：
```
帮我生成一些测试用例
```

### 2. 指定测试重点

```
请为支付功能生成测试用例，重点关注：
1. 支付金额的边界条件
2. 支付失败的异常处理
3. 并发支付的场景
```

### 3. 使用合适的模板

- **普通测试用例**：适用于传统的步骤式测试
- **BDD 测试用例**：适用于行为驱动开发，更关注业务场景

## 注意事项

1. **上下文信息**：确保提供正确的 `project_identifier` 和 `folder_id`
2. **权限控制**：确保 `current_user_id` 有创建测试用例的权限
3. **数据库连接**：确保 PostgreSQL 和 MongoDB 连接正常
4. **API Key**：确保 DeepSeek API Key 配置正确
5. **错误处理**：工具调用失败时会返回错误信息，需要适当处理

## 扩展开发

### 添加新工具

1. 在 `tools.py` 中定义新的工具函数
2. 添加到 `TESTCASE_TOOLS` 列表
3. 在智能体提示词中说明新工具的用途

### 自定义提示词

修改 `testcase_generator.py` 中的 `dynamic_prompt_fn` 函数来自定义系统提示词。

## 故障排查

### 问题 1: 工具调用失败

**错误信息**: "创建测试用例失败: 项目不存在"

**解决方案**: 检查 `project_identifier` 是否正确

### 问题 2: 数据库连接错误

**错误信息**: "数据库连接失败"

**解决方案**: 
1. 检查 PostgreSQL 和 MongoDB 是否运行
2. 检查 `.env` 文件中的数据库配置
3. 确保数据库已初始化

### 问题 3: API Key 错误

**错误信息**: "Invalid API Key"

**解决方案**: 检查 `DEEPSEEK_API_KEY` 环境变量是否正确设置

