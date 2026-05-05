package SanityTest;

import Utilities.TestEnvironment;
import Helpers.KnownProductionIssues;
import Helpers.RouteExpectation;
import Helpers.TestData;
import Utilities.BaseTest;
import PageObjects.DashboardPage;
import PageObjects.HomePage;
import PageObjects.LoginPage;
import PageObjects.TherapistPage;
import Extensions.UiAssertions;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.Response;
import com.microsoft.playwright.assertions.PlaywrightAssertions;
import com.microsoft.playwright.options.WaitUntilState;
import org.testng.annotations.Test;


import static org.assertj.core.api.Assertions.assertThat;

public class TherapistFlowTest extends BaseTest {
    @Test
    public void therapistCtaExistsAndRedirectsToClinicianLandingPage() {
        HomePage homePage = new HomePage(page);
        TherapistPage therapistPage = new TherapistPage(page);

        homePage.goTo();
        PlaywrightAssertions.assertThat(homePage.primaryTherapistCta).isVisible();
        PlaywrightAssertions.assertThat(homePage.primaryTherapistCta).hasAttribute("href", "/for-clinicians");

        homePage.primaryTherapistCta.focus();
        page.keyboard().press("Enter");

        therapistPage.expectClinicianLandingLoaded();
        UiAssertions.assertUrlMatches(page, UiAssertions.regex("/for-clinicians(?:$|[?#/])"));
    }

    @Test(timeOut = 180000)
    public void therapistRoutesStayOutOfClientBookingFlow() {
        TherapistPage therapistPage = new TherapistPage(page);

        for (RouteExpectation route : TestData.THERAPIST_JOURNEY_PAGES) {
            page.navigate(TestEnvironment.absoluteUrl(route.path()), new Page.NavigateOptions().setWaitUntil(WaitUntilState.DOMCONTENTLOADED));
            therapistPage.expectHealthy();
            UiAssertions.assertUrlMatches(page, route.urlPattern());
            PlaywrightAssertions.assertThat(page.getByText(route.heading()).first()).isVisible();
            assertThat(page.url()).doesNotContain("/find-a-therapist", "/consultation", "/schedule");
        }
    }

    @Test
    public void unauthenticatedUsersCannotAccessMemberDashboardDirectly() {
        DashboardPage dashboardPage = new DashboardPage(page);

        dashboardPage.goTo();
        dashboardPage.expectProtectedRedirect();
    }

    @Test
    public void loginErrorsAvoidExposingRawTransportDetailsInUi() {
        UiAssertions.expectKnownIssue(KnownProductionIssues.LOGIN_ERROR_LEAK, () -> {
            LoginPage loginPage = new LoginPage(page);

            loginPage.goTo();
            loginPage.expectLoaded();
            UiAssertions.assertHttps(page);
            Response response = page.waitForResponse(
                    candidate -> candidate.url().contains("/api/member/login")
                            && "POST".equals(candidate.request().method()),
                    () -> loginPage.signInWithEmail("invalid@example.com", "wrong-password")
            );
            assertThat(response).isNotNull();
            loginPage.expectLoginFailureRendered();

            String bodyText = loginPage.visibleBodyText();
            assertThat(bodyText).doesNotContainPattern("401:");
            assertThat(bodyText).doesNotContain("{\"error\"");
        });
    }
}
