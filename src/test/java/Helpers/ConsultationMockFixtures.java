package Helpers;

import java.util.List;
import java.util.Map;

public final class ConsultationMockFixtures {
    private final List<Map<String, Object>> states;
    private final List<Map<String, Object>> specializedNeeds;
    private final Map<String, List<Map<String, Object>>> insuranceProvidersByState;
    private final List<Map<String, Object>> therapists;
    private final Map<String, Map<String, Object>> availabilityByTherapist;
    private final Map<String, Object> submitResponse;
    private final ConsultationLabels labels;

    public ConsultationMockFixtures(
            List<Map<String, Object>> states,
            List<Map<String, Object>> specializedNeeds,
            Map<String, List<Map<String, Object>>> insuranceProvidersByState,
            List<Map<String, Object>> therapists,
            Map<String, Map<String, Object>> availabilityByTherapist,
            Map<String, Object> submitResponse,
            ConsultationLabels labels
    ) {
        this.states = states;
        this.specializedNeeds = specializedNeeds;
        this.insuranceProvidersByState = insuranceProvidersByState;
        this.therapists = therapists;
        this.availabilityByTherapist = availabilityByTherapist;
        this.submitResponse = submitResponse;
        this.labels = labels;
    }

    public List<Map<String, Object>> states() {
        return states;
    }

    public List<Map<String, Object>> specializedNeeds() {
        return specializedNeeds;
    }

    public Map<String, List<Map<String, Object>>> insuranceProvidersByState() {
        return insuranceProvidersByState;
    }

    public List<Map<String, Object>> therapists() {
        return therapists;
    }

    public Map<String, Map<String, Object>> availabilityByTherapist() {
        return availabilityByTherapist;
    }

    public Map<String, Object> submitResponse() {
        return submitResponse;
    }

    public ConsultationLabels labels() {
        return labels;
    }

    public static final class ConsultationLabels {
        private final String dateLabel;
        private final String timeLabel;

        public ConsultationLabels(String dateLabel, String timeLabel) {
            this.dateLabel = dateLabel;
            this.timeLabel = timeLabel;
        }

        public String dateLabel() {
            return dateLabel;
        }

        public String timeLabel() {
            return timeLabel;
        }
    }
}
