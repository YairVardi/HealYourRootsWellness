package Helpers;

import java.time.Instant;
import java.time.LocalDate;
import java.time.LocalTime;
import java.time.ZoneId;
import java.time.ZoneOffset;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.regex.Pattern;

public final class TestData {
    private static final int FLAGS = Pattern.CASE_INSENSITIVE;

    public static final List<RouteExpectation> CLIENT_JOURNEY_PAGES = List.of(
            route("Find a Therapist", "/find-a-therapist", "Find a Therapist", "/find-a-therapist(?:$|[/?#])"),
            route("Services", "/services", "Telehealth Therapy|Services", "/(services|telehealth-therapy)(?:$|[/?#])"),
            route("Specialties", "/specialties", "Our Therapy Specialties|Specialties", "/specialties(?:$|[/?#])"),
            route("Telehealth Therapy", "/telehealth-therapy", "Telehealth Therapy", "/telehealth-therapy(?:$|[/?#])"),
            route("Locations", "/locations", "Our Locations|Locations", "/locations(?:$|[/?#])"),
            route("Insurance & Pricing", "/insurance", "Insurance", "/insurance(?:$|[/?#])"),
            new RouteExpectation(
                    "FAQ",
                    "/faq",
                    Pattern.compile("Frequently Asked Questions|FAQ", FLAGS),
                    Pattern.compile("/faq(?:$|[/?#])", FLAGS),
                    KnownProductionIssues.FAQ_ROUTE
            ),
            route("Contact / Book Consultation", "/contact", "Contact", "/contact(?:$|[/?#])")
    );

    public static final List<RouteExpectation> THERAPIST_JOURNEY_PAGES = List.of(
            route("Why Join", "/for-clinicians", "For Clinicians", "/for-clinicians(?:$|[/?#])"),
            route("Join the Network", "/join", "Join the first 500 clinicians", "/join(?:$|[/?#])"),
            route("Group Practice Plans", "/group-practice", "One subscription for the whole practice", "/group-practice(?:$|[/?#])"),
            route("Member Login", "/dashboard/login", "Sign in to your therapist community account", "/dashboard/login(?:$|[/?#])")
    );

    public static final List<RouteExpectation> FOOTER_SUPPORT_PAGES = List.of(
            route("Privacy Policy", "/privacy-policy", "Privacy Policy", "/privacy-policy(?:$|[/?#])"),
            route("Terms of Service", "/terms-of-service", "Terms of Service", "/terms-of-service(?:$|[/?#])"),
            route("Accessibility", "/accessibility", "Accessibility", "/accessibility(?:$|[/?#])"),
            new RouteExpectation(
                    "Sitemap",
                    "/sitemap",
                    Pattern.compile("Sitemap", FLAGS),
                    Pattern.compile("/sitemap(?:$|[/?#])", FLAGS),
                    KnownProductionIssues.SITEMAP_FOOTER_LINK
            )
    );

    public static final List<String> IMPORTANT_HTTP_ROUTES = List.of(
            "/",
            "/find-a-therapist",
            "/contact",
            "/consultation",
            "/join",
            "/for-clinicians",
            "/dashboard/login",
            "/privacy-policy",
            "/terms-of-service",
            "/accessibility"
    );

    public static final ConsultationData VALID_CONSULTATION_DATA = new ConsultationData.Builder()
            .serviceTypeLabel("Individual Therapy")
            .focusAreaLabel("Anxiety")
            .stateName("Pennsylvania")
            .stateCode("PA")
            .hasInsuranceOptionLabel("Yes, I have insurance")
            .insuranceProviderLabel("Aetna")
            .firstName("QA")
            .lastName("Automation")
            .email("qa.automation+hyr@example.com")
            .phone("5551234567")
            .therapistName("Dr. Avery Cole")
            .build();

    private TestData() {
    }

    public static ConsultationMockFixtures buildMockConsultationFixtures() {
        LocalDate appointmentDay = nextBusinessDay(LocalDate.now());
        String primarySlot = buildIsoSlot(appointmentDay, 14, 0);
        String backupSlot = buildIsoSlot(appointmentDay, 14, 30);

        return new ConsultationMockFixtures(
                List.of(
                        Map.of("id", 1, "name", "Pennsylvania", "abbreviation", "PA", "isActive", true),
                        Map.of("id", 2, "name", "Florida", "abbreviation", "FL", "isActive", true),
                        Map.of("id", 3, "name", "New York", "abbreviation", "NY", "isActive", false)
                ),
                List.of(
                        Map.of(
                                "id", 1,
                                "optionValue", "anxiety",
                                "optionLabel", "Anxiety",
                                "description", "Support for worry, panic, and day-to-day stress.",
                                "isActive", true
                        ),
                        Map.of(
                                "id", 2,
                                "optionValue", "trauma",
                                "optionLabel", "Trauma",
                                "description", "Trauma-informed care for processing difficult experiences.",
                                "isActive", true
                        ),
                        Map.of(
                                "id", 3,
                                "optionValue", "relationship-issues",
                                "optionLabel", "Relationship Issues",
                                "description", "Communication, conflict, and attachment support.",
                                "isActive", true
                        )
                ),
                Map.of(
                        "PA", List.of(
                                Map.of("id", 11, "name", "Aetna", "type", "commercial", "isActive", true),
                                Map.of("id", 12, "name", "Legacy Health Plan", "type", "commercial", "isActive", false)
                        ),
                        "FL", List.of(Map.of("id", 21, "name", "Self Pay Only", "type", "self_pay", "isActive", false))
                ),
                List.of(
                        Map.of("id", 101, "name", "Dr. Avery Cole", "specialties", List.of("Anxiety", "Trauma")),
                        Map.of("id", 102, "name", "Jordan Patel, LPC", "specialties", List.of("Relationship Issues"))
                ),
                Map.of(
                        "101", Map.of("slots", List.of(
                                Map.of("start", primarySlot, "available", true),
                                Map.of("start", backupSlot, "available", true)
                        )),
                        "102", Map.of("slots", List.of(Map.of("start", backupSlot, "available", true)))
                ),
                Map.of("id", 9001, "status", "scheduled"),
                new ConsultationMockFixtures.ConsultationLabels(toDateLabel(appointmentDay), toTimeLabel(primarySlot))
        );
    }

    private static RouteExpectation route(String label, String path, String heading, String urlPattern) {
        return new RouteExpectation(
                label,
                path,
                Pattern.compile(heading, FLAGS),
                Pattern.compile(urlPattern, FLAGS)
        );
    }

    private static LocalDate nextBusinessDay(LocalDate baseDate) {
        LocalDate candidate = baseDate.plusDays(1);
        while (candidate.getDayOfWeek().getValue() >= 6) {
            candidate = candidate.plusDays(1);
        }
        return candidate;
    }

    private static String toTimeLabel(String isoDate) {
        return DateTimeFormatter.ofPattern("h:mm a", Locale.US)
                .withZone(ZoneId.of("America/New_York"))
                .format(Instant.parse(isoDate));
    }

    private static String toDateLabel(LocalDate date) {
        LocalDate today = LocalDate.now();
        if (date.equals(today)) {
            return "Today";
        }
        if (date.equals(today.plusDays(1))) {
            return "Tomorrow";
        }
        return DateTimeFormatter.ofPattern("EEE, MMM d", Locale.US).format(date);
    }

    private static String buildIsoSlot(LocalDate date, int hourUtc, int minuteUtc) {
        return ZonedDateTime.of(date, LocalTime.of(hourUtc, minuteUtc), ZoneOffset.UTC)
                .toInstant()
                .toString();
    }
}
