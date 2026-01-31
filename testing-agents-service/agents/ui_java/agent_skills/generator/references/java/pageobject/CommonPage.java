package com.example.pageobject;

import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.options.AriaRole;

/**
 * CommonPage - 通用页面对象类
 * 
 * 职责:
 * - 定义应用中所有页面共享的UI元素
 * - 提供通用的定位器访问
 * - 封装通用的页面操作
 * 
 * 使用模式: PageObject Pattern
 * - 将页面元素定位逻辑与测试逻辑分离
 * - 提高代码可维护性和可重用性
 * - 当 UI 变化时只需修改 PageObject
 * 
 * 设计原则:
 * - 所有定位器声明为 public final
 * - 使用 Playwright 推荐的定位策略（role > text > testId > css）
 * - 提供辅助方法生成动态定位器
 * 
 * @author Test Automation Team
 */
public class CommonPage {
    protected final Page page;

    // ========== 顶部导航栏元素 ==========
    
    /** 应用Logo */
    public final Locator harmonixLogo;
    
    /** 租户下拉菜单 */
    public final Locator tenantDropdown;
    
    /** 用户资料按钮 */
    public final Locator userProfileButton;
    
    /** 登出按钮 */
    public final Locator logoutButton;
    
    /** 用户菜单弹出层 */
    public final Locator userMenuPopup;
    
    /** 租户列表项 */
    public final Locator tenantListItems;

    // ========== 左侧导航菜单 ==========
    
    /** 主页图标 */
    public final Locator homeIcon;
    
    /** 手机图标（移动设备） */
    public final Locator phoneIcon;
    
    /** 打印机图标 */
    public final Locator printerIcon;
    
    /** 扫描仪图标 */
    public final Locator scannerIcon;

    // ========== 打印机子菜单 ==========
    
    /** 新建打印机设置 */
    public final Locator newPrinterSetup;
    
    /** 我的打印机 */
    public final Locator myPrinters;
    
    /** 打印机设置 */
    public final Locator printerSettings;

    // ========== 搜索和操作栏 ==========
    
    /** 搜索框 */
    public final Locator searchBox;
    
    /** 搜索组件 */
    public final Locator searchComponent;
    
    /** 清空搜索按钮 */
    public final Locator clearSearchButton;
    
    /** 刷新按钮 */
    public final Locator refreshButton;
    
    /** 列可见性按钮 */
    public final Locator columnVisibilityButton;
    
    /** 清空搜索结果按钮 */
    public final Locator clearSearchResultButton;

    // ========== 表格元素 ==========
    
    /** 表头 */
    public final Locator tableHeader;
    
    /** 表格行（有数据索引的） */
    public final Locator tableRows;
    
    /** 所有表格行 */
    public final Locator allTableRows;
    
    /** 数据行（不包含加载占位符） */
    public final Locator dataRows;
    
    /** 行元素 */
    public final Locator rows;
    
    /** 表头列 */
    public final Locator header;
    
    /** 可滚动表格容器 */
    public final Locator scrollableTableContainer;
    
    /** 表格加载占位符 */
    public final Locator tableLoadingShimmer;

    // ========== 操作菜单和对话框 ==========
    
    /** 操作菜单图标（三个点） */
    public final Locator actionsMenuIcon;
    
    /** 删除按钮 */
    public final Locator deleteButton;
    
    /** 删除设备对话框 */
    public final Locator deleteDeviceDialog;
    
    /** 删除设备确认文本 */
    public final Locator deleteDeviceConfirmationText;
    
    /** 删除配置文件对话框 */
    public final Locator deleteProfileDialog;
    
    /** 删除配置文件确认文本 */
    public final Locator deleteProfileConfirmationText;
    
    /** 对话框确认按钮 */
    public final Locator dialogConfirmButton;
    
    /** 对话框取消按钮 */
    public final Locator dialogCancelButton;

    // ========== 通知消息 ==========
    
    /** 成功删除配置文件通知 */
    public final Locator successDeleteProfileNotification;
    
    /** 成功删除设备通知 */
    public final Locator successDeleteDeviceNotification;
    
    /** Toast 消息 */
    public final Locator toastMessage;

    // ========== 过滤器元素 ==========
    
    /** 过滤器图标 */
    public final Locator filterIcon;
    
    /** 应用按钮 */
    public final Locator applyButton;
    
    /** 重置按钮 */
    public final Locator resetButton;
    
    /** 过滤器复选框（未选中） */
    public final Locator filterCheckBox;
    
    /** 过滤器复选框（已选中） */
    public final Locator selectedFilterCheckBox;

    // ========== 其他 ==========
    
    /** 选择文件按钮 */
    public final Locator selectFilesButton;
    
    /** 无结果消息 */
    public final Locator noResultsMessage;
    
    /** 版本信息 */
    public final Locator versionVersion;

    /**
     * 构造函数 - 初始化所有定位器
     * 
     * 定位器策略优先级:
     * 1. Role-based（推荐）: getByRole()
     * 2. Text-based: getByText(), hasText()
     * 3. Test ID: getByTestId()
     * 4. CSS Selector: locator() - 最后选择
     * 
     * @param page Playwright Page 对象
     */
    public CommonPage(Page page) {
        this.page = page;
        
        // 顶部导航栏
        this.harmonixLogo = page.locator("//div[@id='platform-name']");
        this.tenantDropdown = page.locator("//zeta-icon[@id='user-info-icon']");
        this.userProfileButton = page.locator("zeta-avatar[slot='user-avatar']");
        this.logoutButton = page.locator("zeta-button[aria-label='Log Out']");
        this.userMenuPopup = page.locator("div[class*='_dropdown_']:has-text('Tenants:')");
        this.tenantListItems = this.userMenuPopup.locator("> div[class*='_list-item_']");

        // 左侧导航
        this.homeIcon = page.locator("a:has(zeta-icon:has-text('home'))");
        this.phoneIcon = page.locator("a[title='Computers']");
        this.printerIcon = page.locator("a[title='Printers']");
        this.scannerIcon = page.locator("a:has(img[alt='Scanners'])");

        // 打印机子菜单
        this.newPrinterSetup = page.getByText("New Printer Setup");
        this.myPrinters = page.getByText("My Printers");
        this.printerSettings = page.getByText("Printer Settings");

        // 搜索和操作
        this.searchBox = page.locator("input[type='search']");
        this.searchComponent = page.locator("zeta-search");
        this.clearSearchButton = this.searchComponent.locator("zeta-icon:has-text('cancel')");
        this.refreshButton = page.locator("zeta-button:has(zeta-icon:has-text('refresh'))").first();
        this.columnVisibilityButton = page.locator("zeta-icon-button:has-text('columns')");
        this.clearSearchResultButton = page.locator("zeta-button:has-text('Clear search')");

        // 表格
        this.tableHeader = page.locator("table thead tr");
        this.tableRows = page.locator("table tbody tr[data-index]");
        this.allTableRows = page.locator("tbody > tr");
        this.dataRows = page.locator("table tbody tr[data-index]:not(:has(div[class^='_shimmer_']))");
        this.rows = page.locator("tbody tr");
        this.header = page.locator("thead th");
        this.scrollableTableContainer = page.locator("div[style*='overflow: auto']:has(table)").first();
        this.tableLoadingShimmer = this.scrollableTableContainer.locator("div[class^='_shimmer_']");

        // 操作菜单和对话框
        this.actionsMenuIcon = page.locator("zeta-icon-button:has-text('more_vertical')");
        this.deleteButton = page.locator("zeta-button")
            .filter(new Locator.FilterOptions().setHasText("Delete"));
        this.deleteDeviceDialog = page.locator("dialog:has-text('Delete Device')");
        this.deleteDeviceConfirmationText = page.getByText("Are you sure you want to delete this device(s)?");
        this.deleteProfileDialog = page.locator("dialog:has-text('Delete Profile')");
        this.deleteProfileConfirmationText = page.getByText("Are you sure you want to delete this profile(s)?");
        this.dialogConfirmButton = page.locator("dialog[open] zeta-button:has-text('Confirm')");
        this.dialogCancelButton = page.locator("dialog[open] zeta-button:has-text('Cancel')");

        // 通知
        this.successDeleteProfileNotification = page.getByText("Successfully deleted profile(s).");
        this.successDeleteDeviceNotification = page.getByText("Successfully deleted device(s).");
        this.toastMessage = page.locator("div[class^='_toast_'] span");

        // 过滤器
        this.filterIcon = page.locator("zeta-icon:text-is('filter')");
        this.applyButton = page.locator("zeta-button:has-text('Apply'):visible");
        this.resetButton = page.locator("zeta-button:has-text('Reset'):visible");
        this.filterCheckBox = page.locator("zeta-checkbox[aria-checked='false']");
        this.selectedFilterCheckBox = page.locator("zeta-checkbox[name]:not([name=''])[aria-checked='true']");

        // 其他
        this.selectFilesButton = page.getByRole(AriaRole.BUTTON, 
            new Page.GetByRoleOptions().setName("Select Files"));
        this.noResultsMessage = page.locator("text=/No results matched/i");
        this.versionVersion = page.locator(".version");
    }

    // ========== 辅助方法 - 动态定位器 ==========

    /**
     * 获取指定文本的 Toast 元素
     * 
     * @param text Toast 消息文本
     * @return Toast 元素定位器
     */
    public Locator getToastElement(String text) {
        return page.getByText(text);
    }

    /**
     * 根据列名获取表头
     * 
     * @param columnName 列名（如 "Device Name", "Model"）
     * @return 表头定位器
     */
    public Locator getColumnHeaderByName(String columnName) {
        return page.locator(String.format("th:has-text('%s')", columnName));
    }

    /**
     * 获取指定列的排序控件
     * 
     * @param columnName 列名
     * @return 排序控件定位器
     */
    public Locator getSortControlForColumn(String columnName) {
        return getColumnHeaderByName(columnName).locator("harmonix-sort");
    }

    /**
     * 获取指定列的向上排序箭头指示器
     * 
     * @param columnName 列名
     * @return 向上箭头定位器
     */
    public Locator getSortUpArrowIndicator(String columnName) {
        return getSortControlForColumn(columnName).locator("path >> nth=0");
    }

    /**
     * 获取指定列的向下排序箭头指示器
     * 
     * @param columnName 列名
     * @return 向下箭头定位器
     */
    public Locator getSortDownArrowIndicator(String columnName) {
        return getSortControlForColumn(columnName).locator("path >> nth=1");
    }

    /**
     * 获取指定列的过滤器图标
     * 
     * @param columnName 列名
     * @return 过滤器图标定位器
     */
    public Locator getFilterIconForColumn(String columnName) {
        String selector = String.format("th:has-text('%s') zeta-icon:has-text('filter')", columnName);
        return page.locator(selector);
    }

    /**
     * 根据名称获取过滤器复选框
     * 
     * @param checkboxName 复选框名称
     * @return 复选框定位器
     */
    public Locator getFilterCheckboxByName(String checkboxName) {
        String selector = String.format("zeta-checkbox[name=\"%s\"]", checkboxName);
        return page.locator(selector);
    }

    /**
     * 获取已选中的复选框
     * 
     * @param filterName 过滤器名称
     * @return 复选框定位器
     */
    public Locator getSelectedCheckBox(String filterName) {
        return page.locator("zeta-checkbox:text-is('" + filterName + "')")
            .locator("input[type='checkbox']");
    }

    /**
     * 根据索引获取过滤器复选框
     * 
     * @param filterIndex 复选框索引（从0开始）
     * @return 复选框定位器
     */
    public Locator getFilterCheckBox(int filterIndex) {
        return this.filterCheckBox.nth(filterIndex);
    }

    /**
     * 根据索引获取已选中的过滤器复选框
     * 
     * @param filterIndex 复选框索引（从0开始）
     * @return 复选框定位器
     */
    public Locator getSelectedFilterCheckBox(int filterIndex) {
        return this.selectedFilterCheckBox.nth(filterIndex);
    }

    /**
     * 根据过滤器名称获取复选框
     * 
     * @param filterName 过滤器名称
     * @return 复选框定位器
     */
    public Locator getFilterCheckBox(String filterName) {
        return page.locator("zeta-checkbox:text-is('" + filterName + "')");
    }

    /**
     * 获取指定过滤器的图标（通过 Role）
     * 
     * @param filter 过滤器名称
     * @return 过滤器图标定位器
     */
    public Locator getFilterIcon(String filter) {
        return page.getByRole(AriaRole.COLUMNHEADER, 
            new Page.GetByRoleOptions().setName(filter + " filter"))
            .locator("zeta-icon");
    }

    /**
     * 获取租户切换项
     * 
     * @param tenantName 租户名称
     * @return 租户项定位器
     */
    public Locator tenantSwitchItem(String tenantName) {
        return page.getByText(tenantName);
    }

    /**
     * 获取当前激活的租户项
     * 
     * @param tenantName 租户名称
     * @return 激活的租户项定位器
     */
    public Locator activeTenantItem(String tenantName) {
        return page.locator("div[class*='active']")
            .filter(new Locator.FilterOptions().setHasText(tenantName));
    }

    // ========== 通用页面操作 ==========

    /**
     * 刷新页面
     */
    public void refreshPage() {
        page.reload();
    }
}

