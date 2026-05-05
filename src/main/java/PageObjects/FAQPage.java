package PageObjects;

import Extensions.UiAssertions;
import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.assertions.PlaywrightAssertions;
import com.microsoft.playwright.options.AriaRole;

public final class FAQPage extends BasePage {
    public final Locator refreshButton;

    public FAQPage(Page page) {
        super(page);
        this.refreshButton = page.getByRole(
                AriaRole.BUTTON,
                new Page.GetByRoleOptions().setName(UiAssertions.regex("Refresh Page"))
        );
    }

    public void goTo() {
        open("/faq");
    }

    public void expectLoaded() {
        expectHealthy();
        PlaywrightAssertions.assertThat(page.getByRole(
                AriaRole.HEADING,
                new Page.GetByRoleOptions().setName(UiAssertions.regex("Frequently Asked Questions|FAQ"))
        )).isVisible();
    }
}
