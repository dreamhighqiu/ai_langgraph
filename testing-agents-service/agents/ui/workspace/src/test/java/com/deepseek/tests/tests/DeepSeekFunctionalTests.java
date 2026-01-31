package com.deepseek.tests.tests;

import com.deepseek.tests.base.BaseTest;
import com.deepseek.tests.pages.HomePage;
import com.deepseek.tests.utils.TestData;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.Locator;
import org.junit.jupiter.api.*;
import org.junit.jupiter.api.MethodOrderer.OrderAnnotation;

import static org.assertj.core.api.Assertions.*;

@TestMethodOrder(OrderAnnotation.class)
@Tag("functional")
@DisplayName("DeepSeek网站功能测试")
public class DeepSeekFunctionalTests extends BaseTest {
    private HomePage homePage;
    
    @BeforeEach
    public void setUpTest() {
        homePage = new HomePage(page);
    }
    
    @Test
    @Order(1)
    @DisplayName("TC-001: 验证首页正常加载")
    @Tag("smoke")
    public void testHomePageLoadsSuccessfully() {
        // Given: 访问DeepSeek首页
        homePage.navigate();
        
        // When: 页面加载完成
        homePage.waitForPageLoad();
        
        // Then: 验证页面标题
        assertThat(homePage.getPageTitle())
            .as("页面标题应该包含DeepSeek")
            .contains("DeepSeek");
        
        // And: 验证Logo可见
        assertThat(homePage.isLogoVisible())
            .as("Logo应该可见")
            .isTrue();
        
        // And: 验证主要按钮可见
        assertThat(page.getByRole("link", new Page.GetByRoleOptions().setName("开始对话")).isVisible())
            .as("'开始对话'按钮应该可见")
            .isTrue();
        assertThat(page.getByRole("link", new Page.GetByRoleOptions().setName("API开放平台")).isVisible())
            .as("'API开放平台'按钮应该可见")
            .isTrue();
        
        // And: 验证公告链接可见
        assertThat(page.getByRole("link", new Page.GetByRoleOptions()
            .setName("DeepSeek-V3.2 正式版发布")).isVisible())
            .as("公告链接应该可见")
            .isTrue();
            
        System.out.println("✓ TC-001: 首页加载测试通过");
    }
    
    @Test
    @Order(2)
    @DisplayName("TC-002: 验证语言切换功能")
    @Tag("regression")
    public void testLanguageSwitching() {
        // Given: 访问中文首页
        homePage.navigate();
        
        // When: 切换到英文版
        homePage.switchToEnglish();
        
        // Then: 验证切换到英文版
        assertThat(homePage.isEnglishVersion())
            .as("应该切换到英文版")
            .isTrue();
        assertThat(homePage.getPageTitle())
            .as("英文版标题应该是'DeepSeek'")
            .isEqualTo("DeepSeek");
        
        // And: 验证英文版内容
        assertThat(page.getByRole("link", new Page.GetByRoleOptions().setName("Start Now")).isVisible())
            .as("'Start Now'按钮应该可见")
            .isTrue();
        
        // When: 切换回中文版
        homePage.switchToChinese();
        
        // Then: 验证切换回中文版
        assertThat(homePage.isChineseVersion())
            .as("应该切换回中文版")
            .isTrue();
        assertThat(homePage.getPageTitle())
            .as("中文版标题应该包含'深度求索'")
            .contains("深度求索");
            
        System.out.println("✓ TC-002: 语言切换测试通过");
    }
    
    @Test
    @Order(3)
    @DisplayName("TC-003: 验证主要功能链接")
    @Tag("integration")
    @Tag("screenshot")
    public void testMainFunctionLinks() {
        // Given: 访问中文首页
        homePage.navigate();
        
        // When: 点击"开始对话"按钮
        homePage.startChat();
        
        // Then: 验证新标签页打开聊天页面
        Page chatPage = page.waitForPopup(() -> {});
        assertThat(chatPage.url())
            .as("应该跳转到聊天页面")
            .contains("chat.deepseek.com");
        
        // Close chat page and go back to main page
        chatPage.close();
        page.bringToFront();
        
        // When: 点击"API开放平台"链接
        homePage.openAPIPlatform();
        
        // Then: 验证新标签页打开平台页面
        Page platformPage = page.waitForPopup(() -> {});
        assertThat(platformPage.url())
            .as("应该跳转到API平台页面")
            .contains("platform.deepseek.com");
        
        platformPage.close();
        System.out.println("✓ TC-003: 主要功能链接测试通过");
    }
    
    @Test
    @Order(4)
    @DisplayName("TC-004: 验证社交媒体链接")
    public void testSocialMediaLinks() {
        // Given: 访问首页并滚动到底部
        homePage.navigate();
        homePage.scrollToFooter();
        
        // Then: 验证GitHub链接
        Locator githubLink = homePage.getSocialMediaLink("github.com");
        assertThat(githubLink.isVisible())
            .as("GitHub链接应该可见")
            .isTrue();
        
        // And: 验证邮箱链接
        Locator emailLink = page.locator("a[href^='mailto:service@deepseek.com']");
        assertThat(emailLink.isVisible())
            .as("邮箱链接应该可见")
            .isTrue();
        assertThat(emailLink.getAttribute("href"))
            .as("邮箱地址应该正确")
            .isEqualTo("mailto:service@deepseek.com");
        
        // And: 验证其他社交媒体链接
        for (String platform : TestData.SOCIAL_MEDIA_PLATFORMS) {
            if (!platform.equals("github.com")) {
                Locator socialLink = homePage.getSocialMediaLink(platform);
                assertThat(socialLink.count())
                    .as(platform + " 链接应该存在")
                    .isGreaterThan(0);
            }
        }
        
        System.out.println("✓ TC-004: 社交媒体链接测试通过");
    }
    
    @Test
    @Order(5)
    @DisplayName("TC-005: 验证法律信息和备案")
    public void testLegalInformation() {
        // Given: 访问首页并滚动到底部
        homePage.navigate();
        homePage.scrollToFooter();
        
        // Then: 验证ICP备案号
        assertThat(page.getByText(TestData.ICP_NUMBER).isVisible())
            .as("ICP备案号应该可见")
            .isTrue();
        
        // And: 验证公安备案号
        assertThat(page.getByText(TestData.PUBLIC_SECURITY_NUMBER).isVisible())
            .as("公安备案号应该可见")
            .isTrue();
        
        // And: 验证隐私政策链接
        Locator privacyLink = homePage.getFooterLink("隐私政策");
        assertThat(privacyLink.isVisible())
            .as("隐私政策链接应该可见")
            .isTrue();
        assertThat(privacyLink.getAttribute("href"))
            .as("隐私政策链接应该有效")
            .contains("privacy-policy");
        
        // And: 验证用户协议链接
        Locator termsLink = homePage.getFooterLink("用户协议");
        assertThat(termsLink.isVisible())
            .as("用户协议链接应该可见")
            .isTrue();
        assertThat(termsLink.getAttribute("href"))
            .as("用户协议链接应该有效")
            .contains("terms-of-use");
        
        System.out.println("✓ TC-005: 法律信息测试通过");
    }
    
    @Test
    @Order(6)
    @DisplayName("TC-006: 验证公告链接")
    public void testAnnouncementLink() {
        // Given: 访问首页
        homePage.navigate();
        
        // When: 点击公告链接
        homePage.openAnnouncement();
        
        // Then: 验证新标签页打开公告页面
        Page announcementPage = page.waitForPopup(() -> {});
        assertThat(announcementPage.url())
            .as("应该跳转到公告页面")
            .contains("weixin.qq.com");
        
        announcementPage.close();
        System.out.println("✓ TC-006: 公告链接测试通过");
    }
    
    @Test
    @Order(7)
    @DisplayName("TC-007: 验证页面性能")
    @Tag("performance")
    public void testPagePerformance() {
        // Given: 记录开始时间
        long startTime = System.currentTimeMillis();
        
        // When: 访问首页
        homePage.navigate();
        homePage.waitForPageLoad();
        
        // Then: 计算加载时间
        long loadTime = System.currentTimeMillis() - startTime;
        
        // Verify page loads within acceptable time
        assertThat(loadTime)
            .as("页面加载时间应该在5秒以内")
            .isLessThan(5000);
        
        // Log performance metrics
        System.out.println("✓ TC-007: 页面性能测试通过 - 加载时间: " + loadTime + "ms");
    }
    
    @Test
    @Order(8)
    @DisplayName("TC-008: 验证响应式设计")
    @Tag("responsive")
    public void testResponsiveDesign() {
        // Test different viewport sizes
        int[][] viewports = {
            {1920, 1080},  // Desktop
            {1366, 768},   // Laptop
            {768, 1024},   // Tablet
            {375, 667}     // Mobile
        };
        
        for (int i = 0; i < viewports.length; i++) {
            int width = viewports[i][0];
            int height = viewports[i][1];
            
            // When: 设置视口大小并访问首页
            page.setViewportSize(width, height);
            homePage.navigate();
            
            // Then: 验证Logo可见
            assertThat(homePage.isLogoVisible())
                .as("Logo应该在 " + width + "x" + height + " 分辨率下可见")
                .isTrue();
            
            // And: 验证主要按钮可访问
            Locator startChatButton = page.getByRole("link", new Page.GetByRoleOptions().setName("开始对话"));
            assertThat(startChatButton.isVisible() || startChatButton.count() > 0)
                .as("'开始对话'按钮应该在 " + width + "x" + height + " 分辨率下可访问")
                .isTrue();
        }
        
        System.out.println("✓ TC-008: 响应式设计测试通过");
    }
    
    @Test
    @Order(9)
    @DisplayName("TC-009: 验证页面内容完整性")
    public void testPageContentCompleteness() {
        // Given: 访问首页
        homePage.navigate();
        
        // Then: 验证所有主要部分都存在
        assertThat(page.locator("main").isVisible())
            .as("主内容区域应该可见")
            .isTrue();
        
        assertThat(page.locator("header, [role='banner']").first().isVisible())
            .as("页头应该可见")
            .isTrue();
        
        homePage.scrollToFooter();
        assertThat(page.locator("footer, [role='contentinfo']").first().isVisible())
            .as("页脚应该可见")
            .isTrue();
        
        // And: 验证关键文本内容
        assertThat(page.getByText("探索未知之境").isVisible())
            .as("主标题应该可见")
            .isTrue();
        
        assertThat(page.getByText("研究").isVisible())
            .as("研究部分应该可见")
            .isTrue();
        
        assertThat(page.getByText("产品").isVisible())
            .as("产品部分应该可见")
            .isTrue();
        
        System.out.println("✓ TC-009: 页面内容完整性测试通过");
    }
    
    @Test
    @Order(10)
    @DisplayName("TC-010: 验证导航功能")
    public void testNavigationFunctionality() {
        // Given: 访问首页
        homePage.navigate();
        
        // When: 点击"获取手机App"链接
        Locator getAppLink = page.getByRole("link", new Page.GetByRoleOptions().setName("获取手机 App"));
        assertThat(getAppLink.isVisible())
            .as("'获取手机App'链接应该可见")
            .isTrue();
        
        // And: 验证所有底部导航链接
        homePage.scrollToFooter();
        
        for (String section : TestData.FOOTER_SECTIONS_ZH) {
            Locator sectionElement = homePage.getFooterSection(section);
            assertThat(sectionElement.isVisible())
                .as("底部导航部分 '" + section + "' 应该可见")
                .isTrue();
        }
        
        System.out.println("✓ TC-010: 导航功能测试通过");
    }
}