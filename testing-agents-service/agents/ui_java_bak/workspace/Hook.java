package com.example.hook;

import com.microsoft.playwright.*;
import org.junit.jupiter.api.extension.AfterAllCallback;
import org.junit.jupiter.api.extension.BeforeAllCallback;
import org.junit.jupiter.api.extension.ExtensionContext;

import java.nio.file.Paths;

/**
 * 测试Hook类 - 管理Playwright生命周期
 * 实际项目中需要根据具体需求完善
 */
public class Hook implements BeforeAllCallback, AfterAllCallback {
    
    private static Playwright playwright;
    private static Browser browser;
    private static BrowserContext context;
    private static Page page;
    
    // 配置常量
    private static final boolean HEADLESS = true;
    private static final String BROWSER_TYPE = "chromium";
    private static final int VIEWPORT_WIDTH = 1920;
    private static final int VIEWPORT_HEIGHT = 1080;
    
    @Override
    public void beforeAll(ExtensionContext context) {
        // 初始化Playwright
        playwright = Playwright.create();
        
        // 创建浏览器实例
        BrowserType browserType = getBrowserType();
        browser = browserType.launch(new BrowserType.LaunchOptions()
            .setHeadless(HEADLESS)
            .setArgs(java.util.Arrays.asList("--disable-blink-features=AutomationControlled")));
        
        // 创建浏览器上下文
        this.context = browser.newContext(new Browser.NewContextOptions()
            .setViewportSize(VIEWPORT_WIDTH, VIEWPORT_HEIGHT)
            .setUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            .setIgnoreHTTPSErrors(true));
        
        // 启用追踪（可选）
        // this.context.tracing().start(new Tracing.StartOptions()
        //     .setScreenshots(true)
        //     .setSnapshots(true));
        
        // 创建页面
        page = this.context.newPage();
        
        // 设置默认超时
        page.setDefaultTimeout(30000);
        page.setDefaultNavigationTimeout(60000);
    }
    
    @Override
    public void afterAll(ExtensionContext context) {
        // 保存追踪（如果启用）
        // if (this.context != null) {
        //     this.context.tracing().stop(new Tracing.StopOptions()
        //         .setPath(Paths.get("trace.zip")));
        // }
        
        // 关闭资源
        if (page != null) {
            page.close();
        }
        if (this.context != null) {
            this.context.close();
        }
        if (browser != null) {
            browser.close();
        }
        if (playwright != null) {
            playwright.close();
        }
    }
    
    /**
     * 获取浏览器类型
     */
    private BrowserType getBrowserType() {
        switch (BROWSER_TYPE.toLowerCase()) {
            case "firefox":
                return playwright.firefox();
            case "webkit":
                return playwright.webkit();
            case "chromium":
            default:
                return playwright.chromium();
        }
    }
    
    /**
     * 获取Page对象（供测试类使用）
     */
    public static Page getPage() {
        return page;
    }
    
    /**
     * 获取BrowserContext对象
     */
    public static BrowserContext getContext() {
        return context;
    }
    
    /**
     * 获取Browser对象
     */
    public static Browser getBrowser() {
        return browser;
    }
    
    /**
     * 获取Playwright对象
     */
    public static Playwright getPlaywright() {
        return playwright;
    }
    
    /**
     * 环境检查 - 如果需要跳过测试可以调用
     */
    public static void skipIfEnvironmentNotReady() {
        // 检查网络连接
        // 检查测试环境可用性
        // 检查依赖服务状态
        
        // 如果环境不满足条件，可以抛出AssumptionViolatedException
        // org.junit.jupiter.api.Assumptions.assumeTrue(condition, message);
    }
    
    /**
     * 截图方法
     */
    public static void takeScreenshot(String testName) {
        if (page != null) {
            String screenshotPath = "screenshots/" + testName + "_" + 
                System.currentTimeMillis() + ".png";
            page.screenshot(new Page.ScreenshotOptions()
                .setPath(Paths.get(screenshotPath))
                .setFullPage(true));
        }
    }
    
    /**
     * 记录控制台日志
     */
    public static void captureConsoleLogs() {
        if (page != null) {
            page.onConsoleMessage(msg -> {
                System.out.println("Console [" + msg.type() + "]: " + msg.text());
            });
        }
    }
    
    /**
     * 记录网络请求
     */
    public static void captureNetworkRequests() {
        if (page != null) {
            page.onRequest(request -> {
                System.out.println("Request: " + request.method() + " " + request.url());
            });
            
            page.onResponse(response -> {
                System.out.println("Response: " + response.status() + " " + response.url());
            });
        }
    }
}