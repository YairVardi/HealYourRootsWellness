package PageObjects;

import Extensions.UiAssertions;
import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.assertions.PlaywrightAssertions;
import com.microsoft.playwright.options.AriaRole;

public final class LoginPage extends BasePage {
    public final Locator emailInput;
    public final Locator passwordInput;
    public final Locator emailSignInButton;
    public final Locator googleButton;
    public final Locator replitButton;
    public final Locator createAccountLink;
    public final Locator loginFailureMessage;

    public LoginPage(Page page) {
        super(page);
        this.emailInput = page.getByPlaceholder("your@email.com");
        this.passwordInput = page.getByPlaceholder("Your password");
        this.emailSignInButton = page.getByRole(
                AriaRole.BUTTON,
                new Page.GetByRoleOptions().setName(UiAssertions.regex("sign in with email"))
        );
        this.googleButton = page.getByRole(
                AriaRole.BUTTON,
                new Page.GetByRoleOptions().setName(UiAssertions.regex("continue with google"))
        );
        this.replitButton = page.getByRole(
                AriaRole.BUTTON,
                new Page.GetByRoleOptions().setName(UiAssertions.regex("continue with replit"))
        );
        this.createAccountLink = page.getByRole(
                AriaRole.LINK,
                new Page.GetByRoleOptions().setName(UiAssertions.regex("create a free account"))
        );
        this.loginFailureMessage = page.getByText(UiAssertions.regex("login failed")).first();
    }

    public void goTo() {
        open("/dashboard/login");
    }

    public void expectLoaded() {
        PlaywrightAssertions.assertThat(emailInput).isVisible();
        PlaywrightAssertions.assertThat(passwordInput).isVisible();
        PlaywrightAssertions.assertThat(emailSignInButton).isVisible();
        PlaywrightAssertions.assertThat(googleButton).isVisible();
        PlaywrightAssertions.assertThat(replitButton).isVisible();
    }

    public void signInWithEmail(String email, String password) {
        emailInput.fill(email);
        passwordInput.fill(password);
        emailSignInButton.click();
    }

    public void expectLoginFailureRendered() {
        PlaywrightAssertions.assertThat(loginFailureMessage).isVisible();
    }

    public String visibleBodyText() {
        return UiAssertions.normalizeWhitespace(page.locator("body").textContent());
    }
}
