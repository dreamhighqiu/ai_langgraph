package com.example.testcase.smoketest;

import com.epam.reportportal.junit5.ReportPortalExtension;
import com.example.helper.Hook;
import com.example.helper.CommonHelper;
import com.example.property.AppProperty;
import org.junit.jupiter.api.Assumptions;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;

import java.util.List;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

/**
 * 设备库存页面冒烟测试套件
 * 
 * 测试范围:
 * - UI 元素验证
 * - 搜索和过滤功能
 * - 排序功能
 * - 数据加载和显示
 * 
 * 优先级: P0 - 核心功能
 * 
 * 执行频率: 每次构建
 * 
 * @author Test Automation Team
 */
@ExtendWith(ReportPortalExtension.class)
class DeviceInventoryPageTest extends Hook {

    /**
     * 前置检查 - 跳过被禁用的模块
     * 
     * 使用 JUnit 5 Assumptions 在特定环境下跳过测试
     */
    @BeforeAll
    static void skipIfSkipModule() {
        Assumptions.assumeFalse(
                AppProperty.skipModule.contains("DeviceInventoryPage".toLowerCase()),
                "DeviceInventoryPage tests are skipped in this environment"
        );
    }

    /**
     * TC_DEVICE_001: 验证设备库存页面 UI 元素
     * 
     * 目的: 确保所有关键 UI 元素正确显示
     * 
     * 前置条件:
     * - 用户已登录系统
     * - 有设备数据可显示
     * 
     * 测试步骤:
     * 1. 导航到设备库存页面（通过 Hook 自动完成）
     * 2. 验证页面标题可见
     * 3. 验证搜索框可见
     * 4. 验证刷新按钮可见
     * 5. 验证表格数据加载
     * 6. 验证过滤器图标存在
     * 
     * 预期结果:
     * - 所有关键 UI 元素可见且功能正常
     * - 页面加载无错误
     * - 表格显示设备数据
     */
    @Test
    @Tag("smoke")
    @Tag("ui")
    void checkDeviceInventoryPageUI() throws InterruptedException {
        // 验证所有关键元素存在
        deviceInventoryHelper.verifyAllKeyElementsOnDeviceInventoryPresence();
    }

    /**
     * TC_DEVICE_002: 测试多字段排序功能
     * 
     * 目的: 验证按多个字段组合排序的功能
     * 
     * 测试步骤:
     * 1. 验证页面关键元素存在
     * 2. 配置排序动作（Model 升序 + Device Name 降序）
     * 3. 执行排序操作
     * 4. 滚动表格获取数据
     * 5. 验证 UI 显示与 API 返回数据一致
     * 
     * 预期结果:
     * - 排序按钮正确响应
     * - 表格数据按指定顺序排列
     * - UI 数据与 API 数据匹配
     */
    @Test
    @Tag("smoke")
    @Tag("functional")
    void checkSortFunctionInDeviceInventoryPageUIForMultiField() throws InterruptedException {
        // 1. 验证关键元素存在
        deviceInventoryHelper.verifyAllKeyElementsOnDeviceInventoryPresence();
        
        // 2. 配置排序动作
        List<CommonHelper.SortAction> sortActions = List.of(
            new CommonHelper.SortAction("Model", "model", CommonHelper.SortDirection.ASCENDING),
            new CommonHelper.SortAction("Device Name", "name", CommonHelper.SortDirection.DESCENDING)
        );
        
        // 3. 配置验证参数
        String apiPath = "v1/devices";
        String uniqueUiColumnHeader = "Serial Number";
        String uniqueApiJsonKey = "serial_number";
        List<String> allUiColumnHeaders = List.of(
            "Model", "Device Name", "Device Type", "Serial Number", "OS Version"
        );
        int maxScrolls = 3;
        
        // 4. 设置排序验证
        CommonHelper.SortVerificationSetup setup = helperContext.getCommonHelper()
            .setupSortVerification(apiPath, sortActions);

        // 5. 执行排序并验证结果
        helperContext.getCommonHelper().executeAndVerifySort(
            setup,
            uniqueUiColumnHeader,
            uniqueApiJsonKey,
            allUiColumnHeaders,
            maxScrolls
        );
    }

    /**
     * TC_DEVICE_003: 测试单字段排序（设备名称降序）
     * 
     * 目的: 验证按单个字段排序的功能
     */
    @Test
    @Tag("smoke")
    @Tag("functional")
    void checkSortDeviceNameFunctionInDeviceInventoryPageUIForOneField() throws InterruptedException {
        // 验证关键元素
        deviceInventoryHelper.verifyAllKeyElementsOnDeviceInventoryPresence();

        // 配置排序动作（单字段）
        List<CommonHelper.SortAction> sortActions = List.of(
            new CommonHelper.SortAction("Device Name", "name", CommonHelper.SortDirection.DESCENDING)
        );
        
        String apiPath = "v1/devices";
        String uniqueUiColumnHeader = "Serial Number";
        String uniqueApiJsonKey = "serial_number";
        List<String> allUiColumnHeaders = List.of(
            "Model", "Device Name", "Device Type", "Serial Number", "OS Version"
        );
        int maxScrolls = 3;
        
        // 设置并执行排序验证
        CommonHelper.SortVerificationSetup setup = helperContext.getCommonHelper()
            .setupSortVerification(apiPath, sortActions);

        helperContext.getCommonHelper().executeAndVerifySort(
            setup,
            uniqueUiColumnHeader,
            uniqueApiJsonKey,
            allUiColumnHeaders,
            maxScrolls
        );
    }

    /**
     * TC_DEVICE_004: 测试序列号排序功能
     */
    @Test
    @Tag("smoke")
    void checkSortSerialNumberFunctionInDeviceInventoryPageUIForOneField() throws InterruptedException {
        deviceInventoryHelper.verifyAllKeyElementsOnDeviceInventoryPresence();

        List<CommonHelper.SortAction> sortActions = List.of(
            new CommonHelper.SortAction("Serial Number", "serial_number", CommonHelper.SortDirection.DESCENDING)
        );
        
        String apiPath = "v1/devices";
        String uniqueUiColumnHeader = "Serial Number";
        String uniqueApiJsonKey = "serial_number";
        List<String> allUiColumnHeaders = List.of(
            "Model", "Device Name", "Device Type", "Serial Number", "OS Version"
        );
        int maxScrolls = 3;
        
        CommonHelper.SortVerificationSetup setup = helperContext.getCommonHelper()
            .setupSortVerification(apiPath, sortActions);

        helperContext.getCommonHelper().executeAndVerifySort(
            setup,
            uniqueUiColumnHeader,
            uniqueApiJsonKey,
            allUiColumnHeaders,
            maxScrolls
        );
    }

    /**
     * TC_DEVICE_005: 测试单个标签过滤（Model）
     * 
     * 目的: 验证按单个模型过滤设备
     * 
     * 测试步骤:
     * 1. 点击 Model 列的过滤器图标
     * 2. 选择一个模型选项
     * 3. 点击"应用"按钮
     * 4. 验证表格只显示选中模型的设备
     * 5. 验证过滤器标签显示
     * 
     * 预期结果:
     * - 过滤器正确应用
     * - 表格数据符合过滤条件
     * - 可以看到活动的过滤器标签
     */
    @Test
    @Tag("smoke")
    @Tag("filter")
    void filterModelWithOneTag() {
        commonHelper.filterWithSingleOptionAndCheckFilterResult("Model");
    }

    /**
     * TC_DEVICE_006: 测试多个标签过滤（Model）
     * 
     * 目的: 验证按多个模型同时过滤设备
     */
    @Test
    @Tag("smoke")
    @Tag("filter")
    void filterModelWithTags() {
        commonHelper.filterWithMultipleOptionsAndCheckFilterResult("Model");
    }

    /**
     * TC_DEVICE_007: 测试重置过滤器（Model）
     * 
     * 目的: 验证重置过滤器恢复所有数据
     */
    @Test
    @Tag("smoke")
    @Tag("filter")
    void resetModelFilter() {
        commonHelper.resetFilterAndCheckResult("Model");
    }

    /**
     * TC_DEVICE_008: 测试 OS 版本单个标签过滤
     */
    @Test
    @Tag("smoke")
    @Tag("filter")
    void filterOSVersionWithOneTag() {
        commonHelper.filterWithSingleOptionAndCheckFilterResult("OS Version");
    }

    /**
     * TC_DEVICE_009: 测试 OS 版本多个标签过滤
     */
    @Test
    @Tag("smoke")
    @Tag("filter")
    void filterOSVersionWithTags() {
        commonHelper.filterWithMultipleOptionsAndCheckFilterResult("OS Version");
    }

    /**
     * TC_DEVICE_010: 测试重置 OS 版本过滤器
     */
    @Test
    @Tag("smoke")
    @Tag("filter")
    void resetOSVersionFilter() {
        commonHelper.resetFilterAndCheckResult("OS Version");
    }

    /**
     * TC_DEVICE_011: 测试多个过滤器组合（OS Version + Model，单标签）
     * 
     * 目的: 验证多个过滤器同时应用的功能
     * 
     * 测试步骤:
     * 1. 应用 OS Version 过滤器（选择一个）
     * 2. 应用 Model 过滤器（选择一个）
     * 3. 验证表格数据同时满足两个过滤条件
     * 4. 重置 OS Version 过滤器
     * 5. 验证只有 Model 过滤器生效
     * 6. 重置 Model 过滤器
     * 7. 验证所有数据显示
     * 
     * 预期结果:
     * - 多个过滤器正确组合
     * - 数据符合所有过滤条件
     * - 重置单个过滤器不影响其他过滤器
     */
    @Test
    @Tag("smoke")
    @Tag("filter")
    @Tag("complex")
    void filterOSVersionAndModelWithOneTag() {
        // 应用 OS Version 过滤
        List<String> osVersions = commonHelper.filterWithSingleOptionAndCheckFilterResult("OS Version");
        
        // 应用 Model 过滤
        List<String> models = commonHelper.filterWithSingleOptionAndCheckFilterResult("Model");
        
        // 验证多过滤器结果
        commonHelper.checkFilterResultIsCorrectWithMultipleFilters(
            List.of("OS Version", "Model")
        );
        
        // 获取过滤后的结果数量
        int resultCount = commonHelper.checkResultMatchEachFilter(
            List.of("OS Version", "Model")
        );
        
        // 重置 OS Version 过滤器
        commonHelper.openFilterMenu("OS Version");
        commonHelper.resetSelectedFilterAndCheckResult(osVersions, "OS Version");
        
        // 重置 Model 过滤器
        commonHelper.openFilterMenu("Model");
        commonHelper.resetSelectedFilterAndCheckResult(models, "Model");
        
        // 验证所有数据加载
        commonHelper.checkAllDataLoad(resultCount);
    }

    /**
     * TC_DEVICE_012: 测试多个过滤器组合（OS Version + Model，多标签）
     * 
     * 目的: 验证每个过滤器选择多个选项的组合功能
     */
    @Test
    @Tag("smoke")
    @Tag("filter")
    @Tag("complex")
    void filterOSVersionAndModelWithTags() {
        // 应用 Model 过滤（多个选项）
        List<String> models = commonHelper.filterWithMultipleOptionsAndCheckFilterResult("Model");
        
        // 应用 OS Version 过滤（多个选项）
        List<String> osVersions = commonHelper.filterWithMultipleOptionsAndCheckFilterResult("OS Version");
        
        // 验证多过滤器结果
        commonHelper.checkFilterResultIsCorrectWithMultipleFilters(
            List.of("Model", "OS Version")
        );
        
        int resultCount = commonHelper.checkResultMatchEachFilter(
            List.of("Model", "OS Version")
        );
        
        // 依次重置过滤器
        commonHelper.openFilterMenu("Model");
        commonHelper.resetSelectedFilterAndCheckResult(models, "Model");
        
        commonHelper.openFilterMenu("OS Version");
        commonHelper.resetSelectedFilterAndCheckResult(osVersions, "OS Version");
        
        // 验证所有数据恢复
        commonHelper.checkAllDataLoad(resultCount);
    }
}

