package Utilities;

import com.microsoft.playwright.Browser;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.Playwright;
import com.microsoft.playwright.assertions.PlaywrightAssertions;
import org.testng.annotations.AfterMethod;
import org.testng.annotations.BeforeMethod;
import org.testng.annotations.BeforeSuite;

public abstract class BaseTest {
    protected Playwright playwright;
    protected Browser browser;
    protected BrowserContext context;
    protected Page page;

    @BeforeSuite(alwaysRun = true)
    protected void writeAllureEnvironment() {
        AllureEnvironment.write();
    }

    @BeforeMethod(alwaysRun = true)
    protected void createBrowser() {
        playwright = Playwright.create();
        browser = browserType().launch(new BrowserType.LaunchOptions().setHeadless(TestEnvironment.headless()));
        context = browser.newContext(new Browser.NewContextOptions()
                .setBaseURL(TestEnvironment.baseUrl())
                .setLocale("en-US"));
        context.setDefaultTimeout(TestEnvironment.DEFAULT_TIMEOUT_MS);
        context.setDefaultNavigationTimeout(TestEnvironment.DEFAULT_TIMEOUT_MS);
        PlaywrightAssertions.setDefaultAssertionTimeout(TestEnvironment.EXPECT_TIMEOUT_MS);
        page = context.newPage();
    }

    @AfterMethod(alwaysRun = true)
    protected void closeBrowser() {
        if (context != null) {
            context.close();
        }
        if (browser != null) {
            browser.close();
        }
        if (playwright != null) {
            playwright.close();
        }
    }

    protected String browserName() {
        return TestEnvironment.browserName();
    }

    protected boolean isChromium() {
        return "chromium".equals(browserName());
    }

    private BrowserType browserType() {
        switch (browserName()) {
            case "firefox":
                return playwright.firefox();
            case "webkit":
                return playwright.webkit();
            case "chromium":
                return playwright.chromium();
            default:
                throw new IllegalArgumentException("Unsupported browser '" + browserName() + "'.");
        }
    }
}
