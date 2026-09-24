import pytest
from pydantic import ValidationError

from app.schemas import ServiceCreate


def test_service_assignment_mode_defaults_to_optional():
    service = ServiceCreate(
        name="Coupe femme",
        duration_minutes=45,
        price=35,
    )

    assert service.staff_assignment_mode == "optional"


def test_service_assignment_mode_rejects_invalid_value():
    with pytest.raises(ValidationError):
        ServiceCreate(
            name="Coupe femme",
            duration_minutes=45,
            price=35,
            staff_assignment_mode="random",
        )


@pytest.mark.parametrize(
    "assignment_mode",
    [
        "customer_choice",
        "automatic",
        "optional",
    ],
)
def test_service_accepts_valid_assignment_modes(assignment_mode):
    service = ServiceCreate(
        name="Coupe femme",
        duration_minutes=45,
        price=35,
        staff_assignment_mode=assignment_mode,
    )

    assert service.staff_assignment_mode == assignment_mode