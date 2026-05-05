package Helpers;

import java.util.List;

public final class ConsultationMockController {
    private final ConsultationMockFixtures fixtures;
    private final List<String> submittedPayloads;

    public ConsultationMockController(ConsultationMockFixtures fixtures, List<String> submittedPayloads) {
        this.fixtures = fixtures;
        this.submittedPayloads = submittedPayloads;
    }

    public ConsultationMockFixtures fixtures() {
        return fixtures;
    }

    public List<String> submittedPayloads() {
        return submittedPayloads;
    }
}
