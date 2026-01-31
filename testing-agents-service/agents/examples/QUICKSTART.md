# 快速开始指南

## 🚀 5 分钟快速上手

### 前置条件

1. ✅ PostgreSQL 数据库已启动
2. ✅ MongoDB 数据库已启动
3. ✅ 已安装项目依赖 (`pip install -r requirements.txt`)
4. ✅ DeepSeek API Key 已配置

### 步骤 1: 配置环境变量

确保 `.env` 文件包含以下配置：

```env
# DeepSeek API
DEEPSEEK_API_KEY=your-api-key-here

# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-password
POSTGRES_DB=ai_test_management

# MongoDB
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DB=ai_test_management
```

### 步骤 2: 准备项目和文件夹

确保你有一个有效的项目和文件夹：

```python
# 获取项目标识符和文件夹 ID
# 方式 1: 通过 API 查询
# GET /api/v2/projects
# GET /api/v2/projects/{project_id}/folders

# 方式 2: 直接从数据库查询
# SELECT identifier FROM projects WHERE name = '你的项目名';
# SELECT id FROM folders WHERE name = '你的文件夹名';
```

### 步骤 3: 创建第一个测试用例

```python
import asyncio
from app.agents.tools import create_test_case_tool

async def create_first_testcase():
    result = await create_test_case_tool(
        project_identifier="PROJ-001",  # 替换为你的项目标识符
        folder_id="your-folder-uuid",   # 替换为你的文件夹 UUID
        name="我的第一个测试用例",
        description="这是一个测试用例示例",
        priority="medium",
        status="draft",
        case_type="functional",
        test_case_steps=[
            {"step": "步骤 1", "result": "预期结果 1"},
            {"step": "步骤 2", "result": "预期结果 2"},
        ],
        tags=["示例", "快速开始"]
    )
    
    if result["success"]:
        print(f"✅ 成功创建测试用例: {result['data']['identifier']}")
        print(f"   名称: {result['data']['name']}")
        print(f"   优先级: {result['data']['priority']}")
    else:
        print(f"❌ 创建失败: {result['message']}")
    
    return result

# 运行
asyncio.run(create_first_testcase())
```

### 步骤 4: 使用智能体生成测试用例

```python
from app.agents.testcase_generator import testcase_generator_agent, TestCaseGeneratorContext

async def use_agent():
    # 设置上下文
    context = TestCaseGeneratorContext(
        project_identifier="PROJ-001",
        folder_id="your-folder-uuid",
    )
    
    # 用户需求
    user_input = """
    请为用户注册功能生成测试用例。
    
    要求：
    - 用户名长度 6-20 个字符
    - 密码长度 8-20 个字符
    - 邮箱格式验证
    """
    
    # 调用智能体
    result = await testcase_generator_agent.ainvoke({
        "messages": [{"role": "user", "content": user_input}],
        "context": context
    })
    
    print(result)

asyncio.run(use_agent())
```

## 📚 常用场景

### 场景 1: 创建登录测试用例

```python
result = await create_test_case_tool(
    project_identifier="PROJ-001",
    folder_id="your-folder-uuid",
    name="用户使用正确凭据登录成功",
    description="验证用户输入正确的用户名和密码后能够成功登录",
    preconditions="用户已注册且账号状态正常",
    priority="critical",
    status="active",
    case_type="functional",
    test_case_steps=[
        {"step": "打开登录页面", "result": "页面正常显示"},
        {"step": "输入用户名: testuser", "result": "输入框接受输入"},
        {"step": "输入密码: Test@123", "result": "密码显示为密文"},
        {"step": "点击登录按钮", "result": "成功登录并跳转到首页"}
    ],
    tags=["登录", "核心功能", "正向测试"]
)
```

### 场景 2: 创建 BDD 测试用例

```python
result = await create_test_case_tool(
    project_identifier="PROJ-001",
    folder_id="your-folder-uuid",
    name="用户添加商品到购物车",
    template="test_case_bdd",
    priority="high",
    status="active",
    feature="购物车管理",
    scenario="""
Scenario: 用户添加商品到购物车
  Given 用户已登录
  And 用户在商品详情页
  When 用户点击"加入购物车"按钮
  Then 商品成功添加到购物车
  And 购物车图标显示数量
    """,
    tags=["购物车", "BDD"]
)
```

### 场景 3: 更新测试用例

```python
from app.agents.tools import update_test_case_tool

result = await update_test_case_tool(
    project_identifier="PROJ-001",
    test_case_identifier="TC-1234",
    priority="critical",
    status="active",
    tags=["登录", "核心功能", "回归测试"]
)
```

## 🔧 故障排查

### 问题 1: 找不到项目

```
错误: 项目 PROJ-001 不存在
解决: 检查项目标识符是否正确，或创建新项目
```

### 问题 2: 文件夹 ID 无效

```
错误: 文件夹不存在或不属于该项目
解决: 确保 folder_id 是有效的 UUID 且属于指定项目
```

### 问题 3: 数据库连接失败

```
错误: 数据库连接失败
解决: 
1. 检查 PostgreSQL 和 MongoDB 是否运行
2. 检查 .env 文件中的数据库配置
3. 测试数据库连接: psql -h localhost -U postgres
```

## 📖 下一步

- 📘 阅读 [README.md](./README.md) 了解详细功能
- 💻 查看 [example_usage.py](./example_usage.py) 学习更多示例
- 🧪 运行 [test_tools.py](./test_tools.py) 进行测试
- 📊 查看 [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md) 了解实现细节

## 💡 提示

1. **使用正确的 UUID 格式**: 文件夹 ID 必须是有效的 UUID
2. **检查枚举值**: priority, status, case_type 等必须使用有效的枚举值
3. **测试步骤格式**: 每个步骤必须包含 `step` 字段，`result` 可选
4. **BDD 格式**: 使用 BDD 模板时，`feature` 和 `scenario` 是必填的
5. **标签使用**: 使用有意义的标签便于后续检索和分类

## 🎉 完成！

现在你已经可以开始使用测试用例生成工具了！如有问题，请查看文档或联系开发团队。

