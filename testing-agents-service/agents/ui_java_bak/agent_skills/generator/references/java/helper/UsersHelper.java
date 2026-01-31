package com.example.helper;

import com.microsoft.playwright.Locator;
import com.example.context.*;
import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;
import static com.example.common.TimeoutUtility.TIMEOUT_SECONDS_15;
import static org.junit.jupiter.api.Assertions.assertEquals;

/**
 * UsersHelper - 用户管理页面操作辅助类
 * 
 * 职责:
 * - 封装用户相关的业务操作
 * - 提供可重用的用户管理方法
 * - 简化测试代码，提高可维护性
 * 
 * 使用模式: Helper Pattern
 * - 每个页面或功能模块有对应的 Helper
 * - Helper 方法封装多步骤操作
 * - 返回必要的数据供测试验证
 * 
 * @author Test Automation Team
 */
public class UsersHelper {

    private final PagesContext pagesContext;
    private final HelperContext helperContext;

    /**
     * 构造函数 - 依赖注入
     * 
     * @param pagesContext 页面对象上下文
     * @param helperContext Helper 上下文
     */
    public UsersHelper(PagesContext pagesContext, HelperContext helperContext) {
        this.pagesContext = pagesContext;
        this.helperContext = helperContext;
    }

    /**
     * 成功添加新用户的完整流程
     * 
     * 业务流程:
     * 1. 导航到用户页面
     * 2. 邀请新用户
     * 3. 验证成功消息
     * 4. 验证用户出现在列表中
     * 
     * @param email 用户邮箱
     * @throws InterruptedException 如果等待被中断
     */
    public void addNewUserSuccessfully(String email) throws InterruptedException {
        String expectedToastMessage = "User invited successfully!";
        String expectedStatus = "Invited";

        // 1. 导航到用户页面
        helperContext.getCommonHelper().goToUsersPage();

        // 2. 邀请新用户并获取提示消息
        String actualToastMessage = this.inviteUserAndGetToastMessage(email);

        // 3. 验证成功消息
        assertEquals(expectedToastMessage, actualToastMessage, 
            "The success toast message for inviting user was not correct.");

        // 4. 等待提示消息消失
        helperContext.getCommonHelper().waitForToastToDisappear(expectedToastMessage);

        // 5. 验证用户出现在列表中
        this.verifyUserInListWithStatus(email, expectedStatus);
    }

    /**
     * 邀请用户并获取提示消息
     * 
     * 步骤:
     * 1. 点击"添加用户"按钮
     * 2. 输入邮箱
     * 3. 点击"邀请"按钮
     * 4. 获取并返回提示消息
     * 
     * @param email 用户邮箱
     * @return Toast 提示消息
     */
    public String inviteUserAndGetToastMessage(String email) {
        // 1. 点击添加用户按钮
        CommonMethod.clickElement(
            pagesContext.getUsersPage().addUserButton, 
            TIMEOUT_SECONDS_15
        );
        
        // 验证对话框打开
        assertThat(pagesContext.getUsersPage().addUserDialog).isVisible();

        // 2. 输入邮箱
        CommonMethod.input(
            pagesContext.getUsersPage().emailInput, 
            email, 
            TIMEOUT_SECONDS_15
        );

        // 3. 点击邀请按钮
        CommonMethod.clickElement(
            pagesContext.getUsersPage().inviteButton, 
            TIMEOUT_SECONDS_15
        );

        // 4. 获取并返回提示消息
        return helperContext.getCommonHelper()
            .waitForAndGetToastText(TIMEOUT_SECONDS_15);
    }

    /**
     * 获取无效邮箱的错误消息
     * 
     * 用途: 负面测试场景
     * 
     * @param invalidEmail 无效的邮箱地址
     * @return 错误消息文本
     */
    public String getInvalidEmailErrorMessage(String invalidEmail) throws InterruptedException {
        // 打开添加用户对话框
        CommonMethod.clickElement(
            pagesContext.getUsersPage().addUserButton, 
            TIMEOUT_SECONDS_15
        );
        assertThat(pagesContext.getUsersPage().addUserDialog).isVisible();

        // 输入无效邮箱
        CommonMethod.input(
            pagesContext.getUsersPage().emailInput, 
            invalidEmail, 
            TIMEOUT_SECONDS_15
        );

        // 点击邀请按钮
        CommonMethod.clickElement(
            pagesContext.getUsersPage().inviteButton, 
            TIMEOUT_SECONDS_15
        );

        // 等待并获取错误消息
        Locator errorLocator = pagesContext.getUsersPage().invalidEmailError;
        CommonMethod.waitForElementVisible(errorLocator, TIMEOUT_SECONDS_15);
        return errorLocator.textContent();
    }

    /**
     * 验证用户在列表中存在且状态正确
     * 
     * 步骤:
     * 1. 搜索用户
     * 2. 验证用户行可见
     * 3. 验证用户状态
     * 4. 清空搜索
     * 
     * @param email 用户邮箱
     * @param expectedStatus 预期状态（如 "Invited", "Active"）
     */
    public void verifyUserInListWithStatus(String email, String expectedStatus) 
            throws InterruptedException {
        // 1. 搜索用户
        helperContext.getCommonHelper().performSearch(email);

        // 2. 获取用户行
        Locator userRow = pagesContext.getUsersPage().getUserRowByEmail(email);
        assertThat(userRow).isVisible();

        // 3. 验证状态
        assertThat(userRow.getByText(expectedStatus)).isVisible();

        // 4. 清空搜索
        helperContext.getCommonHelper().clearSearchBox();
        helperContext.getCommonHelper().waitForTableData(TIMEOUT_SECONDS_15);
    }

    /**
     * 搜索并验证部分匹配的用户
     * 
     * 用途: 测试搜索功能
     * 
     * @param searchTerm 搜索词
     * @param expectedUserEmails 预期匹配的用户邮箱列表
     */
    public void searchAndVerifyPartialMatches(String searchTerm, 
            java.util.List<String> expectedUserEmails) throws InterruptedException {
        // 执行搜索
        helperContext.getCommonHelper().performSearch(searchTerm);
        helperContext.getCommonHelper().waitForTableData(TIMEOUT_SECONDS_15);

        // 验证结果数量
        int initialRowCount = pagesContext.getUsersPage().allTableRows.count();
        assertThat(pagesContext.getUsersPage().allTableRows)
            .hasCount(expectedUserEmails.size());

        // 验证每个预期用户都存在
        for (String email : expectedUserEmails) {
            assertThat(pagesContext.getUsersPage().getUserRowByEmail(email))
                .isVisible();
        }

        // 清空搜索并验证
        helperContext.getCommonHelper()
            .clearSearchAndVerifyResultCount(initialRowCount);
    }

    /**
     * 删除用户
     * 
     * 步骤:
     * 1. 搜索用户
     * 2. 点击删除按钮
     * 3. 确认删除
     * 4. 返回提示消息
     * 
     * @param email 用户邮箱
     * @return 删除操作的提示消息
     */
    public String deleteUser(String email) throws InterruptedException {
        // 1. 搜索用户
        helperContext.getCommonHelper().performSearch(email);
        helperContext.getCommonHelper().waitForTableData(TIMEOUT_SECONDS_15);

        // 2. 获取用户行
        Locator userRow = pagesContext.getUsersPage().getUserRowByEmail(email);
        assertThat(userRow).isVisible();

        // 3. 点击操作菜单和删除按钮
        Locator menuIcon = userRow.locator(
            pagesContext.getUsersPage().actionsMenuIcon
        );
        if (CommonMethod.isVisible(menuIcon, TIMEOUT_SECONDS_15)) {
            CommonMethod.clickElement(menuIcon, TIMEOUT_SECONDS_15);
            CommonMethod.clickElement(
                pagesContext.getUsersPage().deleteButton, 
                TIMEOUT_SECONDS_15
            );
        } else {
            // 如果没有菜单图标，直接点击删除按钮
            CommonMethod.clickElement(
                userRow.locator(pagesContext.getUsersPage().deleteButton), 
                TIMEOUT_SECONDS_15
            );
        }

        // 4. 确认删除对话框
        assertThat(pagesContext.getUsersPage().deleteUserDialog).isVisible();
        CommonMethod.clickElement(
            pagesContext.getUsersPage().dialogConfirmButton, 
            TIMEOUT_SECONDS_15
        );

        // 5. 获取并返回提示消息
        return helperContext.getCommonHelper()
            .waitForAndGetToastText(TIMEOUT_SECONDS_15);
    }

    /**
     * 搜索并删除用户（如果存在）
     * 
     * 用途: 测试清理，确保测试数据干净
     * 
     * @param email 用户邮箱
     */
    public void searchAndDeleteUserIfExists(String email) {
        try {
            // 导航到用户页面
            helperContext.getCommonHelper().goToUsersPage();
            helperContext.getCommonHelper().waitForTableData(TIMEOUT_SECONDS_15);

            // 搜索用户
            helperContext.getCommonHelper().performSearch(email);
            helperContext.getCommonHelper().waitForTableData(TIMEOUT_SECONDS_15);

            // 检查用户是否存在
            Locator userRow = pagesContext.getUsersPage().getUserRowByEmail(email);
            if (CommonMethod.isVisible(userRow, TIMEOUT_SECONDS_15)) {
                System.out.println("Cleanup: User '" + email + "' found. Deleting.");

                // 删除用户
                Locator deleteButton = userRow.locator(
                    pagesContext.getUsersPage().deleteButton
                );
                if (CommonMethod.isVisible(deleteButton, 2000)) {
                    CommonMethod.clickElement(deleteButton, TIMEOUT_SECONDS_15);
                } else {
                    Locator menuIcon = userRow.locator(
                        pagesContext.getUsersPage().actionsMenuIcon
                    );
                    CommonMethod.clickElement(menuIcon, TIMEOUT_SECONDS_15);
                    CommonMethod.clickElement(
                        pagesContext.getUsersPage().deleteButton, 
                        TIMEOUT_SECONDS_15
                    );
                }

                // 确认删除
                assertThat(pagesContext.getUsersPage().deleteUserDialog).isVisible();
                CommonMethod.clickElement(
                    pagesContext.getUsersPage().dialogConfirmButton, 
                    TIMEOUT_SECONDS_15
                );

                // 等待提示消息
                String toastMessage = helperContext.getCommonHelper()
                    .waitForAndGetToastText(TIMEOUT_SECONDS_15);
                System.out.println("Cleanup successful. Toast: '" + toastMessage + "'");
                
                helperContext.getCommonHelper().waitForToastToDisappear(toastMessage);
                assertThat(userRow).isHidden();
            } else {
                System.out.println("Cleanup: User '" + email + "' not found.");
            }
        } catch (Exception e) {
            System.err.println("Cleanup error for user '" + email + "': " + e.getMessage());
        } finally {
            helperContext.getCommonHelper().clearSearchBox();
        }
    }

    /**
     * 取消用户邀请
     * 
     * @param email 用户邮箱
     * @return 提示消息
     */
    public String cancelInvitationForUser(String email) throws InterruptedException {
        // 搜索用户
        helperContext.getCommonHelper().performSearch(email);
        Locator userRow = pagesContext.getUsersPage().getUserRowByEmail(email);
        assertThat(userRow).isVisible();

        // 点击操作菜单
        Locator menuIcon = userRow.locator(
            pagesContext.getUsersPage().actionsMenuIcon
        );
        CommonMethod.clickElement(menuIcon, TIMEOUT_SECONDS_15);

        // 点击取消邀请按钮
        CommonMethod.clickElement(
            pagesContext.getUsersPage().cancelInviteButton, 
            TIMEOUT_SECONDS_15
        );

        // 确认对话框
        assertThat(pagesContext.getUsersPage().cancelInviteDialog).isVisible();
        CommonMethod.clickElement(
            pagesContext.getUsersPage().dialogConfirmButton, 
            TIMEOUT_SECONDS_15
        );

        // 返回提示消息
        return helperContext.getCommonHelper()
            .waitForAndGetToastText(TIMEOUT_SECONDS_15);
    }
}

