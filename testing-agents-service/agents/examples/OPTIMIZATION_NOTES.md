# 智能体提示词优化说明

## 📝 优化概述

本次优化主要针对 `testcase_generator.py` 中的 `dynamic_prompt_fn` 函数，将前端传入的上下文信息嵌入到系统提示词中，确保智能体能够准确使用这些参数调用工具。

## 🎯 优化目标

1. **自动使用上下文参数**：智能体无需询问用户，直接使用前端传入的参数
2. **减少用户交互**：避免重复询问项目标识符、文件夹 ID 等信息
3. **提高准确性**：明确指示智能体使用正确的参数值
4. **增强可靠性**：通过详细的说明和示例，减少参数使用错误

## ✨ 主要改进

### 1. 新增上下文信息部分

在系统提示词的开头添加了 **"当前上下文信息"** 部分，包含：

```markdown
## 🎯 当前上下文信息（重要！）

**系统已自动配置以下参数，调用工具时必须使用这些值：**

- **项目标识符 (project_identifier)**: `{project_identifier}`
- **文件夹 ID (folder_id)**: `{folder_id}`
- **默认模板类型 (template)**: `{template_type}`
```

### 2. 详细的调用注意事项

添加了 4 条关键注意事项：

1. **必须使用上述参数**：明确要求使用上下文中的值
2. **不要询问用户**：这些参数已由前端自动传入
3. **模板类型**：根据 template_type 选择合适的格式
4. **参数验证**：如果参数为空，提示配置错误

### 3. 正确和错误示例

**✅ 正确的工具调用示例：**
```python
create_test_case_tool(
    project_identifier="{project_identifier}",  # 使用上下文中的值
    folder_id="{folder_id}",                    # 使用上下文中的值
    template="{template_type}",                 # 使用上下文中的默认模板
    name="用户登录功能测试",
    description="验证用户登录功能",
    ...
)
```

**❌ 错误的做法：**
- 不要询问用户 "请提供项目标识符"
- 不要使用硬编码的值如 "PROJ-001"
- 不要忽略上下文中的 template_type

### 4. 优化工作流程

在工作流程的第 4 步添加了明确的提醒：

```markdown
4. **创建测试用例**：使用 create_test_case_tool 创建测试用例
   - ⚠️ **必须使用上下文中的 project_identifier 和 folder_id**
   - ⚠️ **根据 template_type 选择合适的模板格式**
```

### 5. 优化示例对话

在示例对话中展示了如何使用上下文参数：

```markdown
[调用 create_test_case_tool，使用上下文中的参数：
 - project_identifier: "{project_identifier}"
 - folder_id: "{folder_id}"
 - template: "{template_type}"]
```

### 6. 更新注意事项

在注意事项中强调了上下文参数的使用：

```markdown
2. **使用上下文参数**：必须使用上下文中的 project_identifier 和 folder_id
3. **模板选择**：根据 template_type 选择合适的测试用例格式
```

## 📊 优化前后对比

### 优化前

```python
def dynamic_prompt_fn(request: ModelRequest) -> str:
    """动态生成测试用例系统提示词"""
    project_identifier = request.runtime.context.project_identifier
    folder_id = request.runtime.context.folder_id
    template_type = request.runtime.context.template_type

    system_prompt = """# 测试用例生成专家
    
你是一位专业的软件测试工程师...
```

**问题**：
- ❌ 虽然获取了上下文参数，但没有在提示词中明确说明
- ❌ 智能体可能不知道这些参数的存在
- ❌ 可能会询问用户提供这些参数
- ❌ 可能使用错误的参数值

### 优化后

```python
def dynamic_prompt_fn(request: ModelRequest) -> str:
    """动态生成测试用例系统提示词"""
    project_identifier = request.runtime.context.project_identifier
    folder_id = request.runtime.context.folder_id
    template_type = request.runtime.context.template_type

    # 构建上下文信息提示
    context_section = f"""
## 🎯 当前上下文信息（重要！）

**系统已自动配置以下参数，调用工具时必须使用这些值：**

- **项目标识符 (project_identifier)**: `{project_identifier}`
- **文件夹 ID (folder_id)**: `{folder_id}`
- **默认模板类型 (template)**: `{template_type}`
...
"""

    system_prompt = f"""# 测试用例生成专家
    
你是一位专业的软件测试工程师...

{context_section}
...
```

**优势**：
- ✅ 明确显示上下文参数的值
- ✅ 详细说明如何使用这些参数
- ✅ 提供正确和错误的示例
- ✅ 智能体能够准确调用工具

## 🔧 技术实现

### 动态字符串插值

使用 Python 的 f-string 将上下文参数嵌入到提示词中：

```python
context_section = f"""
- **项目标识符 (project_identifier)**: `{project_identifier}`
- **文件夹 ID (folder_id)**: `{folder_id}`
- **默认模板类型 (template)**: `{template_type}`
"""
```

### 提示词结构

```
系统提示词
├── 角色定位
├── 🎯 当前上下文信息（新增）
│   ├── 参数列表
│   ├── 调用注意事项
│   ├── 正确示例
│   └── 错误示例
├── 职责说明
├── 设计原则
├── 可用工具
├── 字段说明
├── 工作流程（优化）
├── 最佳实践
├── 示例对话（优化）
└── 注意事项（优化）
```

## 📈 预期效果

### 1. 减少错误

- 智能体不会使用错误的项目标识符或文件夹 ID
- 不会询问用户已经提供的参数
- 自动选择正确的模板类型

### 2. 提高效率

- 减少用户交互次数
- 直接开始创建测试用例
- 避免参数确认环节

### 3. 增强用户体验

- 流畅的对话体验
- 准确的测试用例创建
- 清晰的结果反馈

## 🧪 测试建议

### 测试场景 1: 普通测试用例

```python
context = TestCaseGeneratorContext(
    project_identifier="PROJ-001",
    folder_id="123e4567-e89b-12d3-a456-426614174000",
    template_type="test_case"
)

user_input = "为用户登录功能生成测试用例"
```

**预期**：智能体直接使用 `PROJ-001` 和指定的 folder_id，创建普通格式的测试用例

### 测试场景 2: BDD 测试用例

```python
context = TestCaseGeneratorContext(
    project_identifier="PROJ-002",
    folder_id="223e4567-e89b-12d3-a456-426614174000",
    template_type="test_case_bdd"
)

user_input = "为购物车功能生成测试用例"
```

**预期**：智能体使用 BDD 格式创建测试用例，包含 feature/scenario/background

### 测试场景 3: 参数为空

```python
context = TestCaseGeneratorContext(
    project_identifier="",
    folder_id="",
    template_type="test_case"
)

user_input = "生成测试用例"
```

**预期**：智能体提示 "系统配置错误，缺少必要的项目或文件夹信息"

## 📚 相关文件

- `backend/app/agents/testcase_generator.py` - 智能体主文件（已优化）
- `backend/app/agents/tools.py` - 工具函数定义
- `backend/app/agents/README.md` - 完整文档
- `backend/app/agents/example_usage.py` - 使用示例

## 🎉 总结

本次优化通过将上下文信息明确嵌入到系统提示词中，显著提高了智能体使用工具的准确性和可靠性。智能体现在能够：

1. ✅ 自动识别并使用前端传入的参数
2. ✅ 避免询问用户已提供的信息
3. ✅ 根据模板类型选择正确的格式
4. ✅ 在参数缺失时给出明确提示

这些改进将大大提升用户体验和系统的整体可用性。

