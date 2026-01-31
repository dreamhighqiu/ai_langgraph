package com.zebra.helper;

import com.microsoft.playwright.*;
import com.microsoft.playwright.options.HttpCredentials;
import com.microsoft.playwright.options.LoadState;
import com.zebra.bidiemulator.EmulatorRunner;
import com.zebra.common.*;
import com.zebra.context.*;
import com.zebra.pageobject.*;
import com.zebra.pageobject.Printer.MyPrinters.MyPrintersPage;
import com.zebra.pageobject.Printer.PrinterSettingsProfile.ApplyPrinterSettingsPage;
import com.zebra.pageobject.Printer.PrinterSettingsProfile.CreatePrinterSettingPage;
import com.zebra.pageobject.Printer.PrinterSettingsProfile.PrinterSettingsPage;
import com.zebra.pageobject.Printer.PrinterSetupProfile.CreatePrinterSetupPage;
import com.zebra.pageobject.Printer.PrinterSetupProfile.NewPrinterSetupPage;
import com.zebra.pageobject.User.UsersPage;
import com.zebra.property.HarmonixProperty;
import com.zebra.property.UserAccountProperty;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.TestInfo;
import org.junit.jupiter.api.extension.ExtendWith;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.Predicate;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;

import static com.zebra.common.TimeoutUtility.*;
import static com.zebra.property.HarmonixProperty.*;

@ExtendWith(SuiteExtension.class)
@ExtendWith(com.zebra.common.AllureFailureScreenshotExtension.class)
public class Hook {
    // Shared Playwright, Browser and Context across all tests in the same session
    private static Playwright sharedPlaywright;
    private static Browser sharedBrowser;
    private static BrowserContext sharedContext;
    private static final Object contextLock = new Object();

    // Instance variables
    public Playwright playwright;
    public Page page;
    public BrowserContext context;

    // Static variables
    public static String timestamp;

    // Track which accounts have been logged in during this test session
    private static final Set<String> loggedInAccounts = ConcurrentHashMap.newKeySet();

    // Test context related
    public String testcaseName;
    public byte[] screenshot;
    public PlaywrightContext playwrightContext;
    public PrintersEmulator printersEmulator;
    public PagesContext pagesContext;
    public HelperContext helperContext;
    public UserAccountProperty userAccountProperty;
    public CreateDataContext createDataContext;

    // Utilities
    public DeviceInventoryHelper deviceInventoryHelper;
    public CommonHelper commonHelper;
    public CreatePrinterSetUpProfileHelper createPrinterSetUpProfileHelper;
    public NewPrinterSetupHelper newPrinterSetupHelper;
    public PrinterSettingsHelper printerSettingsHelper;
    public CreatePrinterSettingProfileHelper createPrinterSettingProfileHelper;
    public ApplyPrinterSettingsProfileHelper applyPrinterSettingsProfileHelper;
    public LoginHelper loginHelper;
    public MyPrinterHelper myPrinterHelper;
    public EmulatorHelper emulatorHelper;
    public RealPrinterHelper realPrinterHelper;
    public UsersHelper usersHelper;

    // Account used by the current thread
    private String currentTestAccount;

    @BeforeEach
    public void testSetup(TestInfo testInfo) throws InterruptedException {
        // 1. Get account from the account pool
        long timeout = 300000; // 5min
        long start = System.currentTimeMillis();

        while (currentTestAccount == null && (System.currentTimeMillis() - start) < timeout) {
            currentTestAccount = SuiteExtension.accountPool.poll();
            if (currentTestAccount == null) {
                // If the pool is empty, wait 1 second and try again
                Thread.sleep(1000);
                System.out.println("Thread " + Thread.currentThread().getId() + " is waiting for an available account...");
            }
        }
        if (currentTestAccount == null) {
            throw new RuntimeException("Timeout! No available account in the pool after waiting.");
        }
        System.out.println("Thread " + Thread.currentThread().getId() + " acquired account: " + currentTestAccount);

        // 2. Initialize context and utilities
        playwrightContext = new PlaywrightContext();
        pagesContext = new PagesContext();
        helperContext = new HelperContext();
        userAccountProperty = new UserAccountProperty();
        createDataContext = new CreateDataContext();

        // 3. Start browser with independent context (each test gets its own context)
        startBrowserWithSessionState();

        // 4. Initialize pages and page utilities
        initAllPagesAndUtils();

        // 5. Navigate to URL and check if login is needed
        boolean shouldSkipLogin = testInfo.getTags().contains("SkipLogin");
        if (shouldSkipLogin) {
            page.navigate(URL);
        } else {
            // Check if this account has already been logged in during this session
            boolean accountAlreadyLoggedIn = loggedInAccounts.contains(currentTestAccount);
            
            if (accountAlreadyLoggedIn) {
                System.out.println("=== Account " + currentTestAccount + " already logged in this session ===");
                System.out.println("Note: Using saved session state file for fast login");
            } else {
                System.out.println("=== First time using account " + currentTestAccount + " in this session ===");
            }

            // Always attempt to login (will use session state if available)
            loginToWebPortal(currentTestAccount);

            // Mark as logged in after successful login
            if (!accountAlreadyLoggedIn) {
                loggedInAccounts.add(currentTestAccount);
            }
        }
    }

    private void startBrowserWithSessionState() {
        playwright = Playwright.create();
        playwrightContext.setPlaywright(playwright);

        BrowserType.LaunchOptions launchOptions = new BrowserType.LaunchOptions()
                .setHeadless(HarmonixProperty.runHeadless)
                .setArgs(Arrays.asList(
                        "--no-sandbox",
                        "--disable-dev-shm-usage",
                        "--disable-blink-features=AutomationControlled",
                        "--disable-infobars",
                        "--disable-extensions",
                        "--start-maximized"
                ))
                .setTimeout(60_000);

        Browser browser = playwright.chromium().launch(launchOptions);

        Browser.NewContextOptions contextOptions = new Browser.NewContextOptions()
                .setViewportSize(null)
                .setAcceptDownloads(true)
                .setIgnoreHTTPSErrors(true);
        contextOptions.setHttpCredentials(new HttpCredentials(currentTestAccount, userAccountProperty.accountPassword));

        // Try to load saved auth state to skip login
        String environment = HarmonixProperty.env != null ? HarmonixProperty.env : "stage";
        Path savedAuthState = AuthStateManager.loadAuthState(currentTestAccount, environment);
        if (savedAuthState != null) {
            contextOptions.setStorageStatePath(savedAuthState);
            System.out.println("Loading saved session state from: " + savedAuthState);
        } else {
            System.out.println("No saved session state found, will perform full login");
        }

        BrowserContext ctx = browser.newContext(contextOptions);
        ctx.setDefaultNavigationTimeout(60_000);
        this.context = ctx;
        playwrightContext.setContext(ctx);
        this.page = ctx.newPage();
        PlaywrightThreadLocal.setPage(this.page);
        playwrightContext.setPage(page);

        ctx.tracing().start(new Tracing.StartOptions()
                .setScreenshots(true)
                .setSnapshots(true)
                .setSources(true));
    }

    /**
     * Initialize all page objects and utility classes
     */
    private void initAllPagesAndUtils() {
        // Page Objects
        pagesContext.setDeviceInventoryPage(new DeviceInventoryPage(page));
        pagesContext.setCommonPage(new CommonPage(page));
        pagesContext.setCreatePrinterSetupPage(new CreatePrinterSetupPage(page));
        pagesContext.setMyPrintersPage(new MyPrintersPage(page));
        pagesContext.setNewPrinterSetupPage(new NewPrinterSetupPage(page));
        pagesContext.setPrinterSettingsPage(new PrinterSettingsPage(page));
        pagesContext.setCreatePrinterSettingPage(new CreatePrinterSettingPage(page));
        pagesContext.setApplyPrinterSettingsPage(new ApplyPrinterSettingsPage(page));
        pagesContext.setLoginPage(new LoginPage(page));
        pagesContext.setUsersPage(new UsersPage(page));

        // Utilities
        commonHelper = new CommonHelper(printersEmulator, playwrightContext, pagesContext,createDataContext);
        loginHelper = new LoginHelper(pagesContext);
        deviceInventoryHelper = new DeviceInventoryHelper( pagesContext);
        createPrinterSetUpProfileHelper = new CreatePrinterSetUpProfileHelper(printersEmulator, playwrightContext, pagesContext, helperContext,createDataContext,userAccountProperty);
        newPrinterSetupHelper = new NewPrinterSetupHelper(emulatorHelper, playwrightContext, pagesContext,createDataContext,commonHelper);
        printerSettingsHelper = new PrinterSettingsHelper(printersEmulator, playwrightContext, pagesContext,createDataContext,commonHelper);
        createPrinterSettingProfileHelper = new CreatePrinterSettingProfileHelper(printersEmulator, playwrightContext, pagesContext,createDataContext, helperContext,userAccountProperty);
        realPrinterHelper = new RealPrinterHelper(primaryIp, secondaryIp, thirdIp, commonHelper);
        applyPrinterSettingsProfileHelper = new ApplyPrinterSettingsProfileHelper(printersEmulator, playwrightContext, pagesContext,createDataContext,commonHelper,realPrinterHelper,emulatorHelper);
        myPrinterHelper = new MyPrinterHelper(emulatorHelper, playwrightContext, pagesContext,createDataContext,helperContext);
        emulatorHelper = new EmulatorHelper(EmulatorRunner.BASE_URL,createDataContext,userAccountProperty,commonHelper);
        usersHelper = new UsersHelper( pagesContext, helperContext);

        // Utility Context
        helperContext.setCommonHelper(commonHelper);
        helperContext.setLoginHelper(loginHelper);
        helperContext.setDeviceInventoryHelper(deviceInventoryHelper);
        helperContext.setCreatePrinterSetUpProfileHelper(createPrinterSetUpProfileHelper);
        helperContext.setNewPrinterSetupHelper(newPrinterSetupHelper);
        helperContext.setPrinterSettingsHelper(printerSettingsHelper);
        helperContext.setCreatePrinterSettingProfileHelper(createPrinterSettingProfileHelper);
        helperContext.setApplyPrinterSettingsProfileHelper(applyPrinterSettingsProfileHelper);
        helperContext.setMyPrinterHelper(myPrinterHelper);
        helperContext.setUsersHelper(usersHelper);

    }

    protected void loginToWebPortal(String username) throws InterruptedException {
        System.out.println("=== Login Process Start ===");
        System.out.println("Username: " + username);
        System.out.println("Environment: " + HarmonixProperty.env);
        
        // Navigate to the URL first
        System.out.println("Step 1: Navigating to URL: " + URL);
        page.navigate(URL);
        page.waitForLoadState(LoadState.DOMCONTENTLOADED,
                new Page.WaitForLoadStateOptions().setTimeout(TIMEOUT_SECONDS_MIDDLE * 3));
        System.out.println("Step 1: Navigation completed");

        // Check if already logged in by verifying if we're on the device inventory page
        System.out.println("Step 2: Checking if already logged in...");
        try {
            // Wait longer for page title to appear (might be slow after loading session state)
            if (pagesContext.getDeviceInventoryPage() != null &&
                CommonMethod.isVisible(pagesContext.getDeviceInventoryPage().pageTitle, 15)) {  // Increased from 5 to 15 seconds
                System.out.println("Already logged in with saved auth state for: " + username);
                helperContext.getDeviceInventoryHelper().verifyAllKeyElementsOnDeviceInventoryPresence();

                // Still need to capture headers for API calls
                try {
                    System.out.println("Step 2a: Capturing headers from existing session...");
                    Page.WaitForResponseOptions options = new Page.WaitForResponseOptions().setTimeout(TIMEOUT_SECONDS_LONG);
                    Predicate<Response> responsePredicate = response -> {
                        boolean urlMatches = response.url().contains("api/v1/devices");
                        boolean methodIsGet = "GET".equalsIgnoreCase(response.request().method());
                        boolean statusIsOk = response.status() == 200;
                        return urlMatches && methodIsGet && statusIsOk;
                    };

                    // Refresh to trigger API call
                    Response apiResponse = page.waitForResponse(responsePredicate, options, () -> {
                        page.reload();
                    });

                    Request capturedRequest = apiResponse.request();
                    Map<String, String> requestHeaders = capturedRequest.headers();
                    Map<String, String> headers = new HashMap<>();
                    headers.put("cookie", requestHeaders.get("cookie"));
                    headers.put("X-Tenant-ID", requestHeaders.get("x-tenant-id"));
                    SuiteExtension.accountHeaders.put(username, headers);
                    setWeblink(requestHeaders.get("x-tenant-id"));
                    System.out.println("Step 2a: Headers captured successfully");
                } catch (Exception e) {
                    System.out.println("Failed to capture headers on saved session, will re-login: " + e.getMessage());
                    // Clear invalid auth state and fall through to login
                    AuthStateManager.clearAuthState(username, HarmonixProperty.env);
                    System.out.println("Cleared invalid auth state, will perform full login");
                    // Don't return here, continue to full login
                }

                if (SuiteExtension.accountHeaders.containsKey(username)) {
                    userAccountProperty.setCurrentTestAccount(currentTestAccount);
                    System.out.println("=== Login Process Complete (Used Saved Session) ===");
                    return;
                }
            } else {
                System.out.println("Step 2: Not logged in (page title not found), will proceed to login");
            }
        } catch (Exception e) {
            System.out.println("Exception during login check: " + e.getMessage());
            e.printStackTrace();
        }

        // Need to login - no valid saved session
        System.out.println("Step 3: Performing full login for: " + username);
        System.out.println("Step 3a: Executing login helper...");

        try {
            // Execute login without waiting for API response first
            helperContext.getLoginHelper().loginWebportalWithOtp(username, userAccountProperty.accountPassword);
            System.out.println("Step 3a: Login helper completed");
        } catch (InterruptedException e) {
            throw new RuntimeException("Login interrupted", e);
        }

        // Wait for page to stabilize
        try {
            Thread.sleep(2000);
        } catch (InterruptedException e) {
            // Ignore
        }

        if(env.equalsIgnoreCase("sandbox")){
            System.out.println("Step 3b: Sandbox environment, navigating to URL again...");
            page.navigate(URL);
            page.waitForLoadState(LoadState.DOMCONTENTLOADED,
                    new Page.WaitForLoadStateOptions().setTimeout(TIMEOUT_SECONDS_MIDDLE * 3));
        }
        
        // Verify we reached the device inventory page
        System.out.println("Step 4: Verifying login success...");
        if (!CommonMethod.isVisible(pagesContext.getDeviceInventoryPage().pageTitle, 30)) {
            System.err.println("❌ Login may have failed - device page title not found");
            System.err.println("Current URL: " + page.url());
            throw new RuntimeException("Login verification failed - not on device inventory page");
        }

        helperContext.getDeviceInventoryHelper().verifyAllKeyElementsOnDeviceInventoryPresence();
        System.out.println("✓ Successfully on device inventory page");

        // Now capture headers by triggering an API call
        System.out.println("Step 5: Capturing request headers...");
        try {
            Page.WaitForResponseOptions options =
                    new Page.WaitForResponseOptions().setTimeout(TIMEOUT_SECONDS_MIDDLE);

            Predicate<Response> responsePredicate = response -> {
                boolean urlMatches = response.url().contains("api/v1/devices");
                boolean methodIsGet = "GET".equalsIgnoreCase(response.request().method());
                boolean statusIsOk = response.status() == 200;
                return urlMatches && methodIsGet && statusIsOk;
            };

            // Reload page to trigger API call
            Response apiResponse = page.waitForResponse(responsePredicate, options, () -> {
                System.out.println("Reloading page to trigger API call...");
                page.reload();
            });

            Request capturedRequest = apiResponse.request();
            Map<String, String> requestHeaders = capturedRequest.headers();
            Map<String, String> headers = new HashMap<>();
            headers.put("cookie", requestHeaders.get("cookie"));
            headers.put("X-Tenant-ID", requestHeaders.get("x-tenant-id"));

            SuiteExtension.accountHeaders.put(username, headers);
            setWeblink(requestHeaders.get("x-tenant-id"));
            System.out.println("✓ Headers captured successfully");
        } catch (Exception e) {
            System.err.println("⚠ Warning: Failed to capture headers via API: " + e.getMessage());
            System.err.println("Will try to continue without headers...");
            // Don't fail the test, try to continue
        }

        userAccountProperty.setCurrentTestAccount(currentTestAccount);

        System.out.println("=== Login Process Complete (Full Login) ===");
        System.out.println("Note: Auth state will be saved in @AfterEach");
    }



    @AfterEach
    public void tearDown(TestInfo testInfo) {
        try {
            testcaseName = testInfo.getDisplayName().replace("()", "").replace("/", "_");

            // Save auth state BEFORE closing context
            if (context != null && currentTestAccount != null) {
                try {
                    System.out.println("=== Saving Auth State in @AfterEach ===");
                    System.out.println("  - Test: " + testcaseName);
                    System.out.println("  - Account: " + currentTestAccount);

                    String environment = HarmonixProperty.env != null ? HarmonixProperty.env : "stage";
                    AuthStateManager.saveAuthState(context, currentTestAccount, environment);
                    System.out.println("✓ Auth state saved successfully in @AfterEach");
                } catch (Exception e) {
                    System.out.println("✗ Failed to save auth state in @AfterEach: " + e.getMessage());
                    e.printStackTrace();
                }
            }

            quitBrowserAndResources(testcaseName);
        } finally {
            PlaywrightThreadLocal.clear();
            // Ensure the account is returned to the pool
            if (currentTestAccount != null) {
                SuiteExtension.accountPool.offer(currentTestAccount);
                System.out.println("Thread " + Thread.currentThread().getId() + " returned account: " + currentTestAccount);
                currentTestAccount = null;
            }
        }
    }

    private void quitBrowserAndResources(String testcaseName) {
        // Get resources from playwrightContext
        BrowserContext context = playwrightContext.getContext();
        Page page = playwrightContext.getPage();
        Playwright playwright = playwrightContext.getPlaywright();

        // 1. Screenshot and tracing
        if (context != null) {
            // Screenshot
            try {
                if (page != null && !page.isClosed()) {
                    Path screenshotPath = Paths.get("screenshots", timestamp, testcaseName + ".png");
                    Files.createDirectories(screenshotPath.getParent());
                    screenshot = page.screenshot(new Page.ScreenshotOptions().setPath(screenshotPath));
                }
            } catch (Exception e) {
                System.err.println("Screenshot failed: " + e.getMessage());
            }
            // Stop tracing
            try {
                String cleanTestName = testcaseName.split(",")[0].strip();
                Path tracePath = Paths.get("playwrightReport", timestamp, cleanTestName + ".zip");
                Files.createDirectories(tracePath.getParent());
                context.tracing().stop(new Tracing.StopOptions().setPath(tracePath));
            } catch (Exception e) {
                System.err.println("Tracing save failed: " + e.getMessage());
            }
        }

        // 2. Close resources:
        // For launchPersistentContext, just close the context, it will take care of closing the browser.
        closeResource(context, "BrowserContext");
        closeResource(playwright, "Playwright");
    }

    private void closeResource(AutoCloseable resource, String resourceName) {
        if (resource != null) {
            try {
                resource.close();
                System.out.println(resourceName + " closed successfully.");
            } catch (Exception e) {
                System.err.println("Error closing " + resourceName + ": " + e.getMessage());
            }
        }
    }

    // zipFolder and zipFile methods remain unchanged
    // ...
    public static void zipFolder(String sourceFolderPath, String zipFilePath) {
        try {
            Path zipPath = Paths.get(zipFilePath);
            Files.createDirectories(zipPath.getParent());

            try (FileOutputStream fos = new FileOutputStream(zipFilePath);
                 ZipOutputStream zipOut = new ZipOutputStream(fos)) {
                File sourceFolder = new File(sourceFolderPath);
                zipFile(sourceFolder, sourceFolder.getName(), zipOut);
            }
            System.out.println("Folder compressed to: " + zipFilePath);
        } catch (IOException e) {
            System.err.println("Compression failed: " + e.getMessage());
            e.printStackTrace();
        }
    }

    private static void zipFile(File fileToZip, String fileName, ZipOutputStream zipOut) throws IOException {
        if (fileToZip.isHidden()) {
            return;
        }

        if (fileToZip.isDirectory()) {
            if (fileName.endsWith("/")) {
                zipOut.putNextEntry(new ZipEntry(fileName));
                zipOut.closeEntry();
            } else {
                zipOut.putNextEntry(new ZipEntry(fileName + "/"));
                zipOut.closeEntry();
            }

            File[] children = fileToZip.listFiles();
            if (children == null) {
                System.out.println("Empty directory: " + fileToZip.getAbsolutePath());
                return;
            }

            for (File childFile : children) {
                zipFile(childFile, fileName + "/" + childFile.getName(), zipOut);
            }
            return;
        }

        try (FileInputStream fis = new FileInputStream(fileToZip)) {
            ZipEntry zipEntry = new ZipEntry(fileName);
            zipOut.putNextEntry(zipEntry);
            byte[] bytes = new byte[1024];
            int length;
            while ((length = fis.read(bytes)) >= 0) {
                zipOut.write(bytes, 0, length);
            }
        }
    }

    void setWeblink(String tenantId) {
        if (tenantId.equalsIgnoreCase("catdog")) {
            if (env.equalsIgnoreCase("dev")) {
                tenantId = "tiger";
            } else if (env.equalsIgnoreCase("stage")) {
                tenantId = "lion";
            } else if (env.equalsIgnoreCase("prod")) {
                tenantId = "leopard";
            } else if (env.equalsIgnoreCase("sandbox")) {
                tenantId = "lion";
            }
        }
        if(env.equalsIgnoreCase("dev")){
            HarmonixProperty.webLinkUrl = "https://"+tenantId+"-device.zpc-dev.zebra.com/weblink/connect/";
        } else if(env.equalsIgnoreCase("stage")){
            HarmonixProperty.webLinkUrl = "https://"+tenantId+"-device.zpc-stage.zebra.com/weblink/connect/";
        } else if(env.equalsIgnoreCase("prod")) {
            HarmonixProperty.webLinkUrl = "https://"+tenantId+"-device.zpc.zebra.com/weblink/connect/";
        } else if(env.equalsIgnoreCase("sandbox")){
            switch (backendENV){
                case "dev":
                    HarmonixProperty.webLinkUrl = "https://"+tenantId+"-device.zpc-dev.zebra.com/weblink/connect/";
                    break;
                case "stage":
                    HarmonixProperty.webLinkUrl = "https://"+tenantId+"-device.zpc-stage.zebra.com/weblink/connect/";
                    break;
                case "prod":
                    HarmonixProperty.webLinkUrl = "https://"+tenantId+"-device.zpc.zebra.com/weblink/connect/";
                    break;
                default:
                    String CLUSTER_ID = System.getenv("CLUSTER_ID");
                    HarmonixProperty.webLinkUrl = "https://"+tenantId+"-device."+ CLUSTER_ID +".zpc-sandbox.zebra.com/weblink/connect/";
                    break;
            }
        } else {
            HarmonixProperty.webLinkUrl = "https://"+tenantId+"-device.zpc-dev.zebra.com/weblink/connect/";
        }
    }
}
