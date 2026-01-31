package com.zebra.TestCase.smokeTest;
import com.zebra.common.CommonMethod;
import com.epam.reportportal.junit5.ReportPortalExtension;
import com.zebra.common.MailTemp;
import com.zebra.common.MailboxTemp;
import com.zebra.property.HarmonixProperty;
import com.zebra.property.UserAccountProperty;
import com.zebra.helper.Hook;
import lombok.extern.slf4j.Slf4j;
import org.junit.jupiter.api.Assumptions;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

import java.util.Arrays;
import java.util.List;

import static com.zebra.property.HarmonixProperty.TEMP_MAIL_DOMAIN;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import org.junit.jupiter.api.extension.ExtendWith;

@ExtendWith(ReportPortalExtension.class)
@Slf4j
public class UsersPageTest extends Hook {
    @BeforeAll
    static void skipIfSkipModule() {
        Assumptions.assumeFalse(
                HarmonixProperty.skipModule.contains("UsersPage".toLowerCase()),
                "Tests are skipped environment"
        );
    }

    private static final String TENANT_CATDOG_NAME = "The Catdog";
    private static final String TENANT_EVT2_NAME = "Harmonix evt2";
    private static final String PRE_EXISTING_USER_EMAIL = "swevtcdc001@virgilian.com";
    private static final String PRE_ADMIN_USER_EMAIL = "swevtcdc001@virgilian.com";

    @Test
    @Tag("smoke")
    void testAddExternalUserSuccessfully() {
        String newExternalUserEmail;
        if (TEMP_MAIL_DOMAIN.equalsIgnoreCase("virgilian.com")) {
            newExternalUserEmail = new MailTemp().getEmail();
        }else{
            newExternalUserEmail = new MailboxTemp().getEmail();
        }

        try {
            usersHelper.addNewUserSuccessfully(newExternalUserEmail);
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        } finally {
            usersHelper.searchAndDeleteUserIfExists(newExternalUserEmail);
        }
    }

    @Test
    @Tag("smoke")
    void testAddInvitedExternalUserSuccessfully() {
        String newExternalUserEmail;
        if (TEMP_MAIL_DOMAIN.equalsIgnoreCase("virgilian.com")) {
            newExternalUserEmail = new MailboxTemp().getEmail();
        }else{
            newExternalUserEmail = new MailboxTemp().getEmail();
        }

        try {
            String expectedToastMessage = "User invited successfully!";
            String expectedStatusInList = "Invited";

            usersHelper.addNewUserSuccessfully(newExternalUserEmail);
            String actualToastMessage = usersHelper.inviteUserAndGetToastMessage(newExternalUserEmail);

            assertEquals(expectedToastMessage, actualToastMessage, "The failure toast message for inviting an active internal user was not correct.");
            usersHelper.verifyUserInListWithStatus(newExternalUserEmail, expectedStatusInList);
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        } finally {
            usersHelper.searchAndDeleteUserIfExists(newExternalUserEmail);
        }
    }

    @Test
    void testAddActiveExternalUserFailed() {
        UserAccountProperty userAccounts = new UserAccountProperty();
        String newExternalUserEmail = userAccounts.threadAccount_1;
        String expectedToastMessage = String.format("Invite user request failed: User: %s already active", newExternalUserEmail);
        commonHelper.goToUsersPage();
        usersHelper.inviteUserAndGetToastMessage(newExternalUserEmail);
        String actualToastMessage = usersHelper.inviteUserAndGetToastMessage(newExternalUserEmail);
        assertEquals(expectedToastMessage, actualToastMessage, "The failure toast message for inviting an active internal user was not correct.");
    }

    @ParameterizedTest(name = "Run #{index}: Invalid email input is [{0}]")
    @ValueSource(strings = {
            "this-is-not-an-email",
            "justletters",
            "1234567890",
            "test@@example.com",
            "test@",
            "@example.com",
            "test @example.com",
            " "
    })
    @Tag("smoke")
    void testInvalidEmailFormat(String invalidEmail) throws InterruptedException {
        String expectedErrorMessage = "Invalid Email Address";

        commonHelper.goToUsersPage();
        String actualErrorMessage = usersHelper.getInvalidEmailErrorMessage(invalidEmail);

        assertEquals(expectedErrorMessage, actualErrorMessage,
                "The validation error for the invalid email '" + invalidEmail + "' was not correct.");
    }

    @Test
    @Tag("smoke")
    void testCancelInvitedUser() {
        String userEmail;
        if (TEMP_MAIL_DOMAIN.equalsIgnoreCase("virgilian.com")) {
            userEmail = new MailTemp().getEmail();
        }else{
            userEmail = new MailboxTemp().getEmail();
        }

        String expectedToastMessage = "User cancelled successfully!";

        try {
            usersHelper.addNewUserSuccessfully(userEmail);

            String actualToastMessage = usersHelper.cancelInvitationForUser(userEmail);

            assertEquals(expectedToastMessage, actualToastMessage, "The toast message for cancelling an invite was incorrect.");
            usersHelper.verifyUserInListWithStatus(userEmail, "Cancelled");
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        } finally {
            usersHelper.searchAndDeleteUserIfExists(userEmail);
        }
    }

    @Test
    @Tag("smoke")
    void testSearchWithMultiFields() {
        String uniqueFingerprint = "autotest-" + System.currentTimeMillis();
        String user1Email;
        String user2Email;
        if (TEMP_MAIL_DOMAIN.equalsIgnoreCase("virgilian.com")) {
            user1Email = "swevtcdc_" + uniqueFingerprint + "_userA@virgilian.com";
            user2Email = "swevtcdc_" + uniqueFingerprint + "_userB@virgilian.com";
        }else{
            user1Email = "swevtcdc_" + uniqueFingerprint + "_userA@nqmo.com";
            user2Email = "swevtcdc_" + uniqueFingerprint + "_userB@nqmo.com";
        }

        try {
            List<String> expectedEmailsInResult = Arrays.asList(user1Email, user2Email);
            usersHelper.addNewUserSuccessfully(user1Email);
            usersHelper.addNewUserSuccessfully(user2Email);
            usersHelper.searchAndVerifyPartialMatches(uniqueFingerprint, expectedEmailsInResult);
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        } finally {
            usersHelper.searchAndDeleteUserIfExists(user1Email);
            usersHelper.searchAndDeleteUserIfExists(user2Email);
        }
    }

    @Test
    @Tag("smoke")
    void testSearchWithoutMatchingResult() throws InterruptedException {
        String nonExistentSearchTerm = CommonMethod.generateRandomString(8);
        commonHelper.goToUsersPage();
        commonHelper.searchAndVerifyNoResults(nonExistentSearchTerm);
    }

    @Test
    @Tag("smoke")
    void testDeleteUserSuccessfully() throws InterruptedException {
        String emailToDelete;
        if (TEMP_MAIL_DOMAIN.equalsIgnoreCase("virgilian.com")) {
            emailToDelete = "swevtcdc_delete_me_" + System.currentTimeMillis() + "@virgilian.com";
        }else {
            emailToDelete = "swevtcdc_delete_me_" + System.currentTimeMillis() + "@nqmo.com";
        }

        String expectedDeletionMessage = "User deleted successfully!";
        usersHelper.addNewUserSuccessfully(emailToDelete);
        String deletionToast = usersHelper.deleteUser(emailToDelete);
        assertEquals(expectedDeletionMessage, deletionToast, "The success message for deletion was incorrect.");
        commonHelper.searchAndVerifyNoResults(emailToDelete);
    }

    @Test
    @Tag("smoke")
    @Tag("SkipLogin")
    void testDeleteUserInMultipleTenants() throws InterruptedException {
        // --- PRE-TEST CLEANUP ---
        System.out.println("--- PRE-TEST CLEANUP PHASE ---");
        loginToWebPortal(PRE_ADMIN_USER_EMAIL);
        commonHelper.goToUsersPage();
        commonHelper.switchTenant(TENANT_CATDOG_NAME);
        usersHelper.searchAndDeleteUserIfExists(PRE_EXISTING_USER_EMAIL);
        commonHelper.switchTenant(TENANT_EVT2_NAME);
        usersHelper.searchAndDeleteUserIfExists(PRE_EXISTING_USER_EMAIL);

        // invite user to both tenants
        commonHelper.goToUsersPage();
        usersHelper.addNewUserSuccessfully(PRE_EXISTING_USER_EMAIL);
        usersHelper.verifyUserInListWithStatus(PRE_EXISTING_USER_EMAIL, "Invited");
        commonHelper.switchTenant(TENANT_CATDOG_NAME);
        commonHelper.goToUsersPage();
        usersHelper.addNewUserSuccessfully(PRE_EXISTING_USER_EMAIL);
        usersHelper.verifyUserInListWithStatus(PRE_EXISTING_USER_EMAIL, "Invited");
        System.out.println("Action: Switching to User account for verification...");

        // verify user sees both tenants
        helperContext.getLoginHelper().logoutWebportal();
        loginToWebPortal(PRE_EXISTING_USER_EMAIL);
        commonHelper.verifyUserTenantSize(2);
        assertTrue(commonHelper.isUserInTenant(TENANT_CATDOG_NAME), "user should have access to tenant: " + TENANT_CATDOG_NAME);
        assertTrue(commonHelper.isUserInTenant(TENANT_EVT2_NAME), "user should have access to tenant: " + TENANT_EVT2_NAME);
        System.out.println("SUCCESS: User sees both tenants.");

        // delete user from Tenant 1 and verify still exists in Tenant 2
        commonHelper.goToUsersPage();
        commonHelper.switchTenant(TENANT_CATDOG_NAME);
        usersHelper.deleteUser(PRE_EXISTING_USER_EMAIL);
        commonHelper.searchAndVerifyNoResults(PRE_EXISTING_USER_EMAIL);
        helperContext.getLoginHelper().logoutWebportal();
        loginToWebPortal(PRE_EXISTING_USER_EMAIL);
        commonHelper.goToUsersPage();
        commonHelper.verifyUserTenantSize(1);
        assertTrue(commonHelper.isUserInTenant(TENANT_EVT2_NAME), "user should have access to tenant: " + TENANT_EVT2_NAME);
    }


    @Test
    @Tag("smoke")
    void filterAccountStatusWithSingleOption() {
        commonHelper.goToUsersPage();
        commonHelper.filterWithSingleOptionAndCheckFilterResult("Account Status");
    }

    @Test
    @Tag("smoke")
    void filterAccountStatuWithMultipleOptions() {
        commonHelper.goToUsersPage();
        commonHelper.filterWithMultipleOptionsAndCheckFilterResult("Account Status");
    }

    @Test
    @Tag("smoke")
    void resetAccountStatuFilter() {
        commonHelper.goToUsersPage();
        commonHelper.resetFilterAndCheckResult("Account Status");
    }

    @Test
    @Tag("smoke")
    @Tag("SkipLogin")
    void registerNewUser() throws InterruptedException {
        String uniqueEmail;
        if (TEMP_MAIL_DOMAIN.equalsIgnoreCase("virgilian.com")) {
            uniqueEmail = "swevtcdc_" + System.currentTimeMillis() + "@virgilian.com";
            MailTemp mailboxTemp = new MailTemp(uniqueEmail);
        }else {
            uniqueEmail = "swevtcdc_" + System.currentTimeMillis() + "@nqmo.com";
        }
        String firstName = "John";
        String lastName = "Doe";
        String password = "BeMore!23456";
        helperContext.getUsersHelper().registerNewUser(uniqueEmail, firstName, lastName, password);
        helperContext.getLoginHelper().loginWebportal(uniqueEmail, password);
    }


}
