package PageObjects.Components;

import Extensions.UiAssertions;
import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.assertions.PlaywrightAssertions;
import com.microsoft.playwright.options.AriaRole;

import java.util.regex.Pattern;

public final class NavigationMenu {
    public final Locator menuToggle;
    private final Page page;

    public NavigationMenu(Page page) {
        this.page = page;
        this.menuToggle = page.getByRole(
                AriaRole.BUTTON,
                new Page.GetByRoleOptions().setName(UiAssertions.regex("toggle menu"))
        );
    }

    public Locator link(Pattern name) {
        return page.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName(name)).first();
    }

    public void openMobileMenu() {
        if (menuToggle.isVisible()) {
            menuToggle.click();
            PlaywrightAssertions.assertThat(menuToggle).hasAttribute("aria-expanded", "true");
        }
    }

    public void closeMobileMenu() {
        if (menuToggle.isVisible()) {
            menuToggle.click();
            PlaywrightAssertions.assertThat(menuToggle).hasAttribute("aria-expanded", "false");
        }
    }
}
