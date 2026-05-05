package SanityTest;

import Helpers.ConsultationData;
import Helpers.KnownProductionIssues;
import Helpers.RouteExpectation;
import Helpers.TestData;
import Utilities.BaseTest;
import PageObjects.ClientPage;
import PageObjects.ConsultationPage;
import PageObjects.ContactPage;
import PageObjects.FAQPage;
import PageObjects.HomePage;
import Helpers.ConsultationMockController;
import Helpers.ConsultationMocks;
import Extensions.UiAssertions;
import com.microsoft.playwright.assertions.PlaywrightAssertions;
import com.microsoft.playwright.options.AriaRole;
import org.testng.annotations.Test;

import java.util.List;
import java.util.Map;

import static org.assertj.core.api.Assertions.assertThat;

public class ClientFlowTest extends BaseTest {
    @Test
    public void homepageLoadsAndExposesPatientFacingEntryPoints() {
        HomePage homePage = new HomePage(page);

        homePage.goTo();
        homePage.expectLoaded();

        PlaywrightAssertions.assertThat(homePage.scheduleConsultLink).isVisible();
        PlaywrightAssertions.assertThat(homePage.header.findTherapistLink).isVisible();
    }

    @Test(timeOut = 180000)
    public void clientJourneyRoutesStayInsidePublicPatientFacingPages() {
        ClientPage clientPage = new ClientPage(page);

        for (RouteExpectation route : TestData.CLIENT_JOURNEY_PAGES) {
            if (route.knownIssue().isPresent()) {
                continue;
            }

            clientPage.goToRoute(route.path());
            clientPage.expectHealthy();
            UiAssertions.assertUrlMatches(page, route.urlPattern());
            PlaywrightAssertions.assertThat(page.getByRole(
                    AriaRole.HEADING,
                    new com.microsoft.playwright.Page.GetByRoleOptions().setName(route.heading())
            ).first()).isVisible();
            assertThat(page.url()).doesNotContain("/dashboard", "/join", "/for-clinicians", "/group-practice");
        }
    }

    @Test
    public void faqRouteShouldRenderFaqContentInsteadOfGlobalErrorBoundary() {
        UiAssertions.expectKnownIssue(KnownProductionIssues.FAQ_ROUTE, () -> {
            FAQPage faqPage = new FAQPage(page);
            faqPage.goTo();
            faqPage.expectLoaded();
        });
    }

    @Test
    public void contactPageBookNowCtaLeadsIntoConsultationFlow() {
        ContactPage contactPage = new ContactPage(page);

        contactPage.goTo();
        contactPage.expectLoaded();
        contactPage.openConsultation();

        UiAssertions.assertUrlMatches(page, UiAssertions.regex("/consultation(?:$|[?#/])"));
        PlaywrightAssertions.assertThat(page.getByRole(
                AriaRole.HEADING,
                new com.microsoft.playwright.Page.GetByRoleOptions()
                        .setName(UiAssertions.regex("Schedule Your Free Consultation"))
        )).isVisible();
    }

    @Test
    public void clientCtaDoesNotRedirectIntoTherapistOnlyAreasUnderRapidClicks() {
        HomePage homePage = new HomePage(page);

        homePage.goTo();
        homePage.primaryClientCta.evaluate("element => { element.click(); element.click(); element.click(); }");

        UiAssertions.assertUrlMatches(page, UiAssertions.regex("/find-a-therapist(?:$|[?#/])"));
        assertThat(page.url()).doesNotContain("/dashboard", "/join", "/for-clinicians", "/group-practice");
    }

    @Test
    public void consultationHappyPathCompletesSafelyWithMockedProductionApis() {
        ConsultationMockController controller = ConsultationMocks.mockConsultationApis(page);
        ConsultationData input = TestData.VALID_CONSULTATION_DATA.withDateAndTime(
                controller.fixtures().labels().dateLabel(),
                controller.fixtures().labels().timeLabel()
        );
        ConsultationPage consultationPage = new ConsultationPage(page);

        consultationPage.goTo();
        consultationPage.completeHappyPath(input);
        consultationPage.expectConfirmation(input.firstName);

        assertThat(controller.submittedPayloads()).hasSize(1);
        String payload = controller.submittedPayloads().get(0);
        @SuppressWarnings("unchecked")
        List<Map<String, Object>> primarySlots =
                (List<Map<String, Object>>) controller.fixtures().availabilityByTherapist().get("101").get("slots");
        String selectedDateTime = String.valueOf(primarySlots.get(0).get("start"));

        assertThat(payload)
                .contains(input.firstName)
                .contains(input.lastName)
                .contains(input.email)
                .contains(input.phone)
                .contains(input.stateCode)
                .contains("individual")
                .contains("101")
                .contains(selectedDateTime);
    }
}
