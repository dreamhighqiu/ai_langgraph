package com.example.pageobject;

import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;

/**
 * DeviceInventoryPage - 设备库存页面对象类
 * 
 * 职责:
 * - 定义设备库存页面特有的UI元素
 * - 继承通用页面元素（CommonPage）
 * - 提供设备库存页面特有的定位器
 * 
 * 页面位置: /mobile-computers 或 /device-inventory
 * 
 * @author Test Automation Team
 */
public class DeviceInventoryPage extends CommonPage {

    // ========== 设备库存页面特有元素 ==========
    
    /** 页面标题 */
    public final Locator pageTitle;
    
    /** 设备库存表格 */
    public final Locator deviceTable;
    
    /** 设备行 */
    public final Locator deviceRows;
    
    /** 添加设备按钮 */
    public final Locator addDeviceButton;
    
    /** 导出按钮 */
    public final Locator exportButton;
    
    /** 批量操作按钮 */
    public final Locator bulkActionsButton;
    
    /** 全选复选框 */
    public final Locator selectAllCheckbox;

    // ========== 表格列定位器 ==========
    
    /** 模型列 */
    public final Locator modelColumn;
    
    /** 设备名称列 */
    public final Locator deviceNameColumn;
    
    /** 设备类型列 */
    public final Locator deviceTypeColumn;
    
    /** 序列号列 */
    public final Locator serialNumberColumn;
    
    /** OS 版本列 */
    public final Locator osVersionColumn;

    /**
     * 构造函数 - 初始化设备库存页面元素
     * 
     * @param page Playwright Page 对象
     */
    public DeviceInventoryPage(Page page) {
        super(page); // 继承 CommonPage 的所有元素
        
        // 页面特有元素
        this.pageTitle = page.locator("h1:has-text('Device Inventory'), h1:has-text('Mobile Computers')");
        this.deviceTable = page.locator("table").first();
        this.deviceRows = this.deviceTable.locator("tbody tr[data-index]");
        this.addDeviceButton = page.locator("zeta-button:has-text('Add Device')");
        this.exportButton = page.locator("zeta-button:has-text('Export')");
        this.bulkActionsButton = page.locator("zeta-button:has-text('Bulk Actions')");
        this.selectAllCheckbox = page.locator("thead input[type='checkbox']").first();
        
        // 表格列
        this.modelColumn = page.locator("th:has-text('Model')");
        this.deviceNameColumn = page.locator("th:has-text('Device Name')");
        this.deviceTypeColumn = page.locator("th:has-text('Device Type')");
        this.serialNumberColumn = page.locator("th:has-text('Serial Number')");
        this.osVersionColumn = page.locator("th:has-text('OS Version')");
    }

    // ========== 辅助方法 - 设备相关操作 ==========

    /**
     * 根据序列号获取设备行
     * 
     * @param serialNumber 设备序列号
     * @return 设备行定位器
     */
    public Locator getDeviceRowBySerialNumber(String serialNumber) {
        return page.locator(String.format("tr:has-text('%s')", serialNumber));
    }

    /**
     * 根据设备名称获取设备行
     * 
     * @param deviceName 设备名称
     * @return 设备行定位器
     */
    public Locator getDeviceRowByName(String deviceName) {
        return page.locator(String.format("tr:has-text('%s')", deviceName));
    }

    /**
     * 获取指定行的操作菜单按钮
     * 
     * @param rowIndex 行索引（从0开始）
     * @return 操作菜单按钮定位器
     */
    public Locator getActionsMenuInRow(int rowIndex) {
        return this.deviceRows.nth(rowIndex)
            .locator("zeta-icon-button:has-text('more_vertical')");
    }

    /**
     * 获取指定行的复选框
     * 
     * @param rowIndex 行索引（从0开始）
     * @return 复选框定位器
     */
    public Locator getCheckboxInRow(int rowIndex) {
        return this.deviceRows.nth(rowIndex).locator("input[type='checkbox']");
    }

    /**
     * 获取指定列的单元格值
     * 
     * @param rowIndex 行索引
     * @param columnName 列名（如 "Model", "Device Name"）
     * @return 单元格定位器
     */
    public Locator getCellValue(int rowIndex, String columnName) {
        // 获取列的索引
        int columnIndex = getColumnIndex(columnName);
        if (columnIndex == -1) {
            throw new IllegalArgumentException("Column not found: " + columnName);
        }
        
        return this.deviceRows.nth(rowIndex).locator("td").nth(columnIndex);
    }

    /**
     * 获取列的索引位置
     * 
     * @param columnName 列名
     * @return 列索引（从0开始），未找到返回-1
     */
    private int getColumnIndex(String columnName) {
        // 这是一个简化的实现，实际项目中可能需要动态查询
        switch (columnName) {
            case "Model":
                return 1;
            case "Device Name":
                return 2;
            case "Device Type":
                return 3;
            case "Serial Number":
                return 4;
            case "OS Version":
                return 5;
            default:
                return -1;
        }
    }
}

