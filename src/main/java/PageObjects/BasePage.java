package PageObjects;

import PageObjects.Components.Footer;
import PageObjects.Components.Header;
import Utilities.TestEnvironment;
import Extensions.UiAssertions;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.options.WaitUntilState;

import java.util.regex.Pattern;

public abstract class BasePage {
    protected final Page page;
    public final Header header;
    public final Footer footer;

    protected BasePage(Page page) {
        this.page = page;
        this.header = new Header(page);
        this.footer = new Footer(page);
    }

    protected void open(String path) {
        page.navigate(
                TestEnvironment.absoluteUrl(path),
                new Page.NavigateOptions().setWaitUntil(WaitUntilState.DOMCONTENTLOADED)
        );
        UiAssertions.waitForAppReady(page);
    }

    public void refresh() {
        page.reload(new Page.ReloadOptions().setWaitUntil(WaitUntilState.DOMCONTENTLOADED));
        UiAssertions.waitForAppReady(page);
    }

    public void expectHealthy() {
        UiAssertions.assertPageHealthy(page);
    }

    public void expectPath(Pattern pathPattern) {
        UiAssertions.assertUrlMatches(page, pathPattern);
    }
}
