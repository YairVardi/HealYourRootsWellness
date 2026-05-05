package SanityTest;

import Utilities.TestEnvironment;
import Helpers.KnownProductionIssues;
import Helpers.RouteExpectation;
import Helpers.TestData;
import Utilities.BaseTest;
import PageObjects.ContactPage;
import PageObjects.HomePage;
import Extensions.UiAssertions;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.assertions.PlaywrightAssertions;
import com.microsoft.playwright.options.AriaRole;
import com.microsoft.playwright.options.WaitUntilState;
import org.testng.annotations.Test;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.regex.Pattern;

import static org.assertj.core.api.Assertions.assertThat;

public class NavigationTest extends BaseTest {
    @Test
    public void homepageRendersHeaderFooterLogoAndMainNavigationLinks() {
        HomePage homePage = new HomePage(page);

        homePage.goTo();
        homePage.expectLoaded();

        PlaywrightAssertions.assertThat(homePage.header.findTherapistLink).isVisible();
        PlaywrightAssertions.assertThat(homePage.header.loginLink).isVisible();
        PlaywrightAssertions.assertThat(homePage.header.joinTherapistLink).isVisible();
    }

    @Test
    public void headerLinksAndLogoNavigateCorrectly() {
        HomePage homePage = new HomePage(page);
        ContactPage contactPage = new ContactPage(page);

        homePage.goTo();
        homePage.header.findTherapistLink.click();
        UiAssertions.assertUrlMatches(page, UiAssertions.regex("/find-a-therapist(?:$|[?#/])"));
        PlaywrightAssertions.assertThat(page.getByText(UiAssertions.regex("Find a Therapist")).first()).isVisible();

        homePage.goTo();
        homePage.header.loginLink.click();
        UiAssertions.assertUrlMatches(page, UiAssertions.regex("/dashboard/login(?:$|[?#/])"));
        PlaywrightAssertions.assertThat(page.getByText(UiAssertions.regex("Sign in to your therapist community account")).first()).isVisible();

        homePage.goTo();
        homePage.header.joinTherapistLink.click();
        UiAssertions.assertUrlMatches(page, UiAssertions.regex("/join(?:$|[?#/])"));
        PlaywrightAssertions.assertThat(page.getByText(UiAssertions.regex("Join the first 500 clinicians")).first()).isVisible();

        contactPage.goTo();
        homePage.header.logoLink.click();
        UiAssertions.assertUrlMatches(page, Pattern.compile("/$"));
    }

    @Test
    public void browserBackForwardAndRefreshPreserveRouteStability() {
        HomePage homePage = new HomePage(page);

        homePage.goTo();
        homePage.header.findTherapistLink.click();
        UiAssertions.assertUrlMatches(page, UiAssertions.regex("/find-a-therapist(?:$|[?#/])"));

        page.goBack();
        UiAssertions.assertUrlMatches(page, Pattern.compile("/$"));

        page.goForward();
        UiAssertions.assertUrlMatches(page, UiAssertions.regex("/find-a-therapist(?:$|[?#/])"));

        page.reload(new Page.ReloadOptions().setWaitUntil(WaitUntilState.DOMCONTENTLOADED));
        UiAssertions.assertPageHealthy(page);
        PlaywrightAssertions.assertThat(page.getByRole(
                AriaRole.HEADING,
                new Page.GetByRoleOptions().setName(UiAssertions.regex("Find a Therapist"))
        )).isVisible();
    }

    @Test
    public void importantPublicRoutesDoNotReturnHttp404Responses() throws Exception {
        HttpClient client = HttpClient.newBuilder()
                .followRedirects(HttpClient.Redirect.NORMAL)
                .build();

        for (String route : TestData.IMPORTANT_HTTP_ROUTES) {
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(TestEnvironment.absoluteUrl(route)))
                    .GET()
                    .build();
            HttpResponse<Void> response = client.send(request, HttpResponse.BodyHandlers.discarding());
            assertThat(response.statusCode())
                    .as("Unexpected HTTP 404 for %s", route)
                    .isNotEqualTo(404);
        }
    }

    @Test(timeOut = 120000)
    public void footerSupportLinksLoadRealContentPages() {
        for (RouteExpectation route : TestData.FOOTER_SUPPORT_PAGES) {
            if (route.knownIssue().isPresent()) {
                continue;
            }

            page.navigate(TestEnvironment.absoluteUrl(route.path()), new Page.NavigateOptions().setWaitUntil(WaitUntilState.DOMCONTENTLOADED));
            UiAssertions.assertPageHealthy(page);
            UiAssertions.assertUrlMatches(page, route.urlPattern());
            PlaywrightAssertions.assertThat(page.getByRole(
                    AriaRole.HEADING,
                    new Page.GetByRoleOptions().setName(route.heading())
            ).first()).isVisible();
        }
    }

    @Test
    public void footerSitemapLinkShouldNotLandOn404Page() {
        UiAssertions.expectKnownIssue(KnownProductionIssues.SITEMAP_FOOTER_LINK, () -> {
            RouteExpectation sitemapRoute = TestData.FOOTER_SUPPORT_PAGES.stream()
                    .filter(route -> "Sitemap".equals(route.label()))
                    .findFirst()
                    .orElseThrow(() -> new IllegalStateException("Sitemap route is missing from test data."));

            page.navigate(TestEnvironment.absoluteUrl(sitemapRoute.path()), new Page.NavigateOptions().setWaitUntil(WaitUntilState.DOMCONTENTLOADED));
            UiAssertions.assertPageHealthy(page);
            PlaywrightAssertions.assertThat(page.getByRole(
                    AriaRole.HEADING,
                    new Page.GetByRoleOptions().setName(sitemapRoute.heading())
            ).first()).isVisible();
        });
    }
}
