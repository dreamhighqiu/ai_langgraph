# Java Playwright UI 自动化测试 Agent Skills

## 📋 概述

本目录包含基于 **Java + Playwright** 的 UI 自动化测试 Agent Skills，用于创建、生成和维护高质量的自动化测试用例。

### 设计理念

- **中文优先**: 所有文档和说明使用中文，便于国内团队阅读和使用
- **Skills 模式**: 采用 DeepAgents Skills 架构，每个 Agent 专注于特定任务
- **Java 生态**: 基于 Java + Playwright + JUnit 5 技术栈
- **最佳实践**: 遵循 PageObject 模式、Helper 模式等测试自动化最佳实践
- **可维护性**: 代码结构清晰，易于扩展和维护

## 🎯 核心 Agent Skills

本项目包含三个核心 Agent Skills：

### 1. **Planner (规划器)**
📁 `planner/SKILL.md`

**职责**: 测试计划设计和场景规划

**能力**:
- 探索和分析 Web 应用界面
- 识别关键用户流程和交互元素
- 设计全面的测试场景（正向、边界、错误处理）
- 生成结构化的测试计划文档
- 考虑 Java Playwright 技术特点

**输出**: Markdown 格式的测试计划，包含详细的测试场景和步骤

**使用场景**:
- 新功能的测试设计
- 回归测试计划更新
- 测试覆盖率分析

---

### 2. **Generator (生成器)**
📁 `generator/SKILL.md`

**职责**: 自动化测试代码生成

**能力**:
- 根据测试计划生成 Java 测试代码
- 实时执行并记录用户操作
- 生成符合 Java 代码规范的测试类
- 应用 PageObject 和 Helper 设计模式
- 使用 Playwright Assertions 和 JUnit 5
- 生成可维护的、可读的测试代码

**输出**: 完整的 Java 测试类文件

**代码特点**:
- 继承自 `Hook` 基类
- 使用 `@Test` 和 `@Tag` 注解
- 清晰的注释和文档
- 适当的异常处理
- 显式等待策略

**使用场景**:
- 快速生成测试代码
- 自动化测试开发
- 测试用例模板创建

---

### 3. **Healer (修复器)**
📁 `healer/SKILL.md`

**职责**: 测试失败调试和修复

**能力**:
- 运行测试并识别失败用例
- 调试模式下逐步分析问题
- 根本原因分析（定位器、时序、断言等）
- 智能修复测试代码
- 更新选择器和等待策略
- 验证修复效果

**修复类型**:
- 元素定位器更新（UI 变化）
- 时序和同步问题（添加等待）
- 断言更新（预期值变化）
- 动态数据处理（正则表达式）

**使用场景**:
- CI/CD 测试失败分析
- 应用更新后的测试维护
- 提高测试稳定性

## 📚 参考资料

### 风格指南
📄 `generator/references/java_test_style_guide_zh.md`

**内容**:
- Java 测试用例编写规范
- 命名约定和代码组织
- PageObject 和 Helper 模式详解
- 断言和等待最佳实践
- 测试数据管理
- 完整的代码示例

### Java 参考代码
📁 `generator/references/java/`

包含完整的参考实现：

#### Helper 类
- **Hook.java**: 测试基类，提供 Playwright 生命周期管理
  - 浏览器启动和关闭
  - 页面对象初始化
  - 登录处理和会话管理
  - 截图和追踪
  - 测试清理

- **UsersHelper.java**: 用户管理业务操作封装
  - 添加用户
  - 删除用户
  - 搜索和验证
  - 测试数据清理

#### PageObject 类
- **CommonPage.java**: 通用页面元素
  - 顶部导航栏
  - 左侧菜单
  - 搜索和过滤
  - 表格操作
  - 动态定位器方法

- **DeviceInventoryPage.java**: 设备库存页面
  - 页面特有元素
  - 设备相关操作
  - 表格数据访问

#### TestCase 类
- **DeviceInventoryPageTest.java**: 完整的测试套件
  - UI 元素验证
  - 排序功能测试
  - 过滤功能测试
  - 多过滤器组合测试

## 🏗️ 技术栈

### 核心技术
- **Java**: JDK 11+
- **Playwright for Java**: 浏览器自动化
- **JUnit 5**: 测试框架
- **Maven/Gradle**: 构建工具

### 可选集成
- **ReportPortal**: 测试报告平台
- **Allure**: 测试报告生成
- **Selenium Grid**: 分布式执行（可选）

### 设计模式
- **PageObject Pattern**: 页面对象模式
- **Helper Pattern**: 业务操作封装
- **Hook Pattern**: 测试生命周期管理
- **Context Pattern**: 依赖注入和管理

## 🚀 快速开始

### 1. 启动 Agent

#### 通过 LangGraph CLI (推荐)

```bash
# 在 testing-agents-service 目录下
cd testing-agents-service

# 启动 LangGraph 开发服务器
langgraph dev

# Agent 将在以下端点可用：
# http://localhost:2025/ui_java_agent
```

#### 通过 Python 代码

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

### 2. 使用 Planner 创建测试计划

```bash
# 启动 Planner Agent
agent-runner run ui_java/planner

# Planner 会:
# 1. 探索目标应用
# 2. 识别测试场景
# 3. 生成测试计划文档
```

### 2. 使用 Generator 生成测试代码

```bash
# 启动 Generator Agent
agent-runner run ui_java/generator --plan=test-plan.md

# Generator 会:
# 1. 读取测试计划
# 2. 实时执行操作
# 3. 生成 Java 测试代码
```

### 3. 运行测试并使用 Healer 修复失败

```bash
# 运行测试
mvn test

# 如果有失败，启动 Healer Agent
agent-runner run ui_java/healer

# Healer 会:
# 1. 识别失败的测试
# 2. 调试和分析问题
# 3. 自动修复代码
# 4. 重新运行验证
```

## 📖 详细使用指南

### Planner 使用技巧

1. **明确测试目标**: 告诉 Planner 要测试的功能模块
2. **提供页面 URL**: 确保 Planner 能访问目标页面
3. **说明业务场景**: 描述关键的用户流程
4. **审查测试计划**: Planner 生成后，检查测试覆盖率

**示例对话**:
```
用户: 请为设备库存页面创建测试计划
      URL: https://app.example.com/device-inventory
      
Planner: 我将探索设备库存页面并创建测试计划...
         [探索界面、识别元素、设计场景]
         测试计划已保存到 device-inventory-test-plan.md
```

### Generator 使用技巧

1. **提供测试计划**: 使用 Planner 生成的或手写的测试计划
2. **指定输出路径**: 告诉 Generator 代码保存位置
3. **选择种子文件**: 提供参考的测试类（可选）
4. **审查生成代码**: 确保代码符合项目规范

**示例对话**:
```
用户: 根据测试计划生成设备库存页面测试代码
      计划: device-inventory-test-plan.md
      输出: src/test/java/com/example/testcase/DeviceInventoryPageTest.java
      
Generator: 我将根据测试计划生成 Java 测试代码...
           [实时执行操作、记录步骤、生成代码]
           测试代码已生成: DeviceInventoryPageTest.java
```

### Healer 使用技巧

1. **运行测试获取报告**: 先运行测试，让 Healer 看到失败
2. **提供错误日志**: 如有详细日志，可以加快分析
3. **信任自动修复**: Healer 会使用最佳实践修复
4. **验证修复结果**: 修复后重新运行测试确认

**示例对话**:
```
用户: 设备库存页面测试失败了，请帮我修复
      错误: TimeoutException at DeviceInventoryPageTest.java:45
      
Healer: 我将调试这个失败的测试...
        [运行调试、分析问题、修复代码]
        问题原因: 元素定位器变化
        已修复: 更新为更健壮的定位策略
        测试现在通过了 ✓
```

## 🎨 代码风格示例

### 测试类结构

```java
@ExtendWith(ReportPortalExtension.class)
class FeaturePageTest extends Hook {

    @BeforeAll
    static void skipIfNeeded() {
        // 环境检查
    }

    @Test
    @Tag("smoke")
    void testCase001_descriptiveName() throws InterruptedException {
        // 1. 准备测试数据（如需要）
        
        // 2. 执行操作
        helperContext.getFeatureHelper().performAction();
        
        // 3. 验证结果
        assertThat(element).isVisible();
        
        // 4. 清理（如需要）
    }
}
```

### Helper 方法结构

```java
public class FeatureHelper {
    
    public String performBusinessOperation(String param) {
        // 1. 导航或准备
        helperContext.getCommonHelper().navigateToPage();
        
        // 2. 执行操作
        CommonMethod.clickElement(element, TIMEOUT_SECONDS_15);
        CommonMethod.input(inputField, param, TIMEOUT_SECONDS_15);
        
        // 3. 等待结果
        helperContext.getCommonHelper().waitForToast(TIMEOUT_SECONDS_15);
        
        // 4. 返回结果
        return getToastMessage();
    }
}
```

### PageObject 结构

```java
public class FeaturePage extends CommonPage {
    
    // 元素定位器
    public final Locator pageTitle;
    public final Locator actionButton;
    
    public FeaturePage(Page page) {
        super(page);
        
        // 使用推荐的定位策略
        this.pageTitle = page.getByRole(AriaRole.HEADING, 
            new Page.GetByRoleOptions().setName("Feature Page"));
        this.actionButton = page.getByRole(AriaRole.BUTTON,
            new Page.GetByRoleOptions().setName("Action"));
    }
    
    // 辅助方法
    public Locator getItemByName(String name) {
        return page.locator(String.format("tr:has-text('%s')", name));
    }
}
```

## 🔧 常见问题

### Q: 如何处理动态加载的元素？

**A**: 使用显式等待策略

```java
// 等待元素可见
CommonMethod.waitForElementVisible(element, TIMEOUT_SECONDS_15);

// 等待网络请求完成
helperContext.getCommonHelper().waitForTableData(TIMEOUT_SECONDS_15);

// 等待页面状态
page.waitForLoadState(LoadState.NETWORKIDLE);
```

### Q: 如何处理动态数据（每次都不同）？

**A**: 使用灵活的断言

```java
// 使用 contains 而非 equals
assertTrue(actualText.contains("Success"), "Should contain success message");

// 使用正则表达式
assertTrue(actualText.matches("Device \\d+ created"), "Should match pattern");

// 使用 Playwright 的模糊匹配
assertThat(element).hasText(Pattern.compile("Device \\d+"));
```

### Q: 测试在 CI/CD 环境中不稳定怎么办？

**A**: 优化等待策略和环境配置

```java
// 1. 增加超时时间
private static final long CI_TIMEOUT = AppProperty.isCI ? 30000 : 15000;

// 2. 添加重试机制（JUnit 5）
@RepeatedTest(value = 3, failureThreshold = 1)

// 3. 使用无头模式
BrowserType.LaunchOptions options = new BrowserType.LaunchOptions()
    .setHeadless(true);
```

### Q: 如何组织大型测试项目？

**A**: 推荐的目录结构

```
src/test/java/
├── com/example/
│   ├── testcase/
│   │   ├── smoketest/          # 冒烟测试
│   │   ├── regression/         # 回归测试
│   │   └── e2e/               # 端到端测试
│   ├── pageobject/            # 页面对象
│   │   ├── common/
│   │   └── feature/
│   ├── helper/                # Helper 类
│   │   ├── Hook.java
│   │   ├── CommonHelper.java
│   │   └── *Helper.java
│   ├── context/               # 上下文管理
│   ├── common/                # 工具类
│   └── property/              # 配置管理
```

## 📊 测试标签使用

使用 JUnit 5 标签组织测试：

```java
@Tag("smoke")      // 冒烟测试 - 快速验证核心功能
@Tag("regression") // 回归测试 - 完整测试套件
@Tag("ui")         // UI 测试
@Tag("functional") // 功能测试
@Tag("filter")     // 过滤功能测试
@Tag("sort")       // 排序功能测试
@Tag("complex")    // 复杂场景测试
@Tag("slow")       // 慢速测试
@Tag("critical")   // 关键业务测试
```

运行特定标签的测试：

```bash
# 只运行冒烟测试
mvn test -Dgroups="smoke"

# 运行冒烟测试和回归测试
mvn test -Dgroups="smoke | regression"

# 排除慢速测试
mvn test -DexcludedGroups="slow"
```

## 🤝 贡献指南

### 添加新的 Helper 类

1. 创建 Helper 类继承结构
2. 在 Hook 中初始化
3. 注册到 HelperContext
4. 添加使用文档

### 添加新的 PageObject

1. 创建 PageObject 类继承 CommonPage
2. 定义页面特有元素
3. 添加辅助方法
4. 在 PagesContext 中注册

### 更新 Agent Skills

1. 修改对应的 SKILL.md 文件
2. 更新示例和文档
3. 测试 Agent 行为
4. 更新此 README

## 📝 最佳实践总结

### ✅ 推荐做法

1. **使用 PageObject 模式**: 分离定位逻辑和测试逻辑
2. **封装业务操作**: 创建 Helper 方法
3. **显式等待**: 避免 `Thread.sleep()`
4. **清晰的命名**: 方法和变量名要描述性强
5. **适当的注释**: 解释业务逻辑，不是代码逻辑
6. **独立的测试**: 每个测试可以独立运行
7. **测试数据清理**: 在 @AfterEach 中清理
8. **使用标签**: 组织和分类测试
9. **断言消息**: 提供清晰的失败信息
10. **代码复用**: 使用 Helper 和 PageObject

### ❌ 避免做法

1. 硬编码等待时间
2. 在测试中直接使用 CSS 选择器
3. 复制粘贴代码
4. 测试之间有依赖关系
5. 忽略测试失败
6. 没有清理测试数据
7. 使用魔法数字
8. 过度复杂的测试
9. 没有断言消息
10. 不遵循命名约定

## 📞 获取帮助

- 查看参考代码: `generator/references/java/`
- 阅读风格指南: `generator/references/java_test_style_guide_zh.md`
- 运行示例测试: 查看 `testcase/DeviceInventoryPageTest.java`
- 提出问题: 在项目 issue 中提问

## 📄 许可证

MIT License - 详见项目根目录 LICENSE 文件

---

**现在开始使用 Java Playwright UI 测试 Agent！** 🚀

查看详细使用指南：[USAGE.md](USAGE.md)

查看 Agent 实现：[agent.py](agent.py)

**祝测试愉快！Happy Testing! 🎉**

