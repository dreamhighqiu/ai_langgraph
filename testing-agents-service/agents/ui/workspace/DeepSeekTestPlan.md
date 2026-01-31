# DeepSeek网站自动化测试计划

## 项目概述
为DeepSeek官方网站（https://www.deepseek.com/）创建自动化测试套件，使用Playwright for Java框架。

## 测试架构设计

### 1. 项目结构
```
deepseek-automation-tests/
├── src/test/java/
│   ├── com/deepseek/tests/
│   │   ├── base/
│   │   │   ├── BaseTest.java
│   │   │   └── TestSetup.java
│   │   ├── pages/
│   │   │   ├── HomePage.java
│   │   │   ├── EnglishHomePage.java
│   │   │   └── ChatPage.java
│   │   ├── tests/
│   │   │   ├── FunctionalTests.java
│   │   │   ├── NavigationTests.java
│   │   │   └── ContentTests.java
│   │   └── utils/
│   │       ├── ConfigReader.java
│   │       └── TestData.java
├── src/test/resources/
│   ├── config.properties
│   └── test-data.json
├── pom.xml
└── README.md
```

### 2. 依赖配置 (pom.xml)
```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.deepseek</groupId>
    <artifactId>deepseek-automation-tests</artifactId>
    <version>1.0.0</version>

    <properties>
        <maven.compiler.source>11</maven.compiler.source>
        <maven.compiler.target>11</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        <playwright.version>1.45.0</playwright.version>
        <junit.version>5.10.0</junit.version>
    </properties>

    <dependencies>
        <!-- Playwright for Java -->
        <dependency>
            <groupId>com.microsoft.playwright</groupId>
            <artifactId>playwright</artifactId>
            <version>${playwright.version}</version>
        </dependency>
        
        <!-- JUnit 5 -->
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter-api</artifactId>
            <version>${junit.version}</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter-engine</artifactId>
            <version>${junit.version}</version>
            <scope>test</scope>
        </dependency>
        
        <!-- AssertJ for fluent assertions -->
        <dependency>
            <groupId>org.assertj</groupId>
            <artifactId>assertj-core</artifactId>
            <version>3.25.3</version>
            <scope>test</scope>
        </dependency>
        
        <!-- Logging -->
        <dependency>
            <groupId>org.slf4j</groupId>
            <artifactId>slf4j-simple</artifactId>
            <version>2.0.9</version>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-surefire-plugin</artifactId>
                <version>3.2.2</version>
            </plugin>
        </plugins>
    </build>
</project>
```

### 3. 配置文件 (config.properties)
```properties
# Application URLs
base.url=https://www.deepseek.com
english.url=https://www.deepseek.com/en/
chat.url=https://chat.deepseek.com
platform.url=https://platform.deepseek.com

# Browser settings
browser=chromium
headless=false
slow.mo=100
timeout=30000

# Test settings
screenshot.on.failure=true
video.on.failure=false
```

### 4. 基础测试类设计

#### BaseTest.java
```java
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
                page.screenshot(new Page.ScreenshotOptions()
                    .setPath(Paths.get("screenshots/" + testInfo.getDisplayName() + ".png"))
                    .setFullPage(true));
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
}
```

### 5. 页面对象模型设计

#### HomePage.java
```java
package com.deepseek.tests.pages;

import com.microsoft.playwright.Page;
import com.microsoft.playwright.Locator;
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
    
    public HomePage(Page page) {
        this.page = page;
        
        // Initialize locators using robust selectors
        this.logo = page.locator("img[alt*='DeepSeek Logo']");
        this.englishLink = page.getByRole("link", new Page.GetByRoleOptions().setName("English"));
        this.startChatButton = page.getByRole("link", new Page.GetByRoleOptions().setName("开始对话"));
        this.apiPlatformLink = page.getByRole("link", new Page.GetByRoleOptions().setName("API开放平台"));
        this.announcementLink = page.getByRole("link", new Page.GetByRoleOptions()
            .setName("DeepSeek-V3.2 正式版发布"));
        this.getAppLink = page.getByRole("link", new Page.GetByRoleOptions().setName("获取手机 App"));
    }
    
    // Navigation methods
    public void navigate() {
        page.navigate("https://www.deepseek.com/");
        page.waitForLoadState(LoadState.NETWORKIDLE);
    }
    
    public void switchToEnglish() {
        englishLink.click();
        page.waitForURL("**/en/");
    }
    
    public void startChat() {
        startChatButton.click();
    }
    
    public void openAPIPlatform() {
        apiPlatformLink.click();
    }
    
    // Validation methods
    public boolean isLogoVisible() {
        return logo.isVisible();
    }
    
    public String getPageTitle() {
        return page.title();
    }
    
    public boolean isChineseVersion() {
        return page.url().contains("/zh/") || !page.url().contains("/en/");
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
        return page.locator(String.format("a[href*='%s']", platform));
    }
    
    public Locator getFooterLink(String text) {
        return page.getByRole("link", new Page.GetByRoleOptions().setName(text));
    }
}
```

### 6. 测试用例实现

#### FunctionalTests.java
```java
package com.deepseek.tests.tests;

import com.deepseek.tests.base.BaseTest;
import com.deepseek.tests.pages.HomePage;
import org.junit.jupiter.api.*;
import static org.assertj.core.api.Assertions.*;

@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
@Tag("functional")
public class FunctionalTests extends BaseTest {
    private HomePage homePage;
    
    @BeforeEach
    public void setUpTest() {
        homePage = new HomePage(page);
        homePage.navigate();
    }
    
    @Test
    @Order(1)
    @DisplayName("TC-001: 验证首页正常加载")
    public void testHomePageLoadsSuccessfully() {
        // Verify page title
        assertThat(homePage.getPageTitle())
            .contains("DeepSeek");
        
        // Verify logo is visible
        assertThat(homePage.isLogoVisible())
            .isTrue();
        
        // Verify main navigation elements
        assertThat(page.getByRole("link", new Page.GetByRoleOptions().setName("开始对话")).isVisible())
            .isTrue();
        assertThat(page.getByRole("link", new Page.GetByRoleOptions().setName("API开放平台")).isVisible())
            .isTrue();
    }
    
    @Test
    @Order(2)
    @DisplayName("TC-002: 验证语言切换功能")
    public void testLanguageSwitching() {
        // Verify initial language is Chinese
        assertThat(homePage.isChineseVersion())
            .isTrue();
        
        // Switch to English
        homePage.switchToEnglish();
        
        // Verify switched to English
        assertThat(homePage.isEnglishVersion())
            .isTrue();
        assertThat(homePage.getPageTitle())
            .isEqualTo("DeepSeek");
        
        // Switch back to Chinese
        page.getByRole("link", new Page.GetByRoleOptions().setName("中文")).click();
        page.waitForURL("https://www.deepseek.com/");
        
        // Verify back to Chinese
        assertThat(homePage.isChineseVersion())
            .isTrue();
    }
    
    @Test
    @Order(3)
    @DisplayName("TC-003: 验证主要功能链接")
    @Tag("screenshot")
    public void testMainFunctionLinks() {
        // Test Start Chat button
        homePage.startChat();
        
        // Verify new tab opened with chat page
        Page chatPage = page.waitForPopup(() -> {});
        assertThat(chatPage.url())
            .contains("chat.deepseek.com");
        chatPage.close();
        
        // Test API Platform link
        homePage.openAPIPlatform();
        
        // Verify new tab opened with platform page
        Page platformPage = page.waitForPopup(() -> {});
        assertThat(platformPage.url())
            .contains("platform.deepseek.com");
        platformPage.close();
    }
    
    @Test
    @Order(4)
    @DisplayName("TC-004: 验证社交媒体链接")
    public void testSocialMediaLinks() {
        homePage.scrollToFooter();
        
        // Test GitHub link
        Locator githubLink = homePage.getSocialMediaLink("github.com");
        assertThat(githubLink.isVisible())
            .isTrue();
        
        // Test email link
        Locator emailLink = page.locator("a[href^='mailto:']");
        assertThat(emailLink.isVisible())
            .isTrue();
        assertThat(emailLink.getAttribute("href"))
            .isEqualTo("mailto:service@deepseek.com");
    }
    
    @Test
    @Order(5)
    @DisplayName("TC-005: 验证法律信息和备案")
    public void testLegalInformation() {
        homePage.scrollToFooter();
        
        // Verify ICP备案号
        assertThat(page.getByText("浙ICP备2023025841号").isVisible())
            .isTrue();
        
        // Verify privacy policy link
        Locator privacyLink = homePage.getFooterLink("隐私政策");
        assertThat(privacyLink.isVisible())
            .isTrue();
        assertThat(privacyLink.getAttribute("href"))
            .contains("privacy-policy");
        
        // Verify terms of use link
        Locator termsLink = homePage.getFooterLink("用户协议");
        assertThat(termsLink.isVisible())
            .isTrue();
        assertThat(termsLink.getAttribute("href"))
            .contains("terms-of-use");
    }
    
    @Test
    @Order(6)
    @DisplayName("TC-006: 验证公告链接")
    public void testAnnouncementLink() {
        // Verify announcement is visible
        Locator announcement = page.getByRole("link", new Page.GetByRoleOptions()
            .setName("DeepSeek-V3.2 正式版发布"));
        assertThat(announcement.isVisible())
            .isTrue();
        
        // Click announcement and verify external link
        Page announcementPage = page.waitForPopup(() -> {
            announcement.click();
        });
        
        assertThat(announcementPage.url())
            .contains("weixin.qq.com");
        announcementPage.close();
    }
    
    @Test
    @Order(7)
    @DisplayName("TC-007: 验证页面性能")
    public void testPagePerformance() {
        // Record page load time
        long startTime = System.currentTimeMillis();
        homePage.navigate();
        long loadTime = System.currentTimeMillis() - startTime;
        
        // Verify page loads within acceptable time
        assertThat(loadTime)
            .isLessThan(5000); // 5 seconds maximum
        
        // Log performance metrics
        System.out.println("Page load time: " + loadTime + "ms");
    }
    
    @Test
    @Order(8)
    @DisplayName("TC-008: 验证响应式设计")
    public void testResponsiveDesign() {
        // Test different viewport sizes
        int[] widths = {1920, 1366, 768, 375};
        
        for (int width : widths) {
            page.setViewportSize(width, 800);
            homePage.navigate();
            
            // Verify logo is still visible
            assertThat(homePage.isLogoVisible())
                .as("Logo should be visible at width " + width)
                .isTrue();
            
            // Verify main buttons are accessible
            assertThat(page.getByRole("link", new Page.GetByRoleOptions().setName("开始对话")).isVisible())
                .as("Start Chat button should be visible at width " + width)
                .isTrue();
        }
    }
}
```

### 7. 测试数据管理

#### TestData.java
```java
package com.deepseek.tests.utils;

import java.util.Arrays;
import java.util.List;

public class TestData {
    public static final String BASE_URL = "https://www.deepseek.com/";
    public static final String ENGLISH_URL = "https://www.deepseek.com/en/";
    public static final String CHAT_URL = "https://chat.deepseek.com";
    public static final String PLATFORM_URL = "https://platform.deepseek.com";
    
    public static final String EXPECTED_TITLE_ZH = "DeepSeek | 深度求索";
    public static final String EXPECTED_TITLE_EN = "DeepSeek";
    
    public static final List<String> SOCIAL_MEDIA_PLATFORMS = Arrays.asList(
        "github.com",
        "twitter.com",
        "zhihu.com",
        "xiaohongshu.com"
    );
    
    public static final List<String> FOOTER_SECTIONS = Arrays.asList(
        "研究",
        "产品", 
        "法律 & 安全",
        "加入我们"
    );
    
    public static final List<String> LEGAL_LINKS = Arrays.asList(
        "隐私政策",
        "用户协议",
        "反馈安全漏洞"
    );
}
```

### 8. 测试执行配置

#### testng.xml (可选)
```xml
<!DOCTYPE suite SYSTEM "https://testng.org/testng-1.0.dtd">
<suite name="DeepSeek Automation Suite" verbose="1">
    <test name="Functional Tests">
        <classes>
            <class name="com.deepseek.tests.tests.FunctionalTests"/>
        </classes>
    </test>
</suite>
```

### 9. 运行测试
```bash
# 使用Maven运行所有测试
mvn test

# 运行特定测试类
mvn test -Dtest=FunctionalTests

# 运行带标签的测试
mvn test -Dgroups=functional

# 生成测试报告
mvn surefire-report:report
```

### 10. 持续集成配置 (GitHub Actions)

#### .github/workflows/ci.yml
```yaml
name: DeepSeek Automation Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up JDK 11
      uses: actions/setup-java@v3
      with:
        java-version: '11'
        distribution: 'temurin'
    
    - name: Install Playwright browsers
      run: mvn exec:java -e -Dexec.mainClass=com.microsoft.playwright.CLI -Dexec.args="install"
    
    - name: Run tests
      run: mvn test
    
    - name: Upload test results
     