# Java Playwright 测试用例风格指南

## 目的
编写一致、可读、可维护的 Java 功能测试用例，映射到 UI 自动化。

## 测试用例结构

每个测试用例应包含以下元素：

### 1. 测试用例标识
- **ID**: TC_XXX（如 TC_001, TC_DEVICE_001）
- **标题**: 包含具体功能名称（避免通用的"点击按钮"）
- **优先级**: P0/P1/P2/P3
  - P0: 核心功能，阻塞性问题
  - P1: 重要功能，高优先级
  - P2: 一般功能，中等优先级
  - P3: 边缘场景，低优先级

### 2. 测试描述
```java
/**
 * 测试用例: TC_DEVICE_001
 * 标题: 验证设备库存页面 UI 元素显示
 * 优先级: P0
 * 描述: 验证设备库存页面的所有关键 UI 元素正确加载和显示
 */
@Test
@Tag("smoke")
void verifyDeviceInventoryPageUIElements() { }
```

### 3. 前置条件
- 明确列出测试执行前的必要条件
- 在 Java 中通常通过 `@BeforeEach` 或 Hook 类处理
- 始终假设空白/全新状态（除非特别说明）

```java
@BeforeAll
static void skipIfSkipModule() {
    Assumptions.assumeFalse(
        HarmonixProperty.skipModule.contains("DeviceInventoryPage".toLowerCase()),
        "Tests are skipped in this environment"
    );
}
```

### 4. 测试步骤
- 有序的、具体的操作，包含元素名称
- 每个步骤前添加注释说明
- 使用业务术语描述操作

```java
// 1. 导航到设备库存页面
helperContext.getCommonHelper().goToDeviceInventoryPage();

// 2. 验证页面标题显示
assertThat(pagesContext.getDeviceInventoryPage().pageTitle).isVisible();

// 3. 验证搜索功能
helperContext.getCommonHelper().performSearch("Test Device");
```

### 5. 预期结果
- 清晰、可观察的结果
- 使用 Playwright Assertions 进行验证
- 包含有意义的断言失败消息

```java
assertThat(pagesContext.getCommonPage().tableRows)
    .hasCount(expectedCount);

assertEquals(expectedMessage, actualMessage, 
    "Toast message should match expected success message");
```

## 测试覆盖清单

### 1. 主流程（Happy Path）
- 正常用户行为
- 标准输入和操作
- 预期的成功场景

### 2. 验证和错误状态
- 无效输入处理
- 错误消息显示
- 表单验证

### 3. 边界值（适用时）
- 最小值/最大值
- 空值/null
- 特殊字符

### 4. 权限/可见性（适用时）
- 不同用户角色
- 访问控制
- 功能可用性

### 5. 列表/搜索/过滤（如果存在）
- 搜索功能
- 过滤器应用
- 排序功能
- 分页

## 编码指南

### 命名约定

1. **测试类命名**
   ```java
   // 格式: <功能名>Test
   DeviceInventoryPageTest
   UsersPageTest
   LoginFunctionalityTest
   ```

2. **测试方法命名**
   ```java
   // 使用驼峰命名法，清晰描述测试内容
   verifyDeviceInventoryPageUIElements()
   checkSortFunctionForMultipleFields()
   filterModelWithSingleTag()
   ```

3. **变量命名**
   ```java
   // 使用有意义的名称
   String expectedToastMessage = "User invited successfully!";
   List<String> selectedFilters = List.of("Model", "OS Version");
   int maxScrollAttempts = 3;
   ```

### 代码组织

1. **使用 PageObject 模式**
   ```java
   // 不要直接使用定位器
   // 错误 ❌
   page.locator("#submit-button").click();
   
   // 正确 ✅
   pagesContext.getDeviceInventoryPage().submitButton.click();
   ```

2. **使用 Helper 类封装复杂操作**
   ```java
   // 不要在测试中编写复杂逻辑
   // 错误 ❌
   page.locator("input[type='search']").fill(searchTerm);
   page.keyboard().press("Enter");
   page.waitForTimeout(2000);
   
   // 正确 ✅
   helperContext.getCommonHelper().performSearch(searchTerm);
   helperContext.getCommonHelper().waitForTableData(TIMEOUT_SECONDS_15);
   ```

3. **使用常量而非魔法数字**
   ```java
   // 错误 ❌
   Thread.sleep(15000);
   
   // 正确 ✅
   CommonMethod.waitForElementVisible(element, TIMEOUT_SECONDS_15);
   ```

### 断言最佳实践

1. **使用 Playwright Assertions**
   ```java
   import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;
   
   // 元素可见性
   assertThat(element).isVisible();
   
   // 元素隐藏
   assertThat(element).isHidden();
   
   // 文本内容
   assertThat(element).hasText("Expected Text");
   
   // 元素数量
   assertThat(rows).hasCount(10);
   ```

2. **使用 JUnit 断言（数据验证）**
   ```java
   import static org.junit.jupiter.api.Assertions.*;
   
   assertEquals(expected, actual, "Error message");
   assertTrue(condition, "Error message");
   assertFalse(condition, "Error message");
   assertNotNull(object, "Error message");
   ```

3. **提供清晰的断言消息**
   ```java
   // 错误 ❌
   assertEquals(expected, actual);
   
   // 正确 ✅
   assertEquals(expectedCount, actualCount, 
       String.format("Device count mismatch. Expected: %d, Actual: %d", 
           expectedCount, actualCount));
   ```

### 等待策略

1. **使用显式等待**
   ```java
   // 等待元素可见
   CommonMethod.waitForElementVisible(element, TIMEOUT_SECONDS_15);
   
   // 等待元素可点击
   CommonMethod.clickElement(element, TIMEOUT_SECONDS_15);
   
   // 等待表格数据加载
   helperContext.getCommonHelper().waitForTableData(TIMEOUT_SECONDS_15);
   ```

2. **避免固定延迟**
   ```java
   // 错误 ❌
   Thread.sleep(5000);
   
   // 正确 ✅
   page.waitForLoadState(LoadState.NETWORKIDLE);
   // 或
   page.waitForSelector("table tbody tr", new Page.WaitForSelectorOptions()
       .setTimeout(TIMEOUT_SECONDS_15));
   ```

### 异常处理

```java
@Test
@Tag("smoke")
void testMethodName() throws InterruptedException {
    try {
        // 测试逻辑
        performAction();
        verifyResult();
    } catch (Exception e) {
        // 记录错误信息
        System.err.println("Test failed: " + e.getMessage());
        throw e; // 重新抛出以标记测试失败
    }
}
```

## 测试数据管理

1. **使用测试数据常量**
   ```java
   private static final String TEST_EMAIL = "test@example.com";
   private static final String TEST_DEVICE_NAME = "TestDevice001";
   ```

2. **参数化测试（适用时）**
   ```java
   @ParameterizedTest
   @ValueSource(strings = {"Model", "OS Version", "Device Name"})
   void testFilterWithDifferentColumns(String columnName) {
       commonHelper.filterWithSingleOptionAndCheckFilterResult(columnName);
   }
   ```

3. **动态数据生成**
   ```java
   String uniqueEmail = "user_" + System.currentTimeMillis() + "@example.com";
   String randomDeviceName = "Device_" + UUID.randomUUID().toString().substring(0, 8);
   ```

## 测试标签（Tags）

使用 JUnit 5 标签对测试进行分类：

```java
@Tag("smoke")      // 冒烟测试
@Tag("regression") // 回归测试
@Tag("critical")   // 关键功能
@Tag("slow")       // 慢速测试
@Tag("ui")         // UI 测试
```

## 代码注释指南

1. **类级别注释**
   ```java
   /**
    * 设备库存页面测试套件
    * 
    * 测试范围:
    * - UI 元素验证
    * - 搜索和过滤功能
    * - 排序功能
    * - 数据加载和显示
    */
   @ExtendWith(ReportPortalExtension.class)
   class DeviceInventoryPageTest extends Hook {
   ```

2. **方法级别注释**
   ```java
   /**
    * 测试设备名称和 OS 版本的多字段排序功能
    * 
    * 步骤:
    * 1. 验证关键元素存在
    * 2. 配置排序动作（设备名称降序 + OS 版本升序）
    * 3. 执行排序并验证结果
    */
   @Test
   @Tag("smoke")
   void checkSortDeviceNameAndOSVersionFunction() { }
   ```

3. **步骤注释**
   ```java
   // 1. 打开过滤菜单
   commonHelper.openFilterMenu("Model");
   
   // 2. 选择多个过滤选项
   List<String> selectedOptions = commonHelper.selectMultipleFilterOptions(3);
   
   // 3. 应用过滤器并验证结果
   commonHelper.applyFilterAndVerifyResult(selectedOptions);
   ```

## 测试独立性原则

每个测试应该：
- 独立于其他测试
- 可以按任意顺序运行
- 不依赖于其他测试的状态
- 清理自己创建的数据（通过 @AfterEach）

```java
@AfterEach
void cleanup() {
    // 清理测试数据
    if (createdUserId != null) {
        deleteUser(createdUserId);
    }
}
```

## 参考现有测试用例

如果参考用例存在，遵循其命名和格式约定：
- 研究现有的测试模式
- 复用现有的 Helper 方法
- 保持一致的代码风格
- 遵循项目的最佳实践

## 示例：完整的测试用例

```java
package com.example.testcase.smoketest;

import com.epam.reportportal.junit5.ReportPortalExtension;
import com.example.helper.Hook;
import com.example.helper.CommonHelper;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Assumptions;
import org.junit.jupiter.api.extension.ExtendWith;

import java.util.List;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

/**
 * 设备库存页面 UI 测试
 * 
 * 测试用例 ID: TC_DEVICE_001 - TC_DEVICE_010
 * 优先级: P0
 * 测试范围: 设备库存页面的关键 UI 功能验证
 */
@ExtendWith(ReportPortalExtension.class)
class DeviceInventoryPageTest extends Hook {

    @BeforeAll
    static void skipIfSkipModule() {
        Assumptions.assumeFalse(
            HarmonixProperty.skipModule.contains("DeviceInventoryPage".toLowerCase()),
            "DeviceInventoryPage tests are skipped in this environment"
        );
    }

    /**
     * TC_DEVICE_001: 验证设备库存页面 UI 元素
     * 
     * 目的: 确保所有关键 UI 元素正确显示
     * 前置条件: 用户已登录系统
     * 步骤:
     * 1. 导航到设备库存页面
     * 2. 验证页面标题
     * 3. 验证搜索框
     * 4. 验证刷新按钮
     * 5. 验证表格数据加载
     * 预期结果: 所有关键元素可见且功能正常
     */
    @Test
    @Tag("smoke")
    void verifyDeviceInventoryPageUIElements() throws InterruptedException {
        // 验证所有关键元素存在
        deviceInventoryHelper.verifyAllKeyElementsOnDeviceInventoryPresence();
    }

    /**
     * TC_DEVICE_002: 测试单字段过滤功能（Model）
     * 
     * 目的: 验证按单个模型过滤设备的功能
     * 步骤:
     * 1. 打开 Model 过滤菜单
     * 2. 选择一个过滤选项
     * 3. 应用过滤
     * 4. 验证过滤结果正确
     */
    @Test
    @Tag("smoke")
    void filterModelWithSingleTag() {
        commonHelper.filterWithSingleOptionAndCheckFilterResult("Model");
    }

    /**
     * TC_DEVICE_003: 测试多字段过滤功能（Model）
     * 
     * 目的: 验证按多个模型同时过滤设备的功能
     */
    @Test
    @Tag("smoke")
    void filterModelWithMultipleTags() {
        commonHelper.filterWithMultipleOptionsAndCheckFilterResult("Model");
    }

    /**
     * TC_DEVICE_004: 测试设备名称排序功能（降序）
     * 
     * 目的: 验证按设备名称降序排序的功能
     * 步骤:
     * 1. 验证页面元素
     * 2. 配置排序动作（设备名称 - 降序）
     * 3. 执行排序
     * 4. 验证 UI 显示与 API 数据一致
     */
    @Test
    @Tag("smoke")
    void checkSortDeviceNameFunctionDescending() throws InterruptedException {
        // 1. 验证关键元素存在
        deviceInventoryHelper.verifyAllKeyElementsOnDeviceInventoryPresence();
        
        // 2. 配置排序参数
        List<CommonHelper.SortAction> sortActions = List.of(
            new CommonHelper.SortAction("Device Name", "name", 
                CommonHelper.SortDirection.DESCENDING)
        );
        String apiPath = "v1/devices";
        String uniqueUiColumnHeader = "Serial Number";
        String uniqueApiJsonKey = "serial_number";
        List<String> allUiColumnHeaders = List.of(
            "Model", "Device Name", "Device Type", "Serial Number", "OS Version"
        );
        int maxScrolls = 3;
        
        // 3. 设置并执行排序验证
        CommonHelper.SortVerificationSetup setup = 
            helperContext.getCommonHelper().setupSortVerification(
                apiPath, sortActions
            );
        
        // 4. 执行排序并验证结果
        helperContext.getCommonHelper().executeAndVerifySort(
            setup,
            uniqueUiColumnHeader,
            uniqueApiJsonKey,
            allUiColumnHeaders,
            maxScrolls
        );
    }
}
```

## 总结

遵循这些指南可以确保：
- **可读性**: 代码清晰易懂
- **可维护性**: 易于修改和扩展
- **可靠性**: 测试结果一致可信
- **可重用性**: 代码组件可复用
- **专业性**: 符合行业最佳实践

