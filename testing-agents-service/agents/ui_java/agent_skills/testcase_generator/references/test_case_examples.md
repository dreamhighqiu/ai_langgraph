# 测试用例示例

## 1. 功能测试用例示例 (UI 测试)

### TC_LOGIN_001 - 正常登录

| 字段 | 内容 |
|------|------|
| **用例ID** | TC_LOGIN_001 |
| **模块** | 用户登录 |
| **用例标题** | 正常登录 - 使用有效凭据 |
| **优先级** | P0 |
| **测试类型** | functional |
| **前置条件** | 1. 用户已注册<br>2. 账号状态正常<br>3. 在登录页面 |
| **测试步骤** | 1. 输入正确的用户名 → 用户名显示在输入框<br>2. 输入正确的密码 → 密码以掩码显示<br>3. 点击登录按钮 → 页面跳转 |
| **预期结果** | 登录成功，跳转到首页，显示用户信息 |
| **定位器** | 1. page.getByLabel("用户名")<br>2. page.getByLabel("密码")<br>3. page.getByRole(BUTTON, "登录") |
| **测试数据** | username: test@test.com<br>password: ValidPass123! |
| **标签** | smoke, functional, auth |
| **状态** | 未执行 |

### TC_LOGIN_002 - 登录失败 - 密码错误

| 字段 | 内容 |
|------|------|
| **用例ID** | TC_LOGIN_002 |
| **模块** | 用户登录 |
| **用例标题** | 登录失败 - 密码错误 |
| **优先级** | P0 |
| **测试类型** | negative |
| **前置条件** | 1. 用户已注册<br>2. 在登录页面 |
| **测试步骤** | 1. 输入正确的用户名 → 用户名显示正常<br>2. 输入错误的密码 → 密码以掩码显示<br>3. 点击登录按钮 → 显示错误提示 |
| **预期结果** | 显示"用户名或密码错误"提示，停留在登录页面 |
| **定位器** | 1. page.getByLabel("用户名")<br>2. page.getByLabel("密码")<br>3. page.getByRole(BUTTON, "登录") |
| **测试数据** | username: test@test.com<br>password: WrongPassword |
| **标签** | negative, validation |
| **状态** | 未执行 |

---

## 2. 全量测试用例示例

### TC_FORM_001 - 表单提交 - 必填字段为空

| 字段 | 内容 |
|------|------|
| **用例ID** | TC_FORM_001 |
| **模块** | 表单提交 |
| **用例标题** | 表单提交 - 必填字段为空 |
| **优先级** | P1 |
| **测试类型** | negative |
| **前置条件** | 在表单页面 |
| **测试步骤** | 1. 保持必填字段为空 → 字段显示空状态<br>2. 点击提交按钮 → 显示验证错误 |
| **预期结果** | 显示必填字段验证错误提示 |
| **测试数据** | - |
| **标签** | negative, validation |

### TC_FORM_002 - 表单提交 - 字段长度边界

| 字段 | 内容 |
|------|------|
| **用例ID** | TC_FORM_002 |
| **模块** | 表单提交 |
| **用例标题** | 表单提交 - 字段长度边界 |
| **优先级** | P2 |
| **测试类型** | boundary |
| **前置条件** | 在表单页面 |
| **测试步骤** | 1. 输入超长文本（超过最大长度限制）→ 文本被截断或显示提示<br>2. 点击提交按钮 → 验证字段长度 |
| **预期结果** | 正确处理边界长度，显示适当提示 |
| **测试数据** | input: "a" × 500 (超长文本) |
| **标签** | boundary |

### TC_SECURITY_001 - SQL 注入防护

| 字段 | 内容 |
|------|------|
| **用例ID** | TC_SECURITY_001 |
| **模块** | 安全测试 |
| **用例标题** | SQL 注入防护 |
| **优先级** | P1 |
| **测试类型** | security |
| **前置条件** | 在登录页面 |
| **测试步骤** | 1. 在用户名输入SQL注入语句 → 输入框显示注入内容<br>2. 输入任意密码 → 密码以掩码显示<br>3. 点击登录按钮 → 系统拒绝登录 |
| **预期结果** | 登录失败，系统未被注入，无异常行为 |
| **测试数据** | username: ' OR '1'='1<br>password: anything |
| **标签** | security |

---

## 3. 从测试用例生成的 Java 代码示例

基于 TC_LOGIN_001 生成的 Java 测试代码：

```java
/**
 * 登录功能测试
 * 基于测试用例：TC_LOGIN_001, TC_LOGIN_002
 */
@ExtendWith(ReportPortalExtension.class)
class LoginPageTest extends Hook {
    
    private LoginPage loginPage;
    
    @BeforeEach
    void setUp() {
        loginPage = pagesContext.getLoginPage();
        page.navigate(BASE_URL + "/login");
    }
    
    /**
     * TC_LOGIN_001 - 正常登录 - 使用有效凭据
     * 优先级: P0
     * 前置条件: 用户已注册，账号状态正常
     */
    @Test
    @Tag("smoke")
    @Tag("functional")
    void testNormalLoginWithValidCredentials() throws InterruptedException {
        // 步骤 1: 输入正确的用户名
        loginPage.usernameInput().fill("test@test.com");
        assertThat(loginPage.usernameInput()).hasValue("test@test.com");
        
        // 步骤 2: 输入正确的密码
        loginPage.passwordInput().fill("ValidPass123!");
        
        // 步骤 3: 点击登录按钮
        loginPage.loginButton().click();
        
        // 验证: 登录成功，跳转到首页
        assertThat(page).hasURL(Pattern.compile(".*/dashboard"));
        assertThat(loginPage.userInfo()).isVisible();
    }
    
    /**
     * TC_LOGIN_002 - 登录失败 - 密码错误
     * 优先级: P0
     * 前置条件: 用户已注册
     */
    @Test
    @Tag("negative")
    @Tag("validation")
    void testLoginFailureWithWrongPassword() throws InterruptedException {
        // 步骤 1: 输入正确的用户名
        loginPage.usernameInput().fill("test@test.com");
        
        // 步骤 2: 输入错误的密码
        loginPage.passwordInput().fill("WrongPassword");
        
        // 步骤 3: 点击登录按钮
        loginPage.loginButton().click();
        
        // 验证: 显示错误提示，停留在登录页面
        assertThat(loginPage.errorMessage()).isVisible();
        assertThat(loginPage.errorMessage()).containsText("用户名或密码错误");
        assertThat(page).hasURL(Pattern.compile(".*/login"));
    }
}
```

---

## 4. Excel 导出格式说明

### UI 测试用例 Excel 列定义

| 列名 | 宽度 | 说明 |
|------|------|------|
| 用例ID | 15 | 唯一标识，如 TC_LOGIN_001 |
| 模块 | 15 | 功能模块名称 |
| 用例标题 | 40 | 测试用例名称 |
| 优先级 | 8 | P0/P1/P2/P3，带颜色标记 |
| 测试类型 | 12 | functional/ui/smoke |
| 前置条件 | 30 | 多行显示 |
| 测试步骤 | 50 | 带预期的步骤描述 |
| 预期结果 | 30 | 最终预期结果 |
| 定位器 | 40 | Playwright 定位器（UI 专用）|
| 测试数据 | 25 | key: value 格式 |
| 标签 | 15 | 逗号分隔 |
| 状态 | 10 | 执行状态 |

### 全量测试用例 Excel 列定义

| 列名 | 宽度 | 说明 |
|------|------|------|
| 用例ID | 15 | 唯一标识 |
| 模块 | 15 | 功能模块名称 |
| 用例标题 | 40 | 测试用例名称 |
| 优先级 | 8 | P0/P1/P2/P3 |
| 测试类型 | 12 | 包含所有类型 |
| 前置条件 | 30 | 多行显示 |
| 测试步骤 | 50 | 详细步骤 |
| 预期结果 | 30 | 预期结果 |
| 测试数据 | 25 | 测试数据 |
| 标签 | 15 | 分类标签 |
| 状态 | 10 | 执行状态 |
| 备注 | 20 | 额外说明 |

