package PageObjects;

import Helpers.ConsultationData;
import Extensions.UiAssertions;
import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.assertions.PlaywrightAssertions;
import com.microsoft.playwright.options.AriaRole;

import java.util.regex.Pattern;

public final class ConsultationPage extends BasePage {
    public final Locator consultationHeading;
    public final Locator nextButton;
    public final Locator previousButton;
    public final Locator scheduleButton;
    public final Locator firstNameInput;
    public final Locator lastNameInput;
    public final Locator emailInput;
    public final Locator phoneInput;

    public ConsultationPage(Page page) {
        super(page);
        this.consultationHeading = page.getByRole(
                AriaRole.HEADING,
                new Page.GetByRoleOptions().setName(UiAssertions.regex("Schedule Your Free Consultation"))
        );
        this.nextButton = page.getByRole(
                AriaRole.BUTTON,
                new Page.GetByRoleOptions().setName(UiAssertions.regex("^Next$"))
        );
        this.previousButton = page.getByRole(
                AriaRole.BUTTON,
                new Page.GetByRoleOptions().setName(UiAssertions.regex("^Previous$"))
        );
        this.scheduleButton = page.getByRole(
                AriaRole.BUTTON,
                new Page.GetByRoleOptions().setName(UiAssertions.regex("Schedule Consultation"))
        );
        this.firstNameInput = page.getByLabel("First Name");
        this.lastNameInput = page.getByLabel("Last Name");
        this.emailInput = page.getByLabel("Email Address");
        this.phoneInput = page.getByLabel("Phone Number");
    }

    public void goTo() {
        open("/consultation");
    }

    public void expectLoaded() {
        expectHealthy();
        PlaywrightAssertions.assertThat(consultationHeading).isVisible();
    }

    public void goNext() {
        nextButton.click();
    }

    public void selectServiceType(String serviceTypeLabel) {
        Locator option = page.getByRole(
                AriaRole.RADIO,
                new Page.GetByRoleOptions().setName(serviceTypeLabel).setExact(true)
        );
        option.click(new Locator.ClickOptions().setForce(true));
        PlaywrightAssertions.assertThat(option).hasAttribute("aria-checked", "true");
    }

    public void chooseFocusArea(String focusAreaLabel) {
        page.getByText(focusAreaLabel, new Page.GetByTextOptions().setExact(true)).click();
    }

    public void selectState(String stateName) {
        selectRadixOption("Select your state|" + Pattern.quote(stateName), stateName);
    }

    public void chooseInsuranceOption(String optionLabel) {
        Locator option = page.getByRole(
                AriaRole.RADIO,
                new Page.GetByRoleOptions().setName(optionLabel).setExact(true)
        );
        option.click(new Locator.ClickOptions().setForce(true));
        PlaywrightAssertions.assertThat(option).hasAttribute("aria-checked", "true");
    }

    public void selectInsuranceProvider(String providerName) {
        selectRadixOption("Select your insurance provider|" + Pattern.quote(providerName), providerName);
    }

    public void fillPersonalDetails(ConsultationData input) {
        firstNameInput.fill(input.firstName);
        lastNameInput.fill(input.lastName);
        emailInput.fill(input.email);
        phoneInput.fill(input.phone);
    }

    public void moveToPersonalInfo(ConsultationData input) {
        selectServiceType(input.serviceTypeLabel);
        goNext();
        PlaywrightAssertions.assertThat(page.getByRole(
                AriaRole.HEADING,
                new Page.GetByRoleOptions().setName(UiAssertions.regex("What areas would you like to focus on\\?"))
        )).isVisible();

        if (input.focusAreaLabel != null) {
            chooseFocusArea(input.focusAreaLabel);
        }
        goNext();
        PlaywrightAssertions.assertThat(page.getByRole(
                AriaRole.HEADING,
                new Page.GetByRoleOptions().setName(UiAssertions.regex("What state do you live in\\?"))
        )).isVisible();

        selectState(input.stateName);
        goNext();
        PlaywrightAssertions.assertThat(page.getByRole(
                AriaRole.HEADING,
                new Page.GetByRoleOptions().setName(UiAssertions.regex("Do you have insurance\\?|Insurance Information"))
        )).isVisible();

        chooseInsuranceOption(input.hasInsuranceOptionLabel);
        goNext();

        if (input.insuranceProviderLabel != null) {
            PlaywrightAssertions.assertThat(page.getByRole(
                    AriaRole.HEADING,
                    new Page.GetByRoleOptions().setName(UiAssertions.regex("What insurance provider do you have\\?"))
            )).isVisible();
            selectInsuranceProvider(input.insuranceProviderLabel);
            goNext();
        }

        PlaywrightAssertions.assertThat(page.getByRole(
                AriaRole.HEADING,
                new Page.GetByRoleOptions().setName(UiAssertions.regex("Tell us about yourself"))
        )).isVisible();
    }

    public void selectFirstRecommendedTherapist(String expectedTherapistName) {
        PlaywrightAssertions.assertThat(
                page.getByText(expectedTherapistName, new Page.GetByTextOptions().setExact(true))
        ).isVisible();
        page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName(UiAssertions.regex("^Select$")))
                .first()
                .click();
    }

    public void chooseDate(String dateLabel) {
        page.getByText(dateLabel, new Page.GetByTextOptions().setExact(true)).click();
    }

    public void chooseTime(String timeLabel) {
        Locator exactTime = page.getByRole(
                AriaRole.BUTTON,
                new Page.GetByRoleOptions().setName(UiAssertions.regex("^" + Pattern.quote(timeLabel) + "$"))
        ).first();
        if (exactTime.count() > 0 && exactTime.isVisible()) {
            exactTime.click();
            return;
        }

        PlaywrightAssertions.assertThat(page.getByText(UiAssertions.regex("Available Times"))).isVisible();
        Locator firstVisibleTime = page.locator("button")
                .filter(new Locator.FilterOptions().setHasText(UiAssertions.regex("\\b\\d{1,2}:\\d{2}\\s*(AM|PM)\\b")))
                .first();
        PlaywrightAssertions.assertThat(firstVisibleTime).isVisible();
        firstVisibleTime.click();
    }

    public void completeHappyPath(ConsultationData input) {
        moveToPersonalInfo(input);
        fillPersonalDetails(input);
        goNext();
        selectFirstRecommendedTherapist(input.therapistName);
        goNext();
        chooseDate(input.dateLabel);
        chooseTime(input.timeLabel);
        PlaywrightAssertions.assertThat(scheduleButton).isEnabled();
        scheduleButton.click();
    }

    public void expectConfirmation(String firstName) {
        PlaywrightAssertions.assertThat(page.getByRole(
                AriaRole.HEADING,
                new Page.GetByRoleOptions().setName(UiAssertions.regex("Thank You"))
        ).first()).isVisible();
        PlaywrightAssertions.assertThat(page.getByText(UiAssertions.regex("What Happens Next\\?"))).isVisible();
    }

    public boolean isNextEnabled() {
        return nextButton.isEnabled();
    }

    private void selectRadixOption(String triggerExpression, String optionName) {
        Locator trigger = page.locator("button, [role=\"combobox\"]")
                .filter(new Locator.FilterOptions().setHasText(UiAssertions.regex(triggerExpression)))
                .first();
        trigger.click();
        Locator option = page.getByText(optionName, new Page.GetByTextOptions().setExact(true)).last();
        PlaywrightAssertions.assertThat(option).isVisible();
        option.click();
    }
}
