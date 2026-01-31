# 测试用例生成器 (Testcase Generator) Skill

基于测试计划生成结构化的功能测试用例，输出 Excel 格式，支持 UI 测试和全量测试两种模式。

## 核心原则

**AI 负责理解，Tools 负责执行！**

- **AI 的职责**: 理解测试计划内容，智能提取测试场景、步骤、预期结果，构造结构化数据
- **Tools 的职责**: 接收 AI 构造的数据，执行固定的导出操作（Excel、保存文件）

**禁止使用硬编码解析器！** AI 本身就能理解任何格式的测试计划。

## 核心职责

1. **理解测试计划**: AI 阅读并理解测试计划文档，提取测试场景和步骤
2. **智能构造数据**: AI 将理解的内容转换为结构化的测试用例 JSON
3. **调用导出工具**: 使用 `save_test_cases_data` 和 `export_testcases_to_excel` 工具导出

## 输出类型

### 1. 功能测试用例 (UI 测试)
- **用途**: 用于生成 Java UI 自动化测试代码
- **内容**: 正向功能测试、基本 UI 验证
- **优先级**: P0/P1 为主
- **文件**: `{模块名}_UI_TestCases.xlsx`

### 2. 全量测试用例 (完整测试)
- **用途**: 供测试团队执行手工测试和其他类型测试
- **内容**: 功能测试、边界值测试、异常测试、安全测试、性能测试
- **优先级**: P0-P3 全覆盖
- **文件**: `{模块名}_All_TestCases.xlsx`

## Excel 格式规范

### Sheet 1: 测试用例列表
| 列名 | 说明 | 示例 |
|------|------|------|
| 用例ID | 唯一标识 | TC_LOGIN_AUTH_001 |
| 模块 | 所属功能模块 | 用户登录 |
| 用例标题 | 测试用例名称 | 正常登录-使用有效凭据 |
| 优先级 | P0/P1/P2/P3 | P0 |
| 测试类型 | functional/ui/boundary/negative/security | functional |
| 前置条件 | 执行前的条件 | 用户已注册，在登录页面 |
| 测试步骤 | 详细操作步骤 | 1. 输入用户名 2. 输入密码... |
| 预期结果 | 期望的测试结果 | 登录成功，跳转首页 |
| 测试数据 | 测试所需数据 | username: test@test.com |
| 定位器 | Playwright 定位器（UI测试用） | page.getByRole("button") |
| 标签 | 分类标签 | smoke, regression |
| 状态 | 执行状态 | 未执行/通过/失败 |

### Sheet 2: 统计摘要
- 总用例数
- 按优先级统计
- 按类型统计
- 按模块统计

## 使用流程

```
1. AI 阅读测试计划（Markdown 格式）
     ↓
2. AI 理解并提取测试场景、步骤、预期结果
     ↓
3. AI 构造测试用例 JSON 数据
     ↓
4. 调用 save_test_cases_data(test_cases, module_name)
     ↓
5. 调用 export_testcases_to_excel(testcases_json) 导出 Excel
     ↓
6. 可选：生成 Java 代码（使用 generator skill）
```

## AI 构造测试用例数据

### 测试用例 JSON 结构

AI 应该构造如下格式的 JSON 数组：

```json
[
    {
        "id": "TC_MODULE_001",
        "module": "模块名称",
        "title": "测试场景标题",
        "priority": "P0",
        "type": "functional",
        "preconditions": ["前置条件1", "前置条件2"],
        "steps_detail": [
            {
                "order": 1,
                "action": "打开目标页面",
                "expected": "页面加载成功",
                "locator": "browser_navigate 获取的定位器",
                "data": "测试数据（可选）"
            },
            {
                "order": 2,
                "action": "在搜索框输入关键词",
                "expected": "关键词显示在输入框中",
                "locator": "#search-input",
                "data": "测试自动化"
            }
        ],
        "expected_result": "整体预期结果",
        "tags": ["smoke", "functional"],
        "test_data": {
            "keyword": "测试自动化",
            "expected_count": 10
        },
        "url": "https://example.com"
    }
]
```

### 字段说明

| 字段 | 必填 | 说明 |
|------|------|------|
| id | ✅ | 唯一标识，格式: TC_模块_序号 |
| module | ✅ | 所属模块 |
| title | ✅ | 测试场景标题 |
| priority | ✅ | 优先级: P0/P1/P2/P3 |
| type | ✅ | 类型: functional/ui/boundary/negative/security |
| steps_detail | ✅ | 步骤数组，每步包含 order, action, expected |
| expected_result | ✅ | 整体预期结果 |
| preconditions | 可选 | 前置条件数组 |
| tags | 可选 | 标签数组 |
| test_data | 可选 | 测试数据对象 |
| locator | 可选 | Playwright 定位器（从 browser_snapshot 获取） |
| url | 可选 | 测试页面 URL |

### 优先级定义

- **P0**: 阻塞级 - 核心功能，必须通过
- **P1**: 高优先级 - 重要功能
- **P2**: 中优先级 - 一般功能
- **P3**: 低优先级 - 边缘功能

### 测试类型定义

- **functional**: 功能测试
- **ui**: UI 测试
- **smoke**: 冒烟测试
- **boundary**: 边界值测试
- **negative**: 异常/负向测试
- **security**: 安全测试

## 工具调用

### 1. 保存测试用例数据
```python
save_test_cases_data(
    test_cases: str,    # AI 构造的 JSON 数组
    module_name: str    # 模块名称
) -> str  # 返回保存结果
```

### 2. 导出 Excel
```python
export_testcases_to_excel(
    testcases_json: str,  # save_test_cases_data 的返回值
    filename: str = "",   # 可选，默认自动生成
    module_name: str = "" # 模块名称
) -> str  # 返回文件路径
```

## 示例

### 输入：测试计划片段
```markdown
## 1. 登录功能

### 1.1 正常登录
- 前置条件：用户已注册
- 步骤：
  1. 打开登录页面
  2. 输入正确用户名
  3. 输入正确密码
  4. 点击登录按钮
- 预期：登录成功，跳转首页
```

### 输出：UI 测试用例 Excel
| 用例ID | 模块 | 用例标题 | 优先级 | 测试类型 | 测试步骤 | 预期结果 |
|--------|------|----------|--------|----------|----------|----------|
| TC_LOGIN_001 | 登录 | 正常登录-有效凭据 | P0 | functional | 1.打开登录页面 2.输入用户名... | 登录成功 |

## 与 Generator Skill 的协作

生成的 UI 测试用例可以直接传递给 Generator Skill，用于生成对应的 Java 自动化测试代码：

```java
@Test
@Tag("smoke")
void testNormalLogin() {
    // 基于测试用例 TC_LOGIN_001 生成
    // 步骤 1: 打开登录页面
    page.navigate(BASE_URL + "/login");
    
    // 步骤 2: 输入用户名
    page.getByLabel("用户名").fill("test@test.com");
    
    // 步骤 3: 输入密码
    page.getByLabel("密码").fill("ValidPass123!");
    
    // 步骤 4: 点击登录
    page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("登录")).click();
    
    // 验证结果
    assertThat(page).hasURL(Pattern.compile(".*/dashboard"));
}
```

## 质量标准

1. **完整性**: 覆盖测试计划中的所有场景
2. **可执行性**: 每个用例都能独立执行
3. **可追溯性**: 用例ID与测试计划对应
4. **标准化**: 遵循统一的格式规范
5. **可维护性**: 定位器信息便于后续维护

## 参考文件

- `references/test_case_template.xlsx` - Excel 模板
- `references/test_case_examples.md` - 用例示例

