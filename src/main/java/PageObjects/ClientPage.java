package PageObjects;

import Extensions.UiAssertions;
import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.assertions.PlaywrightAssertions;
import com.microsoft.playwright.options.AriaRole;

public final class ClientPage extends BasePage {
    public final Locator directoryHeading;
    public final Locator filtersButton;

    public ClientPage(Page page) {
        super(page);
        this.directoryHeading = page.getByRole(
                AriaRole.HEADING,
                new Page.GetByRoleOptions().setName(UiAssertions.regex("Find a Therapist"))
        );
        this.filtersButton = page.getByRole(
                AriaRole.BUTTON,
                new Page.GetByRoleOptions().setName(UiAssertions.regex("^Filters$"))
        );
    }

    public void goToRoute(String path) {
        open(path);
    }

    public void goToDirectory() {
        goToRoute("/find-a-therapist");
    }

    public void expectDirectoryLoaded() {
        expectHealthy();
        PlaywrightAssertions.assertThat(directoryHeading).isVisible();
        PlaywrightAssertions.assertThat(filtersButton).isVisible();
    }
}
