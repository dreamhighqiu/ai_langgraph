package com.zebra.helper;

import com.microsoft.playwright.Locator;
import com.zebra.common.AllureStepHelper;
import com.zebra.common.CommonMethod;
import com.zebra.context.*;
import java.util.List;
import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;
import static com.zebra.common.AllureStepHelper.step;
import static com.zebra.common.TimeoutUtility.TIMEOUT_SECONDS_15;
import static org.junit.jupiter.api.Assertions.assertEquals;

public class UsersHelper {

    private final PagesContext pagesContext;
    private final HelperContext helperContext;

    public UsersHelper(PagesContext pagesContext, HelperContext helperContext) {
        this.pagesContext = pagesContext;
        this.helperContext = helperContext;
    }

    public void addNewUserSuccessfully(String email) throws InterruptedException {
        String expectedToastMessage = "User invited successfully!";
        String expectedStatus = "Invited";

        step("Navigate to Users page", () -> {
            helperContext.getCommonHelper().goToUsersPage();
        });

        String actualToastMessage = step("Invite new user: " + email, () -> {
            AllureStepHelper.parameter("User email", email);
            return this.inviteUserAndGetToastMessage(email);
        });

        step("Verify success toast message", () -> {
            AllureStepHelper.parameter("Expected message", expectedToastMessage);
            AllureStepHelper.parameter("Actual message", actualToastMessage);
            assertEquals(expectedToastMessage, actualToastMessage, "The success toast message for inviting an external user was not correct.");
        });

        step("Wait for toast to disappear", () -> {
            helperContext.getCommonHelper().waitForToastToDisappear(expectedToastMessage);
        });

        step("Verify user in list with Invited status", () -> {
            AllureStepHelper.parameter("User email", email);
            AllureStepHelper.parameter("Expected status", expectedStatus);
            try {
                this.verifyUserInListWithStatus(email, expectedStatus);
            } catch (InterruptedException e) {
                throw new RuntimeException(e);
            }
        });
    }

    public String inviteUserAndGetToastMessage(String email) {
        return step("Invite user and get toast message", () -> {
            step("Click Add User button", () -> {
                CommonMethod.clickElement(pagesContext.getUsersPage().addUserButton, TIMEOUT_SECONDS_15);
                assertThat(pagesContext.getUsersPage().addUserDialog).isVisible();
            });

            step("Enter email and send invitation", () -> {
                AllureStepHelper.parameter("Email", email);
                CommonMethod.input(pagesContext.getUsersPage().emailNativeInput, email, TIMEOUT_SECONDS_15);
                CommonMethod.clickElement(pagesContext.getUsersPage().inviteButton, TIMEOUT_SECONDS_15);
            });

            return step("Get toast message", () -> {
                return helperContext.getCommonHelper().waitForAndGetToastText(TIMEOUT_SECONDS_15);
            });
        });
    }

    public String getInvalidEmailErrorMessage(String invalidEmail) throws InterruptedException {
        CommonMethod.clickElement(pagesContext.getUsersPage().addUserButton, TIMEOUT_SECONDS_15);
        assertThat(pagesContext.getUsersPage().addUserDialog).isVisible();

        CommonMethod.input(pagesContext.getUsersPage().emailNativeInput, invalidEmail, TIMEOUT_SECONDS_15);

        CommonMethod.clickElement(pagesContext.getUsersPage().inviteButton, TIMEOUT_SECONDS_15);

        Locator errorLocator = pagesContext.getUsersPage().invalidEmailError;
        CommonMethod.waitForElementVisble(errorLocator,TIMEOUT_SECONDS_15);
        return errorLocator.textContent();
    }

    public void verifyUserInListWithStatus(String email, String expectedStatus) throws InterruptedException {
        helperContext.getCommonHelper().performSearch(email);
        Locator userRow = pagesContext.getUsersPage().getUserRowByEmail(email);
        assertThat(userRow).isVisible();

        assertThat(userRow.getByText(expectedStatus)).isVisible();

        helperContext.getCommonHelper().clearSearchBox();
        helperContext.getCommonHelper().waitForTableData(TIMEOUT_SECONDS_15);
    }

    public void searchAndVerifyPartialMatches(String searchTerm, List<String> expectedUserEmails) throws InterruptedException {
        helperContext.getCommonHelper().performSearch(searchTerm);
        helperContext.getCommonHelper().waitForTableData(TIMEOUT_SECONDS_15);
        int initialRowCount = pagesContext.getUsersPage().allTableRows.count();
        assertThat(pagesContext.getUsersPage().allTableRows).hasCount(expectedUserEmails.size());

        for (String email : expectedUserEmails) {
            assertThat(pagesContext.getUsersPage().getUserRowByEmail(email)).isVisible();
        }

        helperContext.getCommonHelper().clearSearchAndVerifyResultCount(initialRowCount);
    }

    public String deleteUser(String email) throws InterruptedException {
        helperContext.getCommonHelper().performSearch(email);
        helperContext.getCommonHelper().waitForTableData(TIMEOUT_SECONDS_15);
        Locator userRow = pagesContext.getUsersPage().getUserRowByEmail(email);
        assertThat(userRow).isVisible();

        Locator menuIconInRow = userRow.locator(pagesContext.getUsersPage().actionsMenuIcon);
        if (CommonMethod.isVisible(menuIconInRow, TIMEOUT_SECONDS_15)) {
            CommonMethod.clickElement(menuIconInRow, TIMEOUT_SECONDS_15);
            CommonMethod.clickElement(pagesContext.getUsersPage().deleteButton, TIMEOUT_SECONDS_15);
        } else {
            CommonMethod.clickElement(userRow.locator(pagesContext.getUsersPage().deleteButton), TIMEOUT_SECONDS_15);
        }

        assertThat(pagesContext.getUsersPage().deleteUserDialog).isVisible();
        CommonMethod.clickElement(pagesContext.getUsersPage().dialogConfirmButton, TIMEOUT_SECONDS_15);

        return helperContext.getCommonHelper().waitForAndGetToastText(TIMEOUT_SECONDS_15);
    }

    public void searchAndDeleteUserIfExists(String email) {
        try {
            helperContext.getCommonHelper().goToUsersPage();
            helperContext.getCommonHelper().clearSearchBoxAndInputRandom();
            helperContext.getCommonHelper().waitForTableData(TIMEOUT_SECONDS_15);
            helperContext.getCommonHelper().performSearch(email);
            helperContext.getCommonHelper().waitForTableData(TIMEOUT_SECONDS_15);

            Locator userRow = pagesContext.getUsersPage().getUserRowByEmail(email);
            if (CommonMethod.isVisible(userRow,TIMEOUT_SECONDS_15)) {
                System.out.println("Cleanup: User '" + email + "' found. Attempting to delete.");

                Locator deleteButtonInRow = userRow.locator(pagesContext.getUsersPage().deleteButton);
                if (CommonMethod.isVisible(deleteButtonInRow,2000)) {
                    CommonMethod.clickElement(deleteButtonInRow, TIMEOUT_SECONDS_15);
                } else {
                    Locator menuIconInRow = userRow.locator(pagesContext.getUsersPage().actionsMenuIcon);
//                    assertThat(menuIconInRow).isVisible();
                    CommonMethod.clickElement(menuIconInRow, TIMEOUT_SECONDS_15);
                    CommonMethod.clickElement(pagesContext.getUsersPage().deleteButton, TIMEOUT_SECONDS_15);
                }

                assertThat(pagesContext.getUsersPage().deleteUserDialog).isVisible();
                CommonMethod.clickElement(pagesContext.getUsersPage().dialogConfirmButton, TIMEOUT_SECONDS_15);

                String toastMessage = helperContext.getCommonHelper().waitForAndGetToastText(TIMEOUT_SECONDS_15);
                System.out.println("Cleanup: Deletion successful. Toast: '" + toastMessage + "'");
                helperContext.getCommonHelper().waitForToastToDisappear(toastMessage);
                assertThat(userRow).isHidden();
            } else {
                System.out.println("Cleanup: User '" + email + "' not found. No action needed.");
            }

        } catch (Exception e) {
            System.err.println("Cleanup Warning: An error occurred during deletion of user '" + email + "'. Error: " + e.getMessage());
        } finally {
            helperContext.getCommonHelper().clearSearchBox();
        }
    }

    public String cancelInvitationForUser(String email) throws InterruptedException {
        helperContext.getCommonHelper().performSearch(email);
        Locator userRow = pagesContext.getUsersPage().getUserRowByEmail(email);
        assertThat(userRow).isVisible();

        Locator menuIconInRow = userRow.locator(pagesContext.getUsersPage().actionsMenuIcon);
        CommonMethod.clickElement(menuIconInRow, TIMEOUT_SECONDS_15);

        CommonMethod.clickElement(pagesContext.getUsersPage().cancelInviteButton, TIMEOUT_SECONDS_15);

        assertThat(pagesContext.getUsersPage().cancelInviteDialog).isVisible();
        CommonMethod.clickElement(pagesContext.getUsersPage().dialogConfirmButton, TIMEOUT_SECONDS_15);

        return helperContext.getCommonHelper().waitForAndGetToastText(TIMEOUT_SECONDS_15);
    }


    public void registerNewUser(String email, String firstName, String lastName, String password) throws InterruptedException {
        helperContext.getLoginHelper().clickSSOButtion();
        helperContext.getLoginHelper().clickRegisterNow();
        String otpCode = helperContext.getLoginHelper().enterRegisterEmailAndGetotpCode(email);
        helperContext.getLoginHelper().enterRegisterOtpCodeAndNext(otpCode);
        helperContext.getLoginHelper().fillRegistrationDetails(firstName, lastName, password);
        helperContext.getLoginHelper().submitAndVerifyRegistration();

    }

}
