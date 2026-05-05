package PageObjects;

import Extensions.UiAssertions;
import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.assertions.PlaywrightAssertions;
import com.microsoft.playwright.options.AriaRole;

public final class HomePage extends BasePage {
    public final Locator heroHeading;
    public final Locator primaryClientCta;
    public final Locator primaryTherapistCta;
    public final Locator scheduleConsultLink;

    public HomePage(Page page) {
        super(page);
        this.heroHeading = page.getByRole(
                AriaRole.HEADING,
                new Page.GetByRoleOptions().setName(UiAssertions.regex("A Therapist Directory & Mental Health Community"))
        );
        this.primaryClientCta = page.getByRole(
                AriaRole.LINK,
                new Page.GetByRoleOptions().setName("FIND A THERAPIST").setExact(true)
        ).first();
        this.primaryTherapistCta = page.getByRole(
                AriaRole.LINK,
                new Page.GetByRoleOptions().setName("I'm a therapist").setExact(true)
        ).first();
        this.scheduleConsultLink = page.getByRole(
                AriaRole.LINK,
                new Page.GetByRoleOptions().setName(UiAssertions.regex("schedule a consult"))
        ).first();
    }

    public void goTo() {
        open("/");
    }

    public void expectLoaded() {
        expectHealthy();
        header.expectVisible();
        PlaywrightAssertions.assertThat(heroHeading).isVisible();
        PlaywrightAssertions.assertThat(primaryClientCta).isVisible();
        PlaywrightAssertions.assertThat(primaryTherapistCta).isVisible();
        footer.expectVisible();
    }
}
