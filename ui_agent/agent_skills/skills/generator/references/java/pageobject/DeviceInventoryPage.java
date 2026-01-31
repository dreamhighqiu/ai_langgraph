package com.zebra.pageobject;

import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;

public class DeviceInventoryPage extends CommonPage {
    public final Locator pageTitle;

    public DeviceInventoryPage(Page page) {
        super(page);

        this.pageTitle = page.locator("h1:has-text('Device Inventory')");
    }

}
