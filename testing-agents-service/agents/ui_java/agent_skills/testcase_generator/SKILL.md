# 测试用例生成器 (Testcase Generator) Skill

基于测试计划生成结构化的功能测试用例，输出 Excel 格式，支持 UI 测试和全量测试两种模式。

## 核心职责

1. **分析测试计划**: 解析测试计划文档，提取测试场景和步骤
2. **生成功能测试用例**: 输出用于 UI 自动化的功能测试用例
3. **生成全量测试用例**: 输出包含所有类型（功能、边界、异常、安全等）的完整测试用例
4. **Excel 导出**: 将测试用例导出为标准 Excel 格式

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
1. 输入测试计划（Markdown 或结构化数据）
     ↓
2. 分析测试场景和步骤
     ↓
3. 生成测试用例数据结构
     ↓
4. 导出 UI 测试用例 Excel
     ↓
5. 导出全量测试用例 Excel
     ↓
6. 可选：基于 UI 测试用例生成 Java 代码
```

## 工具调用

### 1. 解析测试计划
```python
parse_test_plan(
    plan_path: str,           # 测试计划文件路径
    module_name: str          # 模块名称
) -> TestPlanData
```

### 2. 生成测试用例
```python
generate_test_cases(
    plan_data: TestPlanData,  # 测试计划数据
    mode: str = "ui"          # "ui" 或 "all"
) -> List[TestCase]
```

### 3. 导出 Excel
```python
export_to_excel(
    test_cases: List[TestCase],
    output_path: str,
    mode: str = "ui"          # "ui" 或 "all"
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

