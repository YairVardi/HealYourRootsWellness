package PageObjects;

import Extensions.UiAssertions;
import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.assertions.PlaywrightAssertions;
import com.microsoft.playwright.options.AriaRole;

public final class ContactPage extends BasePage {
    public final Locator heading;
    public final Locator formHeading;
    public final Locator bookNowLink;

    public ContactPage(Page page) {
        super(page);
        this.heading = page.getByRole(
                AriaRole.HEADING,
                new Page.GetByRoleOptions().setName(UiAssertions.regex("^Contact$"))
        );
        this.formHeading = page.getByRole(
                AriaRole.HEADING,
                new Page.GetByRoleOptions().setName(UiAssertions.regex("Heal Your Roots Wellness Contact Us Form"))
        );
        this.bookNowLink = page.getByRole(
                AriaRole.LINK,
                new Page.GetByRoleOptions().setName(UiAssertions.regex("^Book Now$"))
        );
    }

    public void goTo() {
        open("/contact");
    }

    public void expectLoaded() {
        expectHealthy();
        PlaywrightAssertions.assertThat(heading).isVisible();
        PlaywrightAssertions.assertThat(formHeading).isVisible();
        PlaywrightAssertions.assertThat(bookNowLink).isVisible();
    }

    public void openConsultation() {
        bookNowLink.click();
    }
}
