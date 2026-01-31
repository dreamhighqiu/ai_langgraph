# Java Playwright UI 测试 Agent 使用指南

## 🚀 快速开始

### 1. Agent 注册

Java UI 测试 Agent 已在 LangGraph 中注册为 `ui_java_agent`：

```json
{
  "ui_java_agent": {
    "path": "./agents/ui_java/agent.py:agent",
    "description": "Java Playwright UI 测试自动化 Agent"
  }
}
```

### 2. 启动 Agent

#### 方式一：通过 LangGraph CLI

```bash
# 启动 LangGraph 服务器
cd testing-agents-service
langgraph dev

# Agent 将在以下端点可用：
# http://localhost:2025/ui_java_agent
```

#### 方式二：通过 Python 代码

```python
from agents.ui_java.agent import agent

# 使用异步上下文管理器
async with agent() as ui_java_agent:
    result = await ui_java_agent.ainvoke({
        "messages": [
            {"role": "user", "content": "为登录页面创建测试计划"}
        ]
    })
    print(result)
```

## 📋 功能概览

### 三大核心技能

1. **Planner (规划器)** 📝
   - 分析 Web 应用界面
   - 识别测试场景
   - 生成详细测试计划（中文）

2. **Generator (生成器)** 🔧
   - 根据测试计划生成 Java 代码
   - 遵循 PageObject + Helper 模式
   - 使用 JUnit 5 + Playwright

3. **Healer (修复器)** 🔨
   - 识别失败的测试
   - 分析根本原因
   - 自动修复代码

## 💡 使用示例

### 示例 1: 创建测试计划

**用户输入**:
```
请为设备库存页面创建测试计划
URL: https://app.example.com/device-inventory
```

**Agent 响应**:
```
我将探索设备库存页面并创建测试计划...

[Planner Skill 启动]
- 导航到页面
- 探索 UI 元素
- 识别功能模块
- 设计测试场景

测试计划已生成：workspace/device-inventory-test-plan.md

计划包含：
✓ UI 元素验证测试
✓ 搜索功能测试
✓ 过滤功能测试（单/多过滤器）
✓ 排序功能测试（单/多字段）
✓ 数据加载验证
✓ 错误处理测试
```

### 示例 2: 生成 Java 测试代码

**用户输入**:
```
根据刚才的测试计划生成 Java 测试代码
输出文件: DeviceInventoryPageTest.java
```

**Agent 响应**:
```
我将根据测试计划生成 Java 测试代码...

[Generator Skill 启动]
- 读取测试计划
- 实时执行操作
- 记录定位器和步骤
- 生成 Java 代码

✅ 已生成文件：workspace/DeviceInventoryPageTest.java

代码特点：
✓ 继承 Hook 基类
✓ 使用 @Test 和 @Tag 注解
✓ PageObject 模式访问元素
✓ Helper 封装业务操作
✓ 清晰的中文注释
✓ 适当的等待策略
✓ Playwright Assertions

测试用例数量: 12
包含标签: @smoke, @functional, @filter
```

### 示例 3: 修复失败的测试

**用户输入**:
```
DeviceInventoryPageTest 中的 checkSortFunction 测试失败了
错误: TimeoutException - 等待元素超时
```

**Agent 响应**:
```
我将调试这个失败的测试...

[Healer Skill 启动]
- 运行测试定位失败点
- 捕获页面快照分析
- 检查元素定位器

🔍 问题诊断：
原因: 表格加载使用了异步请求，元素定位器在数据加载完成前就执行了

🔧 修复方案：
1. 在排序操作前添加表格数据等待
2. 更新定位器使用更健壮的策略

✅ 已修复文件：workspace/DeviceInventoryPageTest.java

修改内容：
+ helperContext.getCommonHelper().waitForTableData(TIMEOUT_SECONDS_15);
+ 使用 Role-based 定位器替代 CSS 选择器

重新运行测试... ✓ 通过
```

## 🎯 完整工作流

### 场景：为新功能创建自动化测试

```bash
# 第 1 步：创建测试计划
用户: 为用户管理页面创建测试计划，URL: https://app.example.com/users

Agent: [启动 Planner]
       ✓ 探索页面
       ✓ 识别功能（添加、删除、搜索、过滤用户）
       ✓ 生成测试计划

# 第 2 步：生成 PageObject
用户: 创建 UsersPage.java PageObject 类

Agent: [启动 Generator]
       ✓ 分析页面元素
       ✓ 生成 UsersPage.java
       ✓ 包含所有元素定位器

# 第 3 步：生成 Helper
用户: 创建 UsersHelper.java Helper 类

Agent: [启动 Generator]
       ✓ 封装业务操作
       ✓ 生成 UsersHelper.java
       ✓ 包含添加、删除、搜索等方法

# 第 4 步：生成测试用例
用户: 根据测试计划生成 UsersPageTest.java

Agent: [启动 Generator]
       ✓ 实时执行测试步骤
       ✓ 记录操作和断言
       ✓ 生成完整测试类

# 第 5 步：运行测试
# （在项目中运行 Maven 测试）
mvn test -Dtest=UsersPageTest

# 第 6 步：修复失败（如果有）
用户: testAddUser 失败了，请帮我修复

Agent: [启动 Healer]
       ✓ 调试测试
       ✓ 识别问题
       ✓ 修复代码
       ✓ 验证通过
```

## 🔧 配置说明

### Agent 配置

在 `config/settings.py` 中：

```python
# UI Java 测试工作目录配置
ui_java_workspace_root: str = "agents/ui_java/workspace"
ui_java_skills_root: str = "agents/ui_java/agent_skills"
```

### Skills 配置

Skills 定义位于：
- `agents/ui_java/agent_skills/planner/SKILL.md`
- `agents/ui_java/agent_skills/generator/SKILL.md`
- `agents/ui_java/agent_skills/healer/SKILL.md`

### MCP 配置

使用与 TypeScript UI Agent 相同的 Playwright MCP 服务：

```python
# 在 agent.py 中
client = MultiServerMCPClient({
    "playwright-test": mcp_settings.get_playwright_mcp_config()
})
```

## 📚 参考资料

### 代码风格指南
查看 `agent_skills/generator/references/java_test_style_guide_zh.md`

### 示例代码
查看 `agent_skills/generator/references/java/` 目录：
- `helper/Hook.java` - 测试基类
- `helper/UsersHelper.java` - Helper 示例
- `pageobject/CommonPage.java` - 通用页面对象
- `testcase/DeviceInventoryPageTest.java` - 完整测试套件

## 🎨 生成代码示例

### PageObject 类

```java
package com.example.pageobject;

import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;

public class UsersPage extends CommonPage {
    public final Locator pageTitle;
    public final Locator addUserButton;
    public final Locator searchBox;
    public final Locator userTable;
    
    public UsersPage(Page page) {
        super(page);
        this.pageTitle = page.getByRole(AriaRole.HEADING, 
            new Page.GetByRoleOptions().setName("Users"));
        this.addUserButton = page.getByRole(AriaRole.BUTTON,
            new Page.GetByRoleOptions().setName("Add User"));
        // ... 更多元素
    }
    
    public Locator getUserRowByEmail(String email) {
        return page.locator(String.format("tr:has-text('%s')", email));
    }
}
```

### Helper 类

```java
package com.example.helper;

import com.example.context.*;

public class UsersHelper {
    private final PagesContext pagesContext;
    private final HelperContext helperContext;
    
    public UsersHelper(PagesContext pagesContext, HelperContext helperContext) {
        this.pagesContext = pagesContext;
        this.helperContext = helperContext;
    }
    
    public void addNewUser(String email) {
        // 1. 点击添加用户按钮
        CommonMethod.clickElement(
            pagesContext.getUsersPage().addUserButton,
            TIMEOUT_SECONDS_15
        );
        
        // 2. 输入邮箱
        CommonMethod.input(
            pagesContext.getUsersPage().emailInput,
            email,
            TIMEOUT_SECONDS_15
        );
        
        // 3. 提交
        CommonMethod.clickElement(
            pagesContext.getUsersPage().submitButton,
            TIMEOUT_SECONDS_15
        );
        
        // 4. 等待成功消息
        helperContext.getCommonHelper().waitForToast(TIMEOUT_SECONDS_15);
    }
}
```

### 测试类

```java
package com.example.testcase;

import com.epam.reportportal.junit5.ReportPortalExtension;
import com.example.helper.Hook;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.extension.ExtendWith;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

/**
 * 用户管理页面测试套件
 */
@ExtendWith(ReportPortalExtension.class)
class UsersPageTest extends Hook {

    @Test
    @Tag("smoke")
    void verifyUsersPageUIElements() throws InterruptedException {
        // 1. 验证页面标题
        assertThat(pagesContext.getUsersPage().pageTitle).isVisible();
        
        // 2. 验证添加用户按钮
        assertThat(pagesContext.getUsersPage().addUserButton).isVisible();
        
        // 3. 验证搜索框
        assertThat(pagesContext.getUsersPage().searchBox).isVisible();
        
        // 4. 验证用户表格
        assertThat(pagesContext.getUsersPage().userTable).isVisible();
    }
    
    @Test
    @Tag("functional")
    void testAddNewUser() throws InterruptedException {
        String testEmail = "test_" + System.currentTimeMillis() + "@example.com";
        
        // 使用 Helper 封装的业务操作
        usersHelper.addNewUser(testEmail);
        
        // 验证用户添加成功
        usersHelper.verifyUserInListWithStatus(testEmail, "Active");
        
        // 清理测试数据
        usersHelper.deleteUser(testEmail);
    }
}
```

## ⚙️ 高级用法

### 自定义 System Prompt

如需修改 Agent 行为，编辑 `agent.py` 中的 `SYSTEM_PROMPT`。

### 添加新的 Skill

1. 在 `agent_skills/` 下创建新目录
2. 添加 `SKILL.md` 文件
3. 在 `agent.py` 中更新 `skills_middleware` 的 `sources`

### 集成到 CI/CD

```yaml
# .gitlab-ci.yml 示例
test_java_ui:
  stage: test
  script:
    # 1. 启动 LangGraph 服务
    - langgraph dev &
    
    # 2. 调用 Agent 生成测试
    - curl -X POST http://localhost:2025/ui_java_agent/invoke \
        -H "Content-Type: application/json" \
        -d '{"messages": [{"role": "user", "content": "生成测试用例"}]}'
    
    # 3. 运行生成的测试
    - mvn test
```

## 🐛 故障排除

### 问题 1: Agent 无法启动

**检查**:
- LangGraph 服务是否运行？
- 环境变量是否正确配置？
- MCP 服务器是否可用？

**解决**:
```bash
# 检查服务状态
langgraph status

# 查看日志
langgraph logs ui_java_agent
```

### 问题 2: Skills 未加载

**检查**:
- Skills 路径是否正确？
- SKILL.md 格式是否正确？

**解决**:
```python
# 在 agent.py 中添加调试日志
print(f"Skills root: {skills_root}")
print(f"Skills sources: {skills_middleware.sources}")
```

### 问题 3: 生成的代码有错误

**解决**:
- 使用 Healer Skill 自动修复
- 或查看风格指南手动调整
- 或提供反馈改进 Generator

## 📞 获取支持

- **文档**: 查看 `README.md` 和风格指南
- **示例**: 参考 `agent_skills/generator/references/java/`
- **问题**: 在项目仓库提 Issue

---

**开始使用 Java Playwright UI 测试 Agent，享受自动化测试的乐趣！** 🎉

