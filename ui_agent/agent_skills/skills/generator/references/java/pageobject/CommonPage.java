package com.zebra.pageobject;

import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.options.AriaRole;

public class CommonPage {
    protected final Page page;

    public final Locator harmonixLogo;
    public final Locator tenantDropdown;
    public final Locator userProfileButton;
    public final Locator logoutButton;
    public final Locator userMenuPopup;
    public final Locator tenantListItems;

    public final Locator homeIcon;
    //    public final Locator deviceInventoryMenu;
    public final Locator phoneIcon;
    public final Locator printerIcon;
    public final Locator scannerIcon;
    public final Locator searchComponent;
    public final Locator searchBox;
    public final Locator clearSearchButton;
    public final Locator refreshButton;
    public final Locator columnVisibilityButton;
    public final Locator tableRows;
    public final Locator tableLoadingShimmer;
    public final Locator allTableRows;
    public final Locator dataRows;

    public final Locator actionsMenuIcon;
    public final Locator deleteButton;
    public final Locator deleteDeviceDialog;
    public final Locator deleteDeviceConfirmationText;
    public final Locator deleteProfileDialog;
    public final Locator deleteProfileConfirmationText;
    public final Locator dialogConfirmButton;
    public final Locator dialogCancelButton;
    public final Locator successDeleteProfileNotification;
    public final Locator successDeleteDeviceNotification;

    // No results elements
    public final Locator noResultsMessage;

    public final Locator versionVersion;

    // printer
    public final Locator newPrinterSetup;
    public final Locator myPrinters;
    public final Locator printerSettings;

    public final Locator toastMessage;
    public final Locator scrollableTableContainer;
    public final Locator filterIcon;
    public final Locator applyButton;
    public final Locator filterCheckBox;
    public final Locator selectedFilterCheckBox;
    public final Locator resetButton;
    public final Locator header;
    public final Locator rows;
    public final Locator selectFilesButton;
    public final Locator tableHeader;
    public final Locator clearSearchResultButton;

    public CommonPage(Page page) {
        this.page = page;
        this.harmonixLogo = page.locator("//div[@id='platform-name']");//page.locator("img[src='/assets/zebra-logo.svg']");
        ; // Component may contain logo, adjust based on actual rendering
        this.tenantDropdown = page.locator("//zeta-icon[@id='user-info-icon']");//page.locator("button.interactive-target:has(zeta-icon:has-text('expand_more'))");
        this.userProfileButton = page.locator("zeta-avatar[slot='user-avatar']");
        this.logoutButton = page.locator("zeta-button[aria-label='Log Out']");
        this.userMenuPopup = page.locator("div[class*='_dropdown_']:has-text('Tenants:')");
        this.tenantListItems = this.userMenuPopup.locator("> div[class*='_list-item_']");
        // Left navigation significant adjustments (using title attributes and correct hierarchy)
        this.homeIcon = page.locator("a:has(zeta-icon:has-text('home'))");
//        this.deviceInventoryMenu = page.locator("a[href='/mobile-computers']");
        this.phoneIcon = page.locator("a[title='Computers']");
        this.printerIcon = page.locator("a[title='Printers']");
        this.scannerIcon = page.locator("a:has(img[alt='Scanners'])");

        this.newPrinterSetup = page.getByText("New Printer Setup");
        this.myPrinters = page.getByText("My Printers");
        this.printerSettings = page.getByText("Printer Settings");

        this.searchBox = page.locator("input[type='search']");
        this.searchComponent = page.locator("zeta-search");
        this.clearSearchButton = this.searchComponent.locator("zeta-icon:has-text('cancel')");
        this.refreshButton = page.locator("zeta-button:has(zeta-icon:has-text('refresh'))").first();
        this.columnVisibilityButton = page.locator("zeta-icon-button:has-text('columns')");
        this.tableRows = page.locator("table tbody tr[data-index]");
        this.tableHeader = page.locator("table thead tr");
//        this.tableLoadingShimmer = this.scrollableTableContainer.locator("div[class^='_shimmer_']");
        this.allTableRows = page.locator("tbody > tr");
        this.dataRows = page.locator("table tbody tr[data-index]:not(:has(div[class^='_shimmer_']))");

        // Delete dialog
        this.actionsMenuIcon = page.locator("zeta-icon-button:has-text('more_vertical')");
        this.deleteButton = page.locator("zeta-button").filter(new Locator.FilterOptions().setHasText("Delete"));
        this.deleteDeviceDialog = page.locator("dialog:has-text('Delete Device')");
        this.deleteDeviceConfirmationText = page.getByText("Are you sure you want to delete this device(s)?");
        this.deleteProfileDialog = page.locator("dialog:has-text('Delete Profile')");
        this.deleteProfileConfirmationText = page.getByText("Are you sure you want to delete this profile(s)?");

        // dialog confirmation dialog
        this.dialogConfirmButton = page.locator("dialog[open] zeta-button:has-text('Confirm')"); // "Confirm" button
        this.dialogCancelButton = page.locator("dialog[open] zeta-button:has-text('Cancel')"); // "Cancel" button
        // Success notification with delete
        this.successDeleteProfileNotification = page.getByText("Successfully deleted profile(s).");
        this.successDeleteDeviceNotification = page.getByText("Successfully deleted device(s).");

        this.versionVersion = page.locator(".version");

        // No results section
        this.noResultsMessage = page.locator("text=/No results matched/i");
        this.toastMessage = page.locator("div[class^='_toast_'] span");
        this.scrollableTableContainer = page.locator("div[style*='overflow: auto']:has(table)").first();
        this.tableLoadingShimmer = this.scrollableTableContainer.locator("div[class^='_shimmer_']");
        // filter
        this.filterIcon = page.locator("zeta-icon:text-is('filter')");//page.getByRole(AriaRole.COLUMNHEADER, new Page.GetByRoleOptions().setName("Model filter")).locator("zeta-icon");
        this.applyButton = page.locator("zeta-button:has-text('Apply'):visible");
        this.filterCheckBox = page.locator("zeta-checkbox[aria-checked='false']");
        this.selectedFilterCheckBox = page.locator("zeta-checkbox[name]:not([name=''])[aria-checked='true']");
        this.selectFilesButton = page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Select Files"));
        this.resetButton = page.locator("zeta-button:has-text('Reset'):visible");
        this.rows = page.locator("tbody tr");
        this.header = page.locator("thead th");
        this.clearSearchResultButton = page.locator("zeta-button:has-text('Clear search')");
    }

    public Locator getToastElement(String text) {
        return page.getByText(text);
    }

    public Locator getColumnHeaderByName(String columnName) {
        return page.locator(String.format("th:has-text('%s')", columnName));
    }

    public Locator getSortControlForColumn(String columnName) {
        return getColumnHeaderByName(columnName).locator("harmonix-sort");
    }

    public Locator getSortUpArrowIndicator(String columnName) {
        return getSortControlForColumn(columnName).locator("path >> nth=0");
    }

    public Locator getSortDownArrowIndicator(String columnName) {
        return getSortControlForColumn(columnName).locator("path >> nth=1");
    }

    public Locator getFilterIconForColumn(String columnName) {
        String selector = String.format("th:has-text('%s') zeta-icon:has-text('filter')", columnName);
        return page.locator(selector);
    }

    public Locator getFilterCheckboxByName(String checkboxName) {
        String selector = String.format("zeta-checkbox[name=\"%s\"]", checkboxName);
        return page.locator(selector);
    }

    public Locator getSelectedCheckBox(String filterName){
        return page.locator("zeta-checkbox:text-is('"+filterName+"')").locator("input[type='checkbox']");
    }

    public Locator getFilterCheckBox(int filterIndex) {
        return this.filterCheckBox.nth(filterIndex);
    }

    public Locator getSelectedFilterCheckBox(int filterIndex) {
        return this.selectedFilterCheckBox.nth(filterIndex);
    }

    public Locator getFilterCheckBox(String filterName) {
        return page.locator("zeta-checkbox:text-is('"+filterName+"')");
    }

    public Locator getFilterIcon(String filter){
        return page.getByRole(AriaRole.COLUMNHEADER, new Page.GetByRoleOptions().setName(filter+" filter")).locator("zeta-icon");
    }

    public Locator tenantSwitchItem(String tenantName) {
        return page.getByText(tenantName);
    }

    public Locator activeTenantItem(String tenantName) {
        return page.locator("div[class*='active']").filter(new Locator.FilterOptions().setHasText(tenantName));
    }

    public void refreshPage() {
        page.reload();
    }
}
