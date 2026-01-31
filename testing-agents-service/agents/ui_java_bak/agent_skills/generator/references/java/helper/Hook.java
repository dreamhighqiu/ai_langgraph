package com.example.helper;

import com.microsoft.playwright.*;
import com.microsoft.playwright.options.LoadState;
import com.example.context.*;
import com.example.pageobject.*;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.TestInfo;
import org.junit.jupiter.api.extension.ExtendWith;

import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Arrays;

import static com.example.common.TimeoutUtility.*;
import static com.example.property.AppProperty.*;

/**
 * Hook 基类 - 提供 Playwright 测试的基础设施
 * 
 * 功能:
 * - Playwright 浏览器生命周期管理
 * - 页面对象初始化
 * - Helper 工具类初始化
 * - 登录处理和会话管理
 * - 截图和追踪
 * - 测试清理
 * 
 * 使用方式:
 * 所有测试类继承此类以获得 Playwright 支持
 * 
 * @author Test Automation Team
 */
@ExtendWith(AllureExtension.class)
public class Hook {
    // Playwright 实例
    public Playwright playwright;
    public Page page;
    public BrowserContext context;

    // 测试上下文
    public String testcaseName;
    public byte[] screenshot;
    public PlaywrightContext playwrightContext;
    public PagesContext pagesContext;
    public HelperContext helperContext;
    public UserAccountProperty userAccountProperty;

    // Helper 工具类
    public DeviceInventoryHelper deviceInventoryHelper;
    public CommonHelper commonHelper;
    public LoginHelper loginHelper;
    public UsersHelper usersHelper;

    // 当前测试使用的账号
    private String currentTestAccount;

    /**
     * 测试前置设置 - 在每个测试方法执行前运行
     * 
     * 步骤:
     * 1. 获取测试账号
     * 2. 初始化上下文对象
     * 3. 启动浏览器
     * 4. 初始化页面对象和工具类
     * 5. 登录应用
     */
    @BeforeEach
    public void testSetup(TestInfo testInfo) throws InterruptedException {
        // 1. 获取测试账号
        currentTestAccount = getTestAccount();
        System.out.println("Test account: " + currentTestAccount);

        // 2. 初始化上下文
        playwrightContext = new PlaywrightContext();
        pagesContext = new PagesContext();
        helperContext = new HelperContext();
        userAccountProperty = new UserAccountProperty();

        // 3. 启动浏览器
        startBrowser();

        // 4. 初始化页面对象和工具类
        initAllPagesAndUtils();

        // 5. 登录（除非测试标记为 SkipLogin）
        boolean shouldSkipLogin = testInfo.getTags().contains("SkipLogin");
        if (!shouldSkipLogin) {
            loginToWebPortal(currentTestAccount);
        } else {
            page.navigate(URL);
        }
    }

    /**
     * 启动 Playwright 浏览器
     * 
     * 配置:
     * - Chromium 浏览器
     * - 无头模式（可配置）
     * - 视口最大化
     * - 接受下载
     * - 忽略 HTTPS 错误
     */
    private void startBrowser() {
        playwright = Playwright.create();
        playwrightContext.setPlaywright(playwright);

        // 浏览器启动选项
        BrowserType.LaunchOptions launchOptions = new BrowserType.LaunchOptions()
                .setHeadless(AppProperty.runHeadless)
                .setArgs(Arrays.asList(
                        "--no-sandbox",
                        "--disable-dev-shm-usage",
                        "--start-maximized"
                ))
                .setTimeout(60_000);

        Browser browser = playwright.chromium().launch(launchOptions);

        // 浏览器上下文选项
        Browser.NewContextOptions contextOptions = new Browser.NewContextOptions()
                .setViewportSize(null)
                .setAcceptDownloads(true)
                .setIgnoreHTTPSErrors(true);

        // 尝试加载保存的会话状态（快速登录）
        Path savedAuthState = loadAuthState(currentTestAccount);
        if (savedAuthState != null) {
            contextOptions.setStorageStatePath(savedAuthState);
            System.out.println("Loading saved session state");
        }

        BrowserContext ctx = browser.newContext(contextOptions);
        ctx.setDefaultNavigationTimeout(60_000);
        this.context = ctx;
        playwrightContext.setContext(ctx);
        
        this.page = ctx.newPage();
        playwrightContext.setPage(page);

        // 启动追踪（用于调试）
        ctx.tracing().start(new Tracing.StartOptions()
                .setScreenshots(true)
                .setSnapshots(true)
                .setSources(true));
    }

    /**
     * 初始化所有页面对象和工具类
     * 
     * 模式:
     * - PageObject 模式: 封装页面元素
     * - Helper 模式: 封装业务操作
     * - Context 模式: 管理对象依赖
     */
    private void initAllPagesAndUtils() {
        // 初始化页面对象
        pagesContext.setDeviceInventoryPage(new DeviceInventoryPage(page));
        pagesContext.setCommonPage(new CommonPage(page));
        pagesContext.setLoginPage(new LoginPage(page));
        pagesContext.setUsersPage(new UsersPage(page));

        // 初始化 Helper 工具类
        commonHelper = new CommonHelper(playwrightContext, pagesContext);
        loginHelper = new LoginHelper(pagesContext);
        deviceInventoryHelper = new DeviceInventoryHelper(pagesContext);
        usersHelper = new UsersHelper(pagesContext, helperContext);

        // 设置 Helper 上下文
        helperContext.setCommonHelper(commonHelper);
        helperContext.setLoginHelper(loginHelper);
        helperContext.setDeviceInventoryHelper(deviceInventoryHelper);
        helperContext.setUsersHelper(usersHelper);
    }

    /**
     * 登录到 Web 应用
     * 
     * 步骤:
     * 1. 导航到应用 URL
     * 2. 检查是否已登录（通过会话状态）
     * 3. 如未登录，执行登录流程
     * 4. 保存会话状态（用于后续快速登录）
     * 
     * @param username 用户名
     */
    protected void loginToWebPortal(String username) throws InterruptedException {
        System.out.println("=== Login Process Start ===");
        System.out.println("Username: " + username);
        
        // 1. 导航到 URL
        page.navigate(URL);
        page.waitForLoadState(LoadState.DOMCONTENTLOADED);

        // 2. 检查是否已登录
        try {
            if (pagesContext.getDeviceInventoryPage().pageTitle.isVisible()) {
                System.out.println("Already logged in with saved session");
                deviceInventoryHelper.verifyAllKeyElementsOnDeviceInventoryPresence();
                userAccountProperty.setCurrentTestAccount(currentTestAccount);
                return;
            }
        } catch (Exception e) {
            System.out.println("Not logged in, proceeding to login");
        }

        // 3. 执行登录
        loginHelper.loginWithCredentials(username, userAccountProperty.accountPassword);
        
        // 4. 验证登录成功
        deviceInventoryHelper.verifyAllKeyElementsOnDeviceInventoryPresence();
        userAccountProperty.setCurrentTestAccount(currentTestAccount);

        System.out.println("=== Login Process Complete ===");
    }

    /**
     * 测试清理 - 在每个测试方法执行后运行
     * 
     * 步骤:
     * 1. 保存会话状态
     * 2. 截图
     * 3. 停止追踪
     * 4. 关闭浏览器资源
     * 5. 返还测试账号
     */
    @AfterEach
    public void tearDown(TestInfo testInfo) {
        try {
            testcaseName = testInfo.getDisplayName()
                .replace("()", "")
                .replace("/", "_");

            // 1. 保存会话状态
            if (context != null && currentTestAccount != null) {
                saveAuthState(context, currentTestAccount);
            }

            // 2. 截图和追踪
            quitBrowserAndResources(testcaseName);
        } finally {
            // 3. 返还测试账号
            if (currentTestAccount != null) {
                releaseTestAccount(currentTestAccount);
                currentTestAccount = null;
            }
        }
    }

    /**
     * 关闭浏览器并保存资源
     * 
     * @param testcaseName 测试用例名称
     */
    private void quitBrowserAndResources(String testcaseName) {
        // 截图
        if (page != null && !page.isClosed()) {
            try {
                Path screenshotPath = Paths.get("screenshots", testcaseName + ".png");
                screenshot = page.screenshot(
                    new Page.ScreenshotOptions().setPath(screenshotPath)
                );
            } catch (Exception e) {
                System.err.println("Screenshot failed: " + e.getMessage());
            }
        }

        // 停止追踪
        if (context != null) {
            try {
                Path tracePath = Paths.get("traces", testcaseName + ".zip");
                context.tracing().stop(
                    new Tracing.StopOptions().setPath(tracePath)
                );
            } catch (Exception e) {
                System.err.println("Tracing save failed: " + e.getMessage());
            }
        }

        // 关闭资源
        closeResource(context, "BrowserContext");
        closeResource(playwright, "Playwright");
    }

    /**
     * 安全关闭资源
     */
    private void closeResource(AutoCloseable resource, String resourceName) {
        if (resource != null) {
            try {
                resource.close();
                System.out.println(resourceName + " closed successfully.");
            } catch (Exception e) {
                System.err.println("Error closing " + resourceName + ": " + e.getMessage());
            }
        }
    }

    // ========== 辅助方法 ==========

    /**
     * 获取测试账号（从账号池）
     */
    private String getTestAccount() {
        // 实现账号池逻辑
        return "test_user@example.com";
    }

    /**
     * 释放测试账号（返还到账号池）
     */
    private void releaseTestAccount(String account) {
        // 实现账号池逻辑
        System.out.println("Released account: " + account);
    }

    /**
     * 加载保存的会话状态
     */
    private Path loadAuthState(String username) {
        Path authStatePath = Paths.get("auth-states", username + ".json");
        if (authStatePath.toFile().exists()) {
            return authStatePath;
        }
        return null;
    }

    /**
     * 保存会话状态
     */
    private void saveAuthState(BrowserContext context, String username) {
        try {
            Path authStatePath = Paths.get("auth-states", username + ".json");
            context.storageState(new BrowserContext.StorageStateOptions()
                .setPath(authStatePath));
            System.out.println("Auth state saved: " + authStatePath);
        } catch (Exception e) {
            System.err.println("Failed to save auth state: " + e.getMessage());
        }
    }
}

