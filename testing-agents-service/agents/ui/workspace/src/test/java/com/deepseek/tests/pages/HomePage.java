package com.deepseek.tests.pages;

import com.microsoft.playwright.Page;
import com.microsoft.playwright.Locator;
import com.microsoft.playwright.options.LoadState;
import static org.junit.jupiter.api.Assertions.*;

public class HomePage {
    private final Page page;
    
    // Locators
    private final Locator logo;
    private final Locator englishLink;
    private final Locator startChatButton;
    private final Locator apiPlatformLink;
    private final Locator announcementLink;
    private final Locator getAppLink;
    private final Locator chineseLink;
    
    public HomePage(Page page) {
        this.page = page;
        
        // Initialize locators using robust selectors
        this.logo = page.locator("img[alt*='DeepSeek Logo']").first();
        this.englishLink = page.getByRole("link", new Page.GetByRoleOptions().setName("English"));
        this.startChatButton = page.getByRole("link", new Page.GetByRoleOptions().setName("开始对话"));
        this.apiPlatformLink = page.getByRole("link", new Page.GetByRoleOptions().setName("API开放平台"));
        this.announcementLink = page.getByRole("link", new Page.GetByRoleOptions()
            .setName("DeepSeek-V3.2 正式版发布"));
        this.getAppLink = page.getByRole("link", new Page.GetByRoleOptions().setName("获取手机 App"));
        this.chineseLink = page.getByRole("link", new Page.GetByRoleOptions().setName("中文"));
    }
    
    // Navigation methods
    public void navigate() {
        page.navigate("https://www.deepseek.com/");
        page.waitForLoadState(LoadState.NETWORKIDLE);
    }
    
    public void navigateToEnglish() {
        page.navigate("https://www.deepseek.com/en/");
        page.waitForLoadState(LoadState.NETWORKIDLE);
    }
    
    public void switchToEnglish() {
        englishLink.click();
        page.waitForURL("**/en/");
        page.waitForLoadState(LoadState.NETWORKIDLE);
    }
    
    public void switchToChinese() {
        chineseLink.click();
        page.waitForURL("https://www.deepseek.com/");
        page.waitForLoadState(LoadState.NETWORKIDLE);
    }
    
    public void startChat() {
        startChatButton.click();
    }
    
    public void openAPIPlatform() {
        apiPlatformLink.click();
    }
    
    public void openAnnouncement() {
        announcementLink.click();
    }
    
    // Validation methods
    public boolean isLogoVisible() {
        return logo.isVisible();
    }
    
    public String getPageTitle() {
        return page.title();
    }
    
    public String getCurrentUrl() {
        return page.url();
    }
    
    public boolean isChineseVersion() {
        String url = page.url();
        return url.contains("/zh/") || (!url.contains("/en/") && url.contains("deepseek.com"));
    }
    
    public boolean isEnglishVersion() {
        return page.url().contains("/en/");
    }
    
    // Footer methods
    public void scrollToFooter() {
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)");
        page.waitForTimeout(500);
    }
    
    public Locator getSocialMediaLink(String platform) {
        return page.locator(String.format("a[href*='%s']", platform)).first();
    }
    
    public Locator getFooterLink(String text) {
        return page.getByRole("link", new Page.GetByRoleOptions().setName(text));
    }
    
    public Locator getFooterSection(String sectionTitle) {
        return page.getByText(sectionTitle);
    }
    
    // Wait methods
    public void waitForPageLoad() {
        page.waitForLoadState(LoadState.NETWORKIDLE);
    }
    
    // Element state checks
    public boolean isElementVisible(String selector) {
        return page.locator(selector).first().isVisible();
    }
    
    public String getElementText(String selector) {
        return page.locator(selector).first().textContent();
    }
}