// File: src/main/java/com/zebra/pageobject/user/UserPage.java
package com.zebra.pageobject.User;

import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.options.AriaRole;
import com.zebra.pageobject.CommonPage;

/**
 * This class represents the Users page.
 * It provides robust and unique locators for page elements.
 */
public class UsersPage extends CommonPage {

    // Left-hand navigation menu item
    public final Locator usersMenu;

    // Page header elements
    public final Locator pageTitle;
    public final Locator pageDescription;

    // Main action buttons on the page
    public final Locator addUserButton;

    // Add User dialog root
    public final Locator addUserDialog;

    // Email input (custom component) and its inner native input
    public final Locator emailInputComponent;
    public final Locator emailNativeInput;

    // Dialog action buttons
    public final Locator deleteUserDialog;
    public final Locator cancelInviteDialog;

    public final Locator cancelInviteButton;
    public final Locator inviteButton;

    public final Locator invalidEmailError;

    // Table control elements
    public final Locator searchBar;                 // zeta-search custom component
    public final Locator refreshButton;             // zeta-button with refresh icon
    public final Locator toggleColumnsButton;       // zeta-icon-button for toggling columns

    // Toggle Column dialog
    public final Locator toggleColumnsDialog;
    public final Locator toggleColumnsCancelButton;
    public final Locator toggleColumnsConfirmButton;

    // Table rows
    public final Locator tableRows;

    /**
     * Constructor for the UserPage.
     * @param page Playwright Page instance.
     */
    public UsersPage(Page page) {
        super(page);

        // Side navigation menu locator - use stable title attribute
        this.usersMenu = page.locator("a[title='Users']");

        // Header locators
        this.pageTitle = page.locator("h1:has-text('Users')");
        this.pageDescription = page.locator("aside:has-text('Here you can view and manage all your users')");

        // Main action button locator using ARIA role for robustness
        this.addUserButton = page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Add User"));

        // --- Add User Dialog Initialization ---

        // Dialog identified by stable visible text "Add User"
        this.addUserDialog = page.locator("dialog:has-text('Add User')");

        // Custom component input; interact through inner native input
        this.emailInputComponent = addUserDialog.locator("zeta-text-input[aria-label='email'][name='email']");
        this.emailNativeInput = this.emailInputComponent.locator("input");

        // Stable by slot or text
        this.cancelInviteButton = page.locator("zeta-button:has-text('Cancel Invite')");
        this.inviteButton = addUserDialog.locator("zeta-button[slot='confirm'], zeta-button:has-text('Invite')");
        this.deleteUserDialog = page.getByRole(AriaRole.DIALOG)
                .filter(new Locator.FilterOptions().setHasText("Delete User"));
        this.cancelInviteDialog = page.locator("dialog:has-text('Cancel the invite for User')");

        this.invalidEmailError = page.getByText("Invalid Email Address");


        // Table control locators
        this.searchBar = page.locator("zeta-search");
        this.refreshButton = page.locator("zeta-button:has(zeta-icon:has-text('refresh'))");
        this.toggleColumnsButton = page.locator("zeta-icon-button:has-text('columns')");

        // Toggle Column dialog locators (opened by clicking the columns icon button)
        this.toggleColumnsDialog = page.getByRole(AriaRole.DIALOG, new Page.GetByRoleOptions().setName("Toggle Column Visibility"));
        this.toggleColumnsCancelButton = this.toggleColumnsDialog.getByRole(AriaRole.BUTTON, new Locator.GetByRoleOptions().setName("Cancel"));
        this.toggleColumnsConfirmButton = this.toggleColumnsDialog.getByRole(AriaRole.BUTTON, new Locator.GetByRoleOptions().setName("Confirm"));

        // Table rows - use the stable data-index attribute
        this.tableRows = page.locator("tbody tr[data-index]");
    }

    public Locator getUserRowByEmail(String email) {
        return page.getByRole(AriaRole.ROW)
                .filter(new Locator.FilterOptions().setHasText(email));
    }
}

