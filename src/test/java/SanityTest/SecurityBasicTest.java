package SanityTest;

import Helpers.ConsultationData;
import Helpers.InvalidInputs;
import Helpers.KnownProductionIssues;
import Helpers.TestData;
import Utilities.BaseTest;
import PageObjects.ConsultationPage;
import PageObjects.HomePage;
import PageObjects.LoginPage;
import Helpers.ConsultationMockController;
import Helpers.ConsultationMocks;
import Extensions.UiAssertions;
import com.microsoft.playwright.Response;
import com.microsoft.playwright.assertions.PlaywrightAssertions;
import com.microsoft.playwright.options.AriaRole;
import org.testng.annotations.Test;

import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;

public class SecurityBasicTest extends BaseTest {
    @Test
    public void homeConsultationAndLoginPagesStayOnHttps() {
        HomePage homePage = new HomePage(page);
        ConsultationPage consultationPage = new ConsultationPage(page);
        LoginPage loginPage = new LoginPage(page);

        homePage.goTo();
        UiAssertions.assertHttps(page);

        consultationPage.goTo();
        UiAssertions.assertHttps(page);

        loginPage.goTo();
        UiAssertions.assertHttps(page);
    }

    @Test
    public void scriptSqlHtmlAndSpecialCharacterPayloadsStayInertInConsultationInputs() {
        ConsultationMockController controller = ConsultationMocks.mockConsultationApis(page);
        ConsultationPage consultationPage = new ConsultationPage(page);
        List<String> dialogMessages = UiAssertions.attachDialogCollector(page);
        List<String> consoleMessages = UiAssertions.attachConsoleCollector(page);
        ConsultationData input = validInput(controller);

        consultationPage.goTo();
        consultationPage.moveToPersonalInfo(input);

        consultationPage.firstNameInput.fill(InvalidInputs.MALICIOUS_PAYLOADS.get(0));
        consultationPage.lastNameInput.fill(InvalidInputs.MALICIOUS_PAYLOADS.get(1));
        consultationPage.emailInput.fill(input.email);
        consultationPage.phoneInput.fill(input.phone);

        PlaywrightAssertions.assertThat(consultationPage.firstNameInput).hasValue(InvalidInputs.MALICIOUS_PAYLOADS.get(0));
        PlaywrightAssertions.assertThat(consultationPage.lastNameInput).hasValue(InvalidInputs.MALICIOUS_PAYLOADS.get(1));

        consultationPage.goNext();
        PlaywrightAssertions.assertThat(page.getByRole(
                AriaRole.HEADING,
                new com.microsoft.playwright.Page.GetByRoleOptions()
                        .setName(UiAssertions.regex("Choose your preferred therapist"))
        )).isVisible();

        UiAssertions.assertNoDialog(dialogMessages);
        UiAssertions.assertNoSensitiveConsoleLeak(consoleMessages, InvalidInputs.MALICIOUS_PAYLOADS.subList(0, 2));
    }

    @Test
    public void noSensitiveConsultationPayloadIsEchoedToConsoleDuringDataEntry() {
        ConsultationMockController controller = ConsultationMocks.mockConsultationApis(page);
        ConsultationPage consultationPage = new ConsultationPage(page);
        List<String> consoleMessages = UiAssertions.attachConsoleCollector(page);
        List<String> dialogMessages = UiAssertions.attachDialogCollector(page);
        ConsultationData input = validInput(controller);

        consultationPage.goTo();
        consultationPage.moveToPersonalInfo(input);
        consultationPage.fillPersonalDetails(input.withPersonalDetails(
                InvalidInputs.UNICODE_HEBREW_TEXT,
                InvalidInputs.SPECIAL_CHARACTERS,
                input.email,
                input.phone
        ));

        page.waitForTimeout(300);
        UiAssertions.assertNoDialog(dialogMessages);
        UiAssertions.assertNoSensitiveConsoleLeak(consoleMessages, List.of(
                InvalidInputs.UNICODE_HEBREW_TEXT,
                InvalidInputs.SPECIAL_CHARACTERS,
                input.email,
                input.phone
        ));
    }

    @Test
    public void loginFailuresDoNotExposeRawStatusCodesOrJsonPayloadsInUi() {
        UiAssertions.expectKnownIssue(KnownProductionIssues.LOGIN_ERROR_LEAK, () -> {
            LoginPage loginPage = new LoginPage(page);
            List<String> dialogMessages = UiAssertions.attachDialogCollector(page);

            loginPage.goTo();
            Response response = page.waitForResponse(
                    candidate -> candidate.url().contains("/api/member/login")
                            && "POST".equals(candidate.request().method()),
                    () -> loginPage.signInWithEmail("invalid@example.com", "wrong-password")
            );
            assertThat(response).isNotNull();
            loginPage.expectLoginFailureRendered();

            String bodyText = loginPage.visibleBodyText();
            UiAssertions.assertNoDialog(dialogMessages);
            assertThat(bodyText).doesNotContainPattern("401:");
            assertThat(bodyText).doesNotContain("{\"error\"");
        });
    }

    private ConsultationData validInput(ConsultationMockController controller) {
        return TestData.VALID_CONSULTATION_DATA.withDateAndTime(
                controller.fixtures().labels().dateLabel(),
                controller.fixtures().labels().timeLabel()
        );
    }
}
