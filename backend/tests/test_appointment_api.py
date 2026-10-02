from datetime import datetime

from fastapi.testclient import TestClient

from app.dependencies import get_db
from app.main import app
from app.models import Appointment, Service


def test_get_appointments_for_date_returns_enriched_appointments(
    db_session,
    business_and_staff,
):
    """
    Vérifie que l'API Agenda retourne les rendez-vous de la journée
    avec les informations du service et du professionnel.
    """
    business, staff_member = business_and_staff

    service = Service(
        business_id=business.id,
        name="Coupe femme",
        duration_minutes=45,
        price=35,
    )

    db_session.add(service)
    db_session.commit()
    db_session.refresh(service)

    appointment = Appointment(
        business_id=business.id,
        service_id=service.id,
        staff_member_id=staff_member.id,
        customer_name="Marie Dupont",
        customer_email="marie@example.com",
        customer_phone="0600000000",
        start_datetime=datetime(2026, 10, 2, 10, 0),
        end_datetime=datetime(2026, 10, 2, 10, 45),
        status="confirmed",
    )

    db_session.add(appointment)
    db_session.commit()
    db_session.refresh(appointment)

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            f"/businesses/{business.id}/appointments",
            params={"target_date": "2026-10-02"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["id"] == appointment.id
    assert data[0]["service_id"] == service.id
    assert data[0]["service_name"] == "Coupe femme"
    assert data[0]["staff_member_id"] == staff_member.id
    assert data[0]["staff_first_name"] == staff_member.first_name
    assert data[0]["staff_last_name"] == staff_member.last_name
    assert data[0]["customer_name"] == "Marie Dupont"
    assert data[0]["status"] == "confirmed"