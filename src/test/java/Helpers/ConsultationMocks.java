package Helpers;

import Extensions.JsonUtil;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.Route;

import java.net.URI;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public final class ConsultationMocks {
    private ConsultationMocks() {
    }

    public static ConsultationMockController mockConsultationApis(Page page) {
        return mockConsultationApis(page, new ConsultationMockOptions());
    }

    public static ConsultationMockController mockConsultationApis(Page page, ConsultationMockOptions options) {
        ConsultationMockFixtures fixtures = options.fixtures() == null
                ? TestData.buildMockConsultationFixtures()
                : options.fixtures();
        List<String> submittedPayloads = new ArrayList<>();

        page.route("**/api/states", route -> fulfillJson(route, fixtures.states()));
        page.route("**/api/consultation/specialized-needs", route -> fulfillJson(route, fixtures.specializedNeeds()));

        page.route("**/api/insurance-providers/state/**", route -> {
            String stateCode = lastPathSegment(route.request().url());
            fulfillJson(route, fixtures.insuranceProvidersByState().getOrDefault(stateCode, List.of()));
        });

        page.route("**/api/therapists/match**", route -> {
            delay(options.delayMatchMs());
            fulfillJson(route, fixtures.therapists());
        });

        page.route("**/api/calendar/availability/**", route -> {
            delay(options.delayAvailabilityMs());
            String availabilityKey = lastPathSegment(route.request().url());
            Map<String, Object> availability = fixtures.availabilityByTherapist().getOrDefault(
                    availabilityKey,
                    fixtures.availabilityByTherapist().getOrDefault("101", Map.of("slots", List.of()))
            );
            fulfillJson(route, availability);
        });

        page.route("**/api/consultations/fixed", route -> {
            String payload = route.request().postData();
            submittedPayloads.add(payload == null ? "" : payload);
            fulfillJson(route, fixtures.submitResponse());
        });

        return new ConsultationMockController(fixtures, submittedPayloads);
    }

    private static void fulfillJson(Route route, Object payload) {
        route.fulfill(new Route.FulfillOptions()
                .setStatus(200)
                .setContentType("application/json")
                .setBody(JsonUtil.toJson(payload)));
    }

    private static String lastPathSegment(String rawUrl) {
        String path = URI.create(rawUrl).getPath();
        int lastSlash = path.lastIndexOf('/');
        return lastSlash >= 0 ? path.substring(lastSlash + 1) : path;
    }

    private static void delay(int millis) {
        if (millis <= 0) {
            return;
        }
        try {
            Thread.sleep(millis);
        } catch (InterruptedException interrupted) {
            Thread.currentThread().interrupt();
            throw new IllegalStateException("Interrupted while delaying mocked route.", interrupted);
        }
    }
}
