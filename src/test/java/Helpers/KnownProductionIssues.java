package Helpers;

public final class KnownProductionIssues {
    public static final String FAQ_ROUTE =
            "The public FAQ route currently falls into the global error boundary.";
    public static final String SITEMAP_FOOTER_LINK =
            "The footer sitemap link currently lands on a 404 page.";
    public static final String LOGIN_ERROR_LEAK =
            "Invalid login currently exposes raw 401 JSON in the UI.";
    public static final String INVALID_EMAIL_VALIDATION =
            "The current client flow only checks that the email field is non-empty before enabling Next.";
    public static final String DUPLICATE_CONSULTATION_SUBMIT =
            "Rapid clicks on Schedule Consultation currently create duplicate consultation requests.";

    private KnownProductionIssues() {
    }
}
