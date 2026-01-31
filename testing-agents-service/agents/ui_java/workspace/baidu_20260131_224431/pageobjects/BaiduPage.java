package com.baidu.pageobject;

import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.options.AriaRole;

/**
 * 百度首页 PageObject 类
 * 包含百度首页所有元素的定位器
 */
public class BaiduPage {
    
    private final Page page;
    
    // 页面URL
    public static final String URL = "https://www.baidu.com/";
    
    // 页面标题
    public static final String PAGE_TITLE = "百度一下，你就知道";
    
    // 构造函数
    public BaiduPage(Page page) {
        this.page = page;
    }
    
    // ==================== 顶部导航栏元素 ====================
    
    /**
     * 获取新闻链接
     */
    public Locator getNewsLink() {
        return page.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName("新闻"));
    }
    
    /**
     * 获取hao123链接
     */
    public Locator getHao123Link() {
        return page.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName("hao123"));
    }
    
    /**
     * 获取地图链接
     */
    public Locator getMapLink() {
        return page.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName("地图"));
    }
    
    /**
     * 获取贴吧链接
     */
    public Locator getTiebaLink() {
        return page.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName("贴吧"));
    }
    
    /**
     * 获取视频链接
     */
    public Locator getVideoLink() {
        return page.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName("视频"));
    }
    
    /**
     * 获取图片链接
     */
    public Locator getImageLink() {
        return page.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName("图片"));
    }
    
    /**
     * 获取网盘链接
     */
    public Locator getPanLink() {
        return page.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName("网盘"));
    }
    
    /**
     * 获取文库链接
     */
    public Locator getWenkuLink() {
        return page.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName("文库"));
    }
    
    /**
     * 获取更多链接
     */
    public Locator getMoreLink() {
        return page.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName("更多"));
    }
    
    /**
     * 获取设置链接
     */
    public Locator getSettingsLink() {
        return page.getByText("设置");
    }
    
    /**
     * 获取登录链接
     */
    public Locator getLoginLink() {
        return page.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName("登录"));
    }
    
    // ==================== 搜索区域元素 ====================
    
    /**
     * 获取搜索输入框
     */
    public Locator getSearchInput() {
        return page.locator("#kw");
    }
    
    /**
     * 获取百度一下按钮
     */
    public Locator getSearchButton() {
        return page.locator("#su");
    }
    
    /**
     * 获取搜索建议下拉框
     */
    public Locator getSearchSuggestions() {
        return page.locator(".bdsug");
    }
    
    /**
     * 获取语音输入按钮
     */
    public Locator getVoiceInputButton() {
        return page.locator(".soutu-btn");
    }
    
    /**
     * 获取图片搜索按钮
     */
    public Locator getImageSearchButton() {
        return page.locator(".soutu-btn");
    }
    
    // ==================== AI功能区域元素 ====================
    
    /**
     * 获取文心助手链接
     */
    public Locator getWenxinAssistantLink() {
        return page.getByText("复杂问题就找文心助手");
    }
    
    /**
     * 获取AI生图链接
     */
    public Locator getAIImageLink() {
        return page.getByText("AI生图");
    }
    
    /**
     * 获取AI写作链接
     */
    public Locator getAIWritingLink() {
        return page.getByText("AI写作");
    }
    
    /**
     * 获取AI翻译链接
     */
    public Locator getAITranslationLink() {
        return page.getByText("AI翻译");
    }
    
    /**
     * 获取AI编程链接
     */
    public Locator getAIProgrammingLink() {
        return page.getByText("AI编程");
    }
    
    /**
     * 获取更多AI工具链接
     */
    public Locator getMoreAIToolsLink() {
        return page.locator(".more-ai-tools");
    }
    
    // ==================== 百度热搜区域元素 ====================
    
    /**
     * 获取百度热搜标题
     */
    public Locator getHotSearchTitle() {
        return page.getByText("百度热搜");
    }
    
    /**
     * 获取换一换按钮
     */
    public Locator getRefreshHotSearchButton() {
        return page.getByText("换一换");
    }
    
    /**
     * 获取热搜列表
     */
    public Locator getHotSearchList() {
        return page.locator(".hotsearch-item");
    }
    
    /**
     * 获取指定位置的热搜项
     * @param index 热搜位置（1-10）
     */
    public Locator getHotSearchItem(int index) {
        return page.locator(String.format(".hotsearch-item:nth-child(%d)", index));
    }
    
    // ==================== 页脚区域元素 ====================
    
    /**
     * 获取关于百度链接
     */
    public Locator getAboutBaiduLink() {
        return page.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName("关于百度"));
    }
    
    /**
     * 获取About Baidu链接
     */
    public Locator getAboutBaiduEnLink() {
        return page.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName("About Baidu"));
    }
    
    /**
     * 获取使用百度前必读链接
     */
    public Locator getTermsLink() {
        return page.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName("使用百度前必读"));
    }
    
    /**
     * 获取帮助中心链接
     */
    public Locator getHelpCenterLink() {
        return page.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName("帮助中心"));
    }
    
    /**
     * 获取企业推广链接
     */
    public Locator getEnterpriseLink() {
        return page.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName("企业推广"));
    }
    
    /**
     * 获取备案信息
     */
    public Locator getRecordInfo() {
        return page.getByText("京公网安备11000002000001号");
    }
    
    /**
     * 获取ICP备案号
     */
    public Locator getICPRecord() {
        return page.getByText("京ICP证030173号");
    }
    
    // ==================== 通用方法 ====================
    
    /**
     * 导航到百度首页
     */
    public void navigate() {
        page.navigate(URL);
    }
    
    /**
     * 获取页面标题
     */
    public String getPageTitle() {
        return page.title();
    }
    
    /**
     * 执行搜索
     * @param keyword 搜索关键词
     */
    public void search(String keyword) {
        getSearchInput().fill(keyword);
        getSearchButton().click();
    }
    
    /**
     * 检查页面是否加载完成
     */
    public boolean isPageLoaded() {
        return page.title().contains(PAGE_TITLE) && getSearchInput().isVisible();
    }
    
    /**
     * 获取当前URL
     */
    public String getCurrentUrl() {
        return page.url();
    }
    
    /**
     * 等待页面加载
     */
    public void waitForPageLoad() {
        page.waitForLoadState();
    }
    
    /**
     * 检查元素是否可见
     * @param locator 元素定位器
     * @return 是否可见
     */
    public boolean isElementVisible(Locator locator) {
        try {
            return locator.isVisible();
        } catch (Exception e) {
            return false;
        }
    }
    
    /**
     * 获取页面截图
     * @param filename 截图文件名
     */
    public void takeScreenshot(String filename) {
        page.screenshot(new Page.ScreenshotOptions().setPath(filename));
    }
}