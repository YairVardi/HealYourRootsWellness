package Helpers;

import Helpers.ConsultationMockFixtures;

public final class ConsultationMockOptions {
    private ConsultationMockFixtures fixtures;
    private int delayMatchMs;
    private int delayAvailabilityMs;

    public ConsultationMockFixtures fixtures() {
        return fixtures;
    }

    public int delayMatchMs() {
        return delayMatchMs;
    }

    public int delayAvailabilityMs() {
        return delayAvailabilityMs;
    }

    public ConsultationMockOptions fixtures(ConsultationMockFixtures fixtures) {
        this.fixtures = fixtures;
        return this;
    }

    public ConsultationMockOptions delayMatchMs(int delayMatchMs) {
        this.delayMatchMs = delayMatchMs;
        return this;
    }

    public ConsultationMockOptions delayAvailabilityMs(int delayAvailabilityMs) {
        this.delayAvailabilityMs = delayAvailabilityMs;
        return this;
    }
}
