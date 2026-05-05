package SanityTest;

import Helpers.ConsultationData;
import Helpers.InvalidInputs;
import Helpers.KnownProductionIssues;
import Helpers.TestData;
import Utilities.BaseTest;
import PageObjects.ConsultationPage;
import Helpers.ConsultationMockController;
import Helpers.ConsultationMockOptions;
import Helpers.ConsultationMocks;
import Extensions.UiAssertions;
import com.microsoft.playwright.Locator;
import com.microsoft.playwright.assertions.PlaywrightAssertions;
import com.microsoft.playwright.options.AriaRole;
import org.testng.annotations.Test;

import java.util.regex.Pattern;

import static org.assertj.core.api.Assertions.assertThat;

public class FormsValidationTest extends BaseTest {
    @Test
    public void emptyPersonalInformationKeepsConsultationFlowBlocked() {
        ConsultationMockController controller = ConsultationMocks.mockConsultationApis(page);
        ConsultationPage consultationPage = new ConsultationPage(page);

        consultationPage.goTo();
        consultationPage.moveToPersonalInfo(validInput(controller));

        assertThat(consultationPage.isNextEnabled()).isFalse();
    }

    @Test
    public void invalidEmailFormatsShouldBeBlockedBeforeTherapistMatching() {
        UiAssertions.expectKnownIssue(KnownProductionIssues.INVALID_EMAIL_VALIDATION, () -> {
            ConsultationMockController controller = ConsultationMocks.mockConsultationApis(page);
            ConsultationPage consultationPage = new ConsultationPage(page);

            consultationPage.goTo();
            consultationPage.moveToPersonalInfo(validInput(controller));

            for (String invalidEmail : InvalidInputs.INVALID_EMAILS) {
                consultationPage.fillPersonalDetails(TestData.VALID_CONSULTATION_DATA.withPersonalDetails(
                        TestData.VALID_CONSULTATION_DATA.firstName,
                        TestData.VALID_CONSULTATION_DATA.lastName,
                        invalidEmail,
                        TestData.VALID_CONSULTATION_DATA.phone
                ));

                Boolean isValidEmail = (Boolean) consultationPage.emailInput.evaluate("element => element.checkValidity()");
                assertThat(isValidEmail)
                        .as("%s should fail HTML email validation.", invalidEmail)
                        .isFalse();
                assertThat(consultationPage.isNextEnabled()).isFalse();
            }
        });
    }

    @Test
    public void unicodeSpacesAndSpecialCharactersCanBeEnteredWithoutCrashingTheFlow() {
        ConsultationMockController controller = ConsultationMocks.mockConsultationApis(page);
        ConsultationPage consultationPage = new ConsultationPage(page);

        consultationPage.goTo();
        consultationPage.moveToPersonalInfo(validInput(controller));
        consultationPage.fillPersonalDetails(TestData.VALID_CONSULTATION_DATA.withPersonalDetails(
                InvalidInputs.LEADING_TRAILING_SPACES,
                InvalidInputs.UNICODE_HEBREW_TEXT,
                TestData.VALID_CONSULTATION_DATA.email,
                TestData.VALID_CONSULTATION_DATA.phone
        ));

        PlaywrightAssertions.assertThat(consultationPage.firstNameInput).hasValue(InvalidInputs.LEADING_TRAILING_SPACES);
        PlaywrightAssertions.assertThat(consultationPage.lastNameInput).hasValue(InvalidInputs.UNICODE_HEBREW_TEXT);

        consultationPage.goNext();
        PlaywrightAssertions.assertThat(page.getByRole(
                AriaRole.HEADING,
                new com.microsoft.playwright.Page.GetByRoleOptions()
                        .setName(UiAssertions.regex("Choose your preferred therapist"))
        )).isVisible();
    }

    @Test
    public void copyPasteStyleEntryAndLongInputSurviveOnPersonalInfoStep() {
        ConsultationMockController controller = ConsultationMocks.mockConsultationApis(page);
        ConsultationPage consultationPage = new ConsultationPage(page);

        consultationPage.goTo();
        consultationPage.moveToPersonalInfo(validInput(controller));

        UiAssertions.insertTextWithKeyboard(page, consultationPage.firstNameInput, InvalidInputs.LONG_INPUT);
        UiAssertions.insertTextWithKeyboard(page, consultationPage.lastNameInput, "Copied Name");
        consultationPage.emailInput.fill(TestData.VALID_CONSULTATION_DATA.email);
        consultationPage.phoneInput.fill(TestData.VALID_CONSULTATION_DATA.phone);

        PlaywrightAssertions.assertThat(consultationPage.firstNameInput).hasValue(InvalidInputs.LONG_INPUT);
        PlaywrightAssertions.assertThat(consultationPage.lastNameInput).hasValue("Copied Name");
        assertThat(consultationPage.isNextEnabled()).isTrue();
    }

    @Test
    public void multipleRapidSubmitClicksDoNotCreateDuplicateConsultationRequests() throws Exception {
        if (isChromium()) {
            UiAssertions.expectKnownIssue(
                    KnownProductionIssues.DUPLICATE_CONSULTATION_SUBMIT,
                    this::exerciseRapidSubmitAndAssertSingleRequest
            );
        } else {
            exerciseRapidSubmitAndAssertSingleRequest();
        }
    }

    @Test
    public void consultationFlowStaysUsableWhenAvailabilityCallsAreSlow() {
        ConsultationMockController controller = ConsultationMocks.mockConsultationApis(
                page,
                new ConsultationMockOptions().delayAvailabilityMs(800)
        );
        ConsultationPage consultationPage = new ConsultationPage(page);
        ConsultationData input = validInput(controller);

        consultationPage.goTo();
        consultationPage.moveToPersonalInfo(input);
        consultationPage.fillPersonalDetails(input);
        consultationPage.goNext();
        consultationPage.selectFirstRecommendedTherapist(input.therapistName);
        consultationPage.goNext();
        consultationPage.chooseDate(controller.fixtures().labels().dateLabel());

        PlaywrightAssertions.assertThat(page.getByText(UiAssertions.regex("Available Times"))).isVisible();
        PlaywrightAssertions.assertThat(page.locator("button")
                .filter(new Locator.FilterOptions().setHasText(UiAssertions.regex("\\b\\d{1,2}:\\d{2}\\s*(AM|PM)\\b")))
                .first()).isVisible();
    }

    private void exerciseRapidSubmitAndAssertSingleRequest() {
        ConsultationMockController controller = ConsultationMocks.mockConsultationApis(page);
        ConsultationPage consultationPage = new ConsultationPage(page);
        ConsultationData input = validInput(controller);

        consultationPage.goTo();
        consultationPage.moveToPersonalInfo(input);
        consultationPage.fillPersonalDetails(input);
        consultationPage.goNext();
        consultationPage.selectFirstRecommendedTherapist(input.therapistName);
        consultationPage.goNext();
        consultationPage.chooseDate(controller.fixtures().labels().dateLabel());
        consultationPage.chooseTime(controller.fixtures().labels().timeLabel());

        consultationPage.scheduleButton.click(new Locator.ClickOptions().setClickCount(3));
        consultationPage.expectConfirmation(input.firstName);
        assertThat(controller.submittedPayloads()).hasSize(1);
    }

    private ConsultationData validInput(ConsultationMockController controller) {
        return TestData.VALID_CONSULTATION_DATA.withDateAndTime(
                controller.fixtures().labels().dateLabel(),
                controller.fixtures().labels().timeLabel()
        );
    }
}
