package PageObjects.Components;

import Extensions.UiAssertions;
import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.assertions.PlaywrightAssertions;

public final class Header {
    public final Locator root;
    public final NavigationMenu navigationMenu;
    public final Locator logoLink;
    public final Locator findTherapistLink;
    public final Locator loginLink;
    public final Locator joinTherapistLink;

    public Header(Page page) {
        this.root = page.locator("header").first();
        this.navigationMenu = new NavigationMenu(page);
        this.logoLink = root.locator("a").first();
        this.findTherapistLink = root.locator("a")
                .filter(new Locator.FilterOptions().setHasText(UiAssertions.regex("find a therapist")))
                .first();
        this.loginLink = root.locator("a")
                .filter(new Locator.FilterOptions().setHasText(UiAssertions.regex("^login$")))
                .first();
        this.joinTherapistLink = root.locator("a")
                .filter(new Locator.FilterOptions().setHasText(UiAssertions.regex("join as a therapist")))
                .first();
    }

    public void expectVisible() {
        PlaywrightAssertions.assertThat(root).isVisible();
        PlaywrightAssertions.assertThat(logoLink).isVisible();
    }
}
