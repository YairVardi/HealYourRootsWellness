from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Any


@dataclass(frozen=True)
class ConsultationData:
    service_type_label: str
    focus_area_label: str | None
    state_name: str
    state_code: str
    has_insurance_option_label: str
    insurance_provider_label: str | None
    first_name: str
    last_name: str
    email: str
    phone: str
    therapist_name: str
    date_label: str | None = None
    time_label: str | None = None

    def with_date_and_time(self, date_label: str, time_label: str) -> "ConsultationData":
        return replace(self, date_label=date_label, time_label=time_label)

    def with_personal_details(
        self, first_name: str, last_name: str, email: str, phone: str
    ) -> "ConsultationData":
        return replace(
            self,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
        )


@dataclass(frozen=True)
class RegisterMemberRequest:
    first_name: str
    last_name: str
    email: str
    password: str
    confirm_password: str
    credentials: str
    license_number: str
    license_state: str

    def to_dict(self) -> dict[str, Any]:
        snake_case = asdict(self)
        keys = {
            "first_name": "firstName",
            "last_name": "lastName",
            "confirm_password": "confirmPassword",
            "license_number": "licenseNumber",
            "license_state": "licenseState",
        }
        return {keys.get(key, key): value for key, value in snake_case.items() if value is not None}
