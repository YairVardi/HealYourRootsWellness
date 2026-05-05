package PageObjects;

import Extensions.UiAssertions;
import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.assertions.PlaywrightAssertions;
import com.microsoft.playwright.options.AriaRole;

public final class TherapistPage extends BasePage {
    public final Locator clinicianHeading;

    public TherapistPage(Page page) {
        super(page);
        this.clinicianHeading = page.getByRole(
                AriaRole.HEADING,
                new Page.GetByRoleOptions().setName(UiAssertions.regex("For Clinicians"))
        );
    }

    public void goToWhyJoin() {
        open("/for-clinicians");
    }

    public void goToJoin() {
        open("/join");
    }

    public void goToGroupPractice() {
        open("/group-practice");
    }

    public void expectClinicianLandingLoaded() {
        expectHealthy();
        PlaywrightAssertions.assertThat(clinicianHeading).isVisible();
    }
}
