package PageObjects.Components;

import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.assertions.PlaywrightAssertions;

import java.util.regex.Pattern;

public final class Footer {
    public final Locator root;

    public Footer(Page page) {
        this.root = page.locator("footer").first();
    }

    public Locator link(Pattern name) {
        return root.locator("a").filter(new Locator.FilterOptions().setHasText(name)).first();
    }

    public void expectVisible() {
        PlaywrightAssertions.assertThat(root).isVisible();
    }
}
