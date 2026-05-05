package PageObjects;

import Extensions.UiAssertions;
import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.assertions.PlaywrightAssertions;

public final class DashboardPage extends BasePage {
    public final Locator signInHeading;

    public DashboardPage(Page page) {
        super(page);
        this.signInHeading = page.getByText(UiAssertions.regex("Sign in to your therapist community account"));
    }

    public void goTo() {
        open("/dashboard");
    }

    public void expectProtectedRedirect() {
        UiAssertions.assertUrlMatches(page, UiAssertions.regex("/dashboard/login(?:$|[?#/])"));
        PlaywrightAssertions.assertThat(signInHeading).isVisible();
    }
}
