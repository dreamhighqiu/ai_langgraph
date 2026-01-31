package com.deepseek.tests.base;

import com.microsoft.playwright.*;
import org.junit.jupiter.api.*;
import java.nio.file.Paths;
import static org.junit.jupiter.api.Assertions.*;

public class BaseTest {
    protected static Playwright playwright;
    protected static Browser browser;
    protected BrowserContext context;
    protected Page page;
    
    @BeforeAll
    public static void setUpAll() {
        playwright = Playwright.create();
        browser = playwright.chromium().launch(new BrowserType.LaunchOptions()
            .setHeadless(false)
            .setSlowMo(100));
    }
    
    @AfterAll
    public static void tearDownAll() {
        if (browser != null) {
            browser.close();
        }
        if (playwright != null) {
            playwright.close();
        }
    }
    
    @BeforeEach
    public void setUp() {
        context = browser.newContext(new Browser.NewContextOptions()
            .setViewportSize(1920, 1080));
        page = context.newPage();
    }
    
    @AfterEach
    public void tearDown(TestInfo testInfo) {
        if (page != null) {
            // Take screenshot on test failure
            if (testInfo.getTags().contains("screenshot")) {
                try {
                    page.screenshot(new Page.ScreenshotOptions()
                        .setPath(Paths.get("screenshots/" + testInfo.getDisplayName() + ".png"))
                        .setFullPage(true));
                } catch (Exception e) {
                    System.err.println("Failed to take screenshot: " + e.getMessage());
                }
            }
            page.close();
        }
        if (context != null) {
            context.close();
        }
    }
    
    protected void navigateToHomePage() {
        page.navigate("https://www.deepseek.com/");
        page.waitForLoadState(LoadState.NETWORKIDLE);
    }
    
    protected void takeScreenshot(String testName) {
        try {
            page.screenshot(new Page.ScreenshotOptions()
                .setPath(Paths.get("screenshots/" + testName + ".png"))
                .setFullPage(true));
        } catch (Exception e) {
            System.err.println("Failed to take screenshot: " + e.getMessage());
        }
    }
}