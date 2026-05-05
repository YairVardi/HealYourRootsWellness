package Helpers;

public final class ConsultationData {
    public final String serviceTypeLabel;
    public final String focusAreaLabel;
    public final String stateName;
    public final String stateCode;
    public final String hasInsuranceOptionLabel;
    public final String insuranceProviderLabel;
    public final String firstName;
    public final String lastName;
    public final String email;
    public final String phone;
    public final String therapistName;
    public final String dateLabel;
    public final String timeLabel;

    private ConsultationData(Builder builder) {
        this.serviceTypeLabel = builder.serviceTypeLabel;
        this.focusAreaLabel = builder.focusAreaLabel;
        this.stateName = builder.stateName;
        this.stateCode = builder.stateCode;
        this.hasInsuranceOptionLabel = builder.hasInsuranceOptionLabel;
        this.insuranceProviderLabel = builder.insuranceProviderLabel;
        this.firstName = builder.firstName;
        this.lastName = builder.lastName;
        this.email = builder.email;
        this.phone = builder.phone;
        this.therapistName = builder.therapistName;
        this.dateLabel = builder.dateLabel;
        this.timeLabel = builder.timeLabel;
    }

    public ConsultationData withDateAndTime(String dateLabel, String timeLabel) {
        return toBuilder().dateLabel(dateLabel).timeLabel(timeLabel).build();
    }

    public ConsultationData withPersonalDetails(
            String firstName,
            String lastName,
            String email,
            String phone
    ) {
        return toBuilder()
                .firstName(firstName)
                .lastName(lastName)
                .email(email)
                .phone(phone)
                .build();
    }

    public Builder toBuilder() {
        return new Builder()
                .serviceTypeLabel(serviceTypeLabel)
                .focusAreaLabel(focusAreaLabel)
                .stateName(stateName)
                .stateCode(stateCode)
                .hasInsuranceOptionLabel(hasInsuranceOptionLabel)
                .insuranceProviderLabel(insuranceProviderLabel)
                .firstName(firstName)
                .lastName(lastName)
                .email(email)
                .phone(phone)
                .therapistName(therapistName)
                .dateLabel(dateLabel)
                .timeLabel(timeLabel);
    }

    public static final class Builder {
        private String serviceTypeLabel;
        private String focusAreaLabel;
        private String stateName;
        private String stateCode;
        private String hasInsuranceOptionLabel;
        private String insuranceProviderLabel;
        private String firstName;
        private String lastName;
        private String email;
        private String phone;
        private String therapistName;
        private String dateLabel;
        private String timeLabel;

        public Builder serviceTypeLabel(String serviceTypeLabel) {
            this.serviceTypeLabel = serviceTypeLabel;
            return this;
        }

        public Builder focusAreaLabel(String focusAreaLabel) {
            this.focusAreaLabel = focusAreaLabel;
            return this;
        }

        public Builder stateName(String stateName) {
            this.stateName = stateName;
            return this;
        }

        public Builder stateCode(String stateCode) {
            this.stateCode = stateCode;
            return this;
        }

        public Builder hasInsuranceOptionLabel(String hasInsuranceOptionLabel) {
            this.hasInsuranceOptionLabel = hasInsuranceOptionLabel;
            return this;
        }

        public Builder insuranceProviderLabel(String insuranceProviderLabel) {
            this.insuranceProviderLabel = insuranceProviderLabel;
            return this;
        }

        public Builder firstName(String firstName) {
            this.firstName = firstName;
            return this;
        }

        public Builder lastName(String lastName) {
            this.lastName = lastName;
            return this;
        }

        public Builder email(String email) {
            this.email = email;
            return this;
        }

        public Builder phone(String phone) {
            this.phone = phone;
            return this;
        }

        public Builder therapistName(String therapistName) {
            this.therapistName = therapistName;
            return this;
        }

        public Builder dateLabel(String dateLabel) {
            this.dateLabel = dateLabel;
            return this;
        }

        public Builder timeLabel(String timeLabel) {
            this.timeLabel = timeLabel;
            return this;
        }

        public ConsultationData build() {
            return new ConsultationData(this);
        }
    }
}
