import pytest
from pydantic import ValidationError

from app.schemas import ServiceCreate

from fastapi.testclient import TestClient

from app.dependencies import get_db
from app.main import app
from app.models import Service


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


def test_delete_service(db_session, business_and_staff):
    business, _ = business_and_staff

    service = Service(
        business_id=business.id,
        name="Service à supprimer",
        duration_minutes=30,
        price=20,
        staff_assignment_mode="optional",
    )
    db_session.add(service)
    db_session.commit()
    db_session.refresh(service)

    service_id = service.id

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.delete(
            f"/businesses/{business.id}/services/{service_id}"
        )

        assert response.status_code == 204
        assert db_session.get(Service, service_id) is None
    finally:
        app.dependency_overrides.clear()