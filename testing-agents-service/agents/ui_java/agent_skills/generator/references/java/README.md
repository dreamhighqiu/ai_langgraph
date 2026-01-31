# Java Playwright 参考代码

本目录包含 Java + Playwright 自动化测试的完整参考实现。

## 📁 目录结构

```
java/
├── helper/
│   ├── Hook.java           # 测试基类，提供 Playwright 生命周期管理
│   └── UsersHelper.java    # 用户管理业务操作封装示例
├── pageobject/
│   ├── CommonPage.java     # 通用页面元素定位器
│   └── DeviceInventoryPage.java  # 设备库存页面对象示例
└── testcase/
    └── DeviceInventoryPageTest.java  # 完整测试套件示例
```

## 🎯 代码用途

这些参考代码是为 **Generator Agent** 提供的编码风格参考：

1. **不要直接导入或执行** 这些文件
2. **作为风格模板** 生成新的测试代码
3. **学习最佳实践** 了解推荐的代码结构
4. **参考模式** PageObject、Helper、Hook 模式

## 📖 各文件说明

### Hook.java
**测试基类** - 所有测试类继承此类

**提供功能**:
- Playwright 浏览器启动和关闭
- 页面对象和 Helper 初始化
- 登录处理和会话状态管理
- 截图和追踪记录
- 测试前后的清理工作
- 账号池管理

**关键方法**:
- `testSetup()`: 测试前置设置
- `startBrowser()`: 启动浏览器
- `loginToWebPortal()`: 登录应用
- `tearDown()`: 测试清理

### UsersHelper.java
**业务操作封装** - 用户管理功能

**提供方法**:
- `addNewUserSuccessfully()`: 完整的添加用户流程
- `inviteUserAndGetToastMessage()`: 邀请用户操作
- `deleteUser()`: 删除用户
- `searchAndVerifyPartialMatches()`: 搜索验证
- `searchAndDeleteUserIfExists()`: 测试数据清理

**设计特点**:
- 封装多步骤操作
- 返回必要的验证数据
- 包含断言和等待
- 适当的异常处理

### CommonPage.java
**通用页面对象** - 所有页面共享的元素

**定义元素**:
- 顶部导航栏（Logo、用户菜单、租户切换）
- 左侧导航菜单（主页、设备、打印机等）
- 搜索和操作栏（搜索框、刷新、过滤）
- 表格元素（表头、行、加载状态）
- 对话框和通知（删除确认、Toast消息）
- 过滤器控件

**辅助方法**:
- `getColumnHeaderByName()`: 获取指定列的表头
- `getSortControlForColumn()`: 获取排序控件
- `getFilterCheckboxByName()`: 获取过滤器复选框
- 等等...

**设计原则**:
- 所有定位器声明为 `public final`
- 优先使用 Role 和 Text 定位
- 提供动态定位器方法
- 清晰的分组和注释

### DeviceInventoryPage.java
**特定页面对象** - 设备库存页面

**继承**: `extends CommonPage`

**定义元素**:
- 页面标题
- 设备表格和行
- 添加设备、导出、批量操作按钮
- 表格列（Model、Device Name、Serial Number 等）

**辅助方法**:
- `getDeviceRowBySerialNumber()`: 按序列号查找设备
- `getDeviceRowByName()`: 按名称查找设备
- `getActionsMenuInRow()`: 获取行操作菜单
- `getCellValue()`: 获取单元格值

### DeviceInventoryPageTest.java
**完整测试套件** - 设备库存页面测试

**测试用例**:
- `checkDeviceInventoryPageUI()`: UI 元素验证
- `checkSortFunctionInDeviceInventoryPageUIForMultiField()`: 多字段排序
- `checkSortDeviceNameFunctionInDeviceInventoryPageUIForOneField()`: 单字段排序
- `filterModelWithOneTag()`: 单个过滤器
- `filterModelWithTags()`: 多个过滤器
- `filterOSVersionAndModelWithOneTag()`: 组合过滤器

**测试特点**:
- 使用 `@Test` 和 `@Tag` 注解
- 继承自 `Hook` 基类
- 清晰的步骤注释
- 使用 Helper 和 PageObject
- Playwright Assertions 断言
- 适当的等待策略

## 🎨 代码风格要点

### 1. 命名约定

```java
// 测试类: <功能名>Test
DeviceInventoryPageTest

// 测试方法: 动词开头 + 描述性名称
checkSortDeviceNameFunction
filterModelWithTags
verifyDeviceInventoryPageUI

// Helper 类: <功能名>Helper
UsersHelper
DeviceInventoryHelper

// PageObject 类: <页面名>Page
DeviceInventoryPage
UsersPage
```

### 2. 注释风格

```java
/**
 * Javadoc 注释 - 类和公共方法
 * 
 * 包含:
 * - 功能描述
 * - 参数说明
 * - 返回值说明
 * - 使用示例（可选）
 */

// 单行注释 - 测试步骤
// 1. 导航到页面
// 2. 执行操作
// 3. 验证结果
```

### 3. 测试结构

```java
@Test
@Tag("smoke")
void testMethodName() throws InterruptedException {
    // Arrange - 准备测试数据
    String testData = "value";
    
    // Act - 执行操作
    String result = helperContext.getHelper().performAction(testData);
    
    // Assert - 验证结果
    assertEquals(expected, result, "Error message");
}
```

### 4. 等待策略

```java
// ✅ 推荐：使用 CommonMethod 的显式等待
CommonMethod.waitForElementVisible(element, TIMEOUT_SECONDS_15);
CommonMethod.clickElement(element, TIMEOUT_SECONDS_15);

// ✅ 推荐：使用 Helper 的业务等待
helperContext.getCommonHelper().waitForTableData(TIMEOUT_SECONDS_15);

// ❌ 避免：固定延迟
Thread.sleep(5000);
```

### 5. 断言方式

```java
// Playwright Assertions - UI 元素
import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;
assertThat(element).isVisible();
assertThat(element).hasText("Expected");

// JUnit Assertions - 数据验证
import static org.junit.jupiter.api.Assertions.*;
assertEquals(expected, actual, "Message");
assertTrue(condition, "Message");
```

## 🔗 相关文档

- **风格指南**: `../java_test_style_guide_zh.md` - 详细的编码规范
- **README**: `../../README.md` - 总体说明和使用指南
- **Generator SKILL**: `../../generator/SKILL.md` - 代码生成器说明

## 💡 使用建议

1. **学习模式**: 研究这些文件了解推荐的代码结构
2. **复制模板**: 创建新测试时参考这些模板
3. **保持一致**: 确保团队使用相同的风格
4. **持续改进**: 根据项目需求调整和优化

---

这些参考代码展示了 Java + Playwright 自动化测试的最佳实践。使用它们作为指导，创建高质量、可维护的测试代码！

