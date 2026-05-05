package SanityTest;

import Helpers.TestData;
import Utilities.BaseTest;
import PageObjects.ConsultationPage;
import PageObjects.HomePage;
import Extensions.UiAssertions;
import com.microsoft.playwright.assertions.PlaywrightAssertions;
import com.microsoft.playwright.options.AriaRole;
import org.testng.annotations.Test;

public class ResponsiveTest extends BaseTest {
    @Test
    public void mobileHamburgerMenuOpensAndClosesWithClientAndTherapistLinks() {
        HomePage homePage = new HomePage(page);

        page.setViewportSize(390, 844);
        homePage.goTo();

        PlaywrightAssertions.assertThat(homePage.header.navigationMenu.menuToggle).isVisible();
        homePage.header.navigationMenu.openMobileMenu();
        PlaywrightAssertions.assertThat(homePage.header.navigationMenu.link(UiAssertions.regex("Find a Therapist"))).isVisible();
        PlaywrightAssertions.assertThat(homePage.header.navigationMenu.link(UiAssertions.regex("Join as a Therapist"))).isVisible();
        PlaywrightAssertions.assertThat(homePage.header.navigationMenu.link(UiAssertions.regex("^Login$"))).isVisible();
        homePage.header.navigationMenu.closeMobileMenu();
    }

    @Test
    public void mobileCtasStayTappableAndHeroLayoutAvoidsOverlap() {
        HomePage homePage = new HomePage(page);

        page.setViewportSize(390, 844);
        homePage.goTo();

        UiAssertions.assertNoHorizontalOverflow(page);
        PlaywrightAssertions.assertThat(homePage.primaryClientCta).isVisible();
        PlaywrightAssertions.assertThat(homePage.primaryTherapistCta).isVisible();
        UiAssertions.assertElementsDoNotOverlap(homePage.primaryClientCta, homePage.primaryTherapistCta);

        homePage.primaryClientCta.click();
        UiAssertions.assertUrlMatches(page, UiAssertions.regex("/find-a-therapist(?:$|[?#/])"));
    }

    @Test
    public void tabletPortraitAndLandscapeViewportsKeepConsultationEntryUsable() {
        ConsultationPage consultationPage = new ConsultationPage(page);

        validateConsultationViewport(consultationPage, 768, 1024);
        validateConsultationViewport(consultationPage, 1024, 768);
    }

    private void validateConsultationViewport(ConsultationPage consultationPage, int width, int height) {
        page.setViewportSize(width, height);
        consultationPage.goTo();
        consultationPage.expectLoaded();
        consultationPage.selectServiceType(TestData.VALID_CONSULTATION_DATA.serviceTypeLabel);
        PlaywrightAssertions.assertThat(consultationPage.nextButton).isEnabled();
        UiAssertions.assertNoHorizontalOverflow(page);
        PlaywrightAssertions.assertThat(page.getByRole(
                AriaRole.BUTTON,
                new com.microsoft.playwright.Page.GetByRoleOptions().setName(UiAssertions.regex("^Next$"))
        )).isVisible();
    }
}
