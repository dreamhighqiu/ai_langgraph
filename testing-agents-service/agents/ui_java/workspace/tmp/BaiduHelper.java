package com.baidu.helper;

import com.baidu.pageobject.BaiduPage;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.assertions.PlaywrightAssertions;
import org.junit.jupiter.api.Assertions;

import java.util.List;

/**
 * 百度首页 Helper 类
 * 封装百度首页的业务操作
 */
public class BaiduHelper {
    
    private final BaiduPage baiduPage;
    private final Page page;
    
    // 超时时间常量
    private static final int TIMEOUT_SECONDS_15 = 15;
    private static final int TIMEOUT_SECONDS_30 = 30;
    
    // 构造函数
    public BaiduHelper(Page page) {
        this.page = page;
        this.baiduPage = new BaiduPage(page);
    }
    
    // ==================== 页面导航和验证方法 ====================
    
    /**
     * 导航到百度首页并验证
     */
    public void navigateToBaiduHomePage() {
        baiduPage.navigate();
        baiduPage.waitForPageLoad();
        verifyPageLoaded();
    }
    
    /**
     * 验证页面是否成功加载
     */
    public void verifyPageLoaded() {
        // 验证页面标题
        String pageTitle = baiduPage.getPageTitle();
        Assertions.assertTrue(pageTitle.contains(BaiduPage.PAGE_TITLE), 
            "页面标题不正确，期望包含: " + BaiduPage.PAGE_TITLE + "，实际: " + pageTitle);
        
        // 验证搜索框可见
        PlaywrightAssertions.assertThat(baiduPage.getSearchInput())
            .isVisible();
        
        // 验证搜索按钮可见
        PlaywrightAssertions.assertThat(baiduPage.getSearchButton())
            .isVisible();
        
        System.out.println("百度首页加载验证通过");
    }
    
    /**
     * 验证页面元素可见性
     */
    public void verifyPageElementsVisibility() {
        // 验证顶部导航链接
        verifyNavigationLinksVisible();
        
        // 验证搜索区域
        verifySearchAreaVisible();
        
        // 验证AI功能区域
        verifyAIFunctionsVisible();
        
        // 验证百度热搜区域
        verifyHotSearchVisible();
        
        // 验证页脚区域
        verifyFooterVisible();
        
        System.out.println("页面所有元素可见性验证通过");
    }
    
    // ==================== 搜索功能方法 ====================
    
    /**
     * 执行搜索并验证
     * @param keyword 搜索关键词
     */
    public void searchAndVerify(String keyword) {
        // 输入搜索关键词
        baiduPage.getSearchInput().fill(keyword);
        
        // 点击搜索按钮
        baiduPage.getSearchButton().click();
        
        // 等待页面加载
        page.waitForLoadState();
        
        // 验证搜索结果页面
        verifySearchResultsPage(keyword);
    }
    
    /**
     * 验证搜索结果页面
     * @param keyword 搜索关键词
     */
    public void verifySearchResultsPage(String keyword) {
        // 验证URL包含搜索关键词
        String currentUrl = baiduPage.getCurrentUrl();
        Assertions.assertTrue(currentUrl.contains(keyword), 
            "搜索结果页面URL不包含搜索关键词: " + keyword);
        
        // 验证页面标题包含搜索关键词
        String pageTitle = baiduPage.getPageTitle();
        Assertions.assertTrue(pageTitle.contains(keyword), 
            "搜索结果页面标题不包含搜索关键词: " + keyword);
        
        System.out.println("搜索功能验证通过，关键词: " + keyword);
    }
    
    /**
     * 测试空搜索
     */
    public void testEmptySearch() {
        // 清空搜索框
        baiduPage.getSearchInput().fill("");
        
        // 点击搜索按钮
        baiduPage.getSearchButton().click();
        
        // 验证页面没有跳转
        String currentUrl = baiduPage.getCurrentUrl();
        Assertions.assertEquals(BaiduPage.URL, currentUrl, 
            "空搜索时页面不应跳转");
        
        System.out.println("空搜索测试通过");
    }
    
    /**
     * 测试超长字符串搜索
     * @param longString 超长字符串
     */
    public void testLongStringSearch(String longString) {
        searchAndVerify(longString);
        System.out.println("超长字符串搜索测试通过，字符串长度: " + longString.length());
    }
    
    /**
     * 测试特殊字符搜索
     * @param specialChars 特殊字符
     */
    public void testSpecialCharsSearch(String specialChars) {
        searchAndVerify(specialChars);
        System.out.println("特殊字符搜索测试通过: " + specialChars);
    }
    
    // ==================== 导航链接功能方法 ====================
    
    /**
     * 验证导航链接可见性
     */
    public void verifyNavigationLinksVisible() {
        // 验证主要导航链接
        String[] navLinks = {"新闻", "hao123", "地图", "贴吧", "视频", "图片", "网盘", "文库", "更多"};
        
        for (String linkText : navLinks) {
            PlaywrightAssertions.assertThat(page.getByText(linkText))
                .isVisible();
        }
        
        // 验证设置和登录链接
        PlaywrightAssertions.assertThat(baiduPage.getSettingsLink())
            .isVisible();
        PlaywrightAssertions.assertThat(baiduPage.getLoginLink())
            .isVisible();
        
        System.out.println("导航链接可见性验证通过");
    }
    
    /**
     * 点击导航链接并验证
     * @param linkText 链接文本
     */
    public void clickNavigationLinkAndVerify(String linkText) {
        // 点击链接
        page.getByText(linkText).click();
        
        // 等待新页面加载
        page.waitForLoadState();
        
        // 验证页面跳转
        String currentUrl = baiduPage.getCurrentUrl();
        Assertions.assertNotEquals(BaiduPage.URL, currentUrl, 
            "点击导航链接后页面应跳转");
        
        System.out.println("导航链接点击验证通过: " + linkText);
        
        // 返回百度首页
        navigateToBaiduHomePage();
    }
    
    // ==================== AI功能方法 ====================
    
    /**
     * 验证AI功能区域可见性
     */
    public void verifyAIFunctionsVisible() {
        // 验证文心助手链接
        PlaywrightAssertions.assertThat(baiduPage.getWenxinAssistantLink())
            .isVisible();
        
        // 验证AI工具链接
        String[] aiTools = {"AI生图", "AI写作", "AI翻译", "AI编程"};
        for (String tool : aiTools) {
            PlaywrightAssertions.assertThat(page.getByText(tool))
                .isVisible();
        }
        
        System.out.println("AI功能区域可见性验证通过");
    }
    
    /**
     * 点击AI功能链接并验证
     * @param linkText 链接文本
     */
    public void clickAIFunctionAndVerify(String linkText) {
        // 点击链接
        page.getByText(linkText).click();
        
        // 等待新页面加载
        page.waitForLoadState();
        
        // 验证页面跳转
        String currentUrl = baiduPage.getCurrentUrl();
        Assertions.assertNotEquals(BaiduPage.URL, currentUrl, 
            "点击AI功能链接后页面应跳转");
        
        System.out.println("AI功能链接点击验证通过: " + linkText);
        
        // 返回百度首页
        navigateToBaiduHomePage();
    }
    
    // ==================== 百度热搜功能方法 ====================
    
    /**
     * 验证百度热搜区域可见性
     */
    public void verifyHotSearchVisible() {
        // 验证热搜标题
        PlaywrightAssertions.assertThat(baiduPage.getHotSearchTitle())
            .isVisible();
        
        // 验证换一换按钮
        PlaywrightAssertions.assertThat(baiduPage.getRefreshHotSearchButton())
            .isVisible();
        
        // 验证热搜列表
        int hotSearchCount = baiduPage.getHotSearchList().count();
        Assertions.assertTrue(hotSearchCount >= 5, 
            "热搜列表项数量不足，期望至少5个，实际: " + hotSearchCount);
        
        System.out.println("百度热搜区域可见性验证通过，热搜项数量: " + hotSearchCount);
    }
    
    /**
     * 点击热搜项并验证
     * @param index 热搜项索引（从1开始）
     */
    public void clickHotSearchItemAndVerify(int index) {
        // 获取热搜项文本
        String hotSearchText = baiduPage.getHotSearchItem(index).textContent();
        
        // 点击热搜项
        baiduPage.getHotSearchItem(index).click();
        
        // 等待新页面加载
        page.waitForLoadState();
        
        // 验证页面跳转
        String currentUrl = baiduPage.getCurrentUrl();
        Assertions.assertNotEquals(BaiduPage.URL, currentUrl, 
            "点击热搜项后页面应跳转");
        
        System.out.println("热搜项点击验证通过，索引: " + index + "，内容: " + hotSearchText);
        
        // 返回百度首页
        navigateToBaiduHomePage();
    }
    
    /**
     * 测试换一换功能
     */
    public void testRefreshHotSearch() {
        // 获取当前热搜列表
        List<String> beforeRefresh = baiduPage.getHotSearchList()
            .allTextContents();
        
        // 点击换一换按钮
        baiduPage.getRefreshHotSearchButton().click();
        
        // 等待列表更新
        page.waitForTimeout(2000); // 等待2秒让列表更新
        
        // 获取更新后的热搜列表
        List<String> afterRefresh = baiduPage.getHotSearchList()
            .allTextContents();
        
        // 验证列表已更新（至少有一个不同）
        boolean hasChange = false;
        for (int i = 0; i < Math.min(beforeRefresh.size(), afterRefresh.size()); i++) {
            if (!beforeRefresh.get(i).equals(afterRefresh.get(i))) {
                hasChange = true;
                break;
            }
        }
        
        Assertions.assertTrue(hasChange, "换一换功能未更新热搜列表");
        
        System.out.println("换一换功能测试通过");
    }
    
    // ==================== 页脚功能方法 ====================
    
    /**
     * 验证页脚区域可见性
     */
    public void verifyFooterVisible() {
        // 验证页脚链接
        String[] footerLinks = {"关于百度", "About Baidu", "使用百度前必读", "帮助中心", "企业推广"};
        for (String link : footerLinks) {
            PlaywrightAssertions.assertThat(page.getByText(link))
                .isVisible();
        }
        
        // 验证备案信息
        PlaywrightAssertions.assertThat(baiduPage.getRecordInfo())
            .isVisible();
        PlaywrightAssertions.assertThat(baiduPage.getICPRecord())
            .isVisible();
        
        System.out.println("页脚区域可见性验证通过");
    }
    
    /**
     * 点击页脚链接并验证
     * @param linkText 链接文本
     */
    public void clickFooterLinkAndVerify(String linkText) {
        // 点击链接
        page.getByText(linkText).click();
        
        // 等待新页面加载
        page.waitForLoadState();
        
        // 验证页面跳转
        String currentUrl = baiduPage.getCurrentUrl();
        Assertions.assertNotEquals(BaiduPage.URL, currentUrl, 
            "点击页脚链接后页面应跳转");
        
        System.out.println("页脚链接点击验证通过: " + linkText);
        
        // 返回百度首页
        navigateToBaiduHomePage();
    }
    
    // ==================== 安全测试方法 ====================
    
    /**
     * 测试XSS攻击输入
     * @param xssInput XSS攻击代码
     */
    public void testXSSInput(String xssInput) {
        searchAndVerify(xssInput);
        
        // 验证页面没有执行恶意脚本
        // 这里可以添加更详细的安全验证逻辑
        System.out.println("XSS攻击输入测试完成: " + xssInput);
    }
    
    /**
     * 测试SQL注入输入
     * @param sqlInjection SQL注入代码
     */
    public void testSQLInjection(String sqlInjection) {
        searchAndVerify(sqlInjection);
        
        // 验证页面正常显示，没有数据库错误
        // 这里可以添加更详细的安全验证逻辑
        System.out.println("SQL注入输入测试完成: " + sqlInjection);
    }
    
    // ==================== 性能测试方法 ====================
    
    /**
     * 测量页面加载时间
     * @return 页面加载时间（毫秒）
     */
    public long measurePageLoadTime() {
        long startTime = System.currentTimeMillis();
        navigateToBaiduHomePage();
        long endTime = System.currentTimeMillis();
        
        long loadTime = endTime - startTime;
        System.out.println("页面加载时间: " + loadTime + "ms");
        
        return loadTime;
    }
    
    /**
     * 测量搜索响应时间
     * @param keyword 搜索关键词
     * @return 搜索响应时间（毫秒）
     */
    public long measureSearchResponseTime(String keyword) {
        // 确保在百度首页
        navigateToBaiduHomePage();
        
        long startTime = System.currentTimeMillis();
        searchAndVerify(keyword);
        long endTime = System.currentTimeMillis();
        
        long responseTime = endTime - startTime;
        System.out.println("搜索响应时间: " + responseTime + "ms，关键词: " + keyword);
        
        return responseTime;
    }
    
    // ==================== 通用工具方法 ====================
    
    /**
     * 获取BaiduPage实例
     */
    public BaiduPage getBaiduPage() {
        return baiduPage;
    }
    
    /**
     * 获取Page实例
     */
    public Page getPage() {
        return page;
    }
    
    /**
     * 截图并保存
     * @param screenshotName 截图名称
     */
    public void takeScreenshot(String screenshotName) {
        baiduPage.takeScreenshot("screenshots/" + screenshotName + ".png");
        System.out.println("截图已保存: " + screenshotName);
    }
}