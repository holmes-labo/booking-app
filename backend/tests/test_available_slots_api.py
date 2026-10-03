from datetime import time

from fastapi.testclient import TestClient

from app.dependencies import get_db
from app.main import app
from app.models import Availability, Service, StaffMember, StaffService, OpeningHour

def test_customer_choice_requires_staff_member_for_available_slots(
    db_session,
    business_and_staff,
):
    business, staff_member = business_and_staff

    service = Service(
        business_id=business.id,
        name="Coupe femme",
        duration_minutes=45,
        price=35,
        staff_assignment_mode="customer_choice",
    )

    db_session.add(service)
    db_session.commit()
    db_session.refresh(service)

    staff_service = StaffService(
        staff_member_id=staff_member.id,
        service_id=service.id,
    )

    availability = Availability(
        business_id=business.id,
        staff_member_id=staff_member.id,
        weekday=0,
        start_time=time(9, 0),
        end_time=time(18, 0),
    )

    opening_hour = OpeningHour(
        business_id=business.id,
        weekday=0,
        start_time=time(9, 0),
        end_time=time(10, 0),
    )

    db_session.add_all([
        staff_service,
        availability,
        opening_hour,
    ])
    db_session.commit()

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            f"/businesses/{business.id}/appointments/available-slots",
            params={
                "service_id": service.id,
                "target_date": "2026-09-28",
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 422
    assert response.json() == {
        "detail": "A staff member must be selected for this service"
    }


def test_automatic_mode_rejects_staff_member_for_available_slots(
    db_session,
    business_and_staff,
):
    business, staff_member = business_and_staff

    service = Service(
        business_id=business.id,
        name="Coupe femme",
        duration_minutes=45,
        price=35,
        staff_assignment_mode="automatic",
    )

    db_session.add(service)
    db_session.commit()
    db_session.refresh(service)

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            f"/businesses/{business.id}/appointments/available-slots",
            params={
                "service_id": service.id,
                "target_date": "2026-09-28",
                "staff_member_id": staff_member.id,
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 422
    assert response.json() == {
        "detail": "A staff member cannot be selected for this service"
    }


def test_optional_mode_returns_available_slots_without_staff_choice(
    db_session,
    business_and_staff,
):
    business, staff_member = business_and_staff

    service = Service(
        business_id=business.id,
        name="Coupe femme",
        duration_minutes=45,
        price=35,
        staff_assignment_mode="optional",
    )

    db_session.add(service)
    db_session.commit()
    db_session.refresh(service)

    staff_service = StaffService(
        staff_member_id=staff_member.id,
        service_id=service.id,
    )

    availability = Availability(
        business_id=business.id,
        staff_member_id=staff_member.id,
        weekday=0,
        start_time=time(9, 0),
        end_time=time(10, 0),
    )

    opening_hour = OpeningHour(
        business_id=business.id,
        weekday=0,
        start_time=time(9, 0),
        end_time=time(10, 0),
    )

    db_session.add_all([
        staff_service,
        availability,
        opening_hour,
    ])
    db_session.commit()

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            f"/businesses/{business.id}/appointments/available-slots",
            params={
                "service_id": service.id,
                "target_date": "2026-09-28",
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200

    assert response.json() == [
        {
            "start_datetime": "2026-09-28T09:00:00",
            "end_datetime": "2026-09-28T09:45:00",
            "staff_member_id": staff_member.id,
        },
        {
            "start_datetime": "2026-09-28T09:15:00",
            "end_datetime": "2026-09-28T10:00:00",
            "staff_member_id": staff_member.id,
        },
    ]


def test_automatic_mode_deduplicates_slots_and_hides_staff_member(
    db_session,
    business_and_staff,
):
    business, first_staff_member = business_and_staff

    second_staff_member = StaffMember(
        business_id=business.id,
        first_name="Léa",
        active=True,
    )

    service = Service(
        business_id=business.id,
        name="Coupe femme",
        duration_minutes=45,
        price=35,
        staff_assignment_mode="automatic",
    )

    db_session.add_all([second_staff_member, service])
    db_session.commit()
    db_session.refresh(second_staff_member)
    db_session.refresh(service)

    db_session.add_all(
        [
            StaffService(
                staff_member_id=first_staff_member.id,
                service_id=service.id,
            ),
            StaffService(
                staff_member_id=second_staff_member.id,
                service_id=service.id,
            ),
            Availability(
                business_id=business.id,
                staff_member_id=first_staff_member.id,
                weekday=0,
                start_time=time(9, 0),
                end_time=time(10, 0),
            ),
            Availability(
                business_id=business.id,
                staff_member_id=second_staff_member.id,
                weekday=0,
                start_time=time(9, 0),
                end_time=time(10, 0),
            ),
            OpeningHour(
                business_id=business.id,
                weekday=0,
                start_time=time(9, 0),
                end_time=time(10, 0),
            ),
        ]
    )
    db_session.commit()

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            f"/businesses/{business.id}/appointments/available-slots",
            params={
                "service_id": service.id,
                "target_date": "2026-09-28",
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == [
        {
            "start_datetime": "2026-09-28T09:00:00",
            "end_datetime": "2026-09-28T09:45:00",
            "staff_member_id": None,
        },
        {
            "start_datetime": "2026-09-28T09:15:00",
            "end_datetime": "2026-09-28T10:00:00",
            "staff_member_id": None,
        },
    ]


def test_booked_slot_is_no_longer_available(
    db_session,
    business_and_staff,
):
    business, staff_member = business_and_staff

    service = Service(
        business_id=business.id,
        name="Coupe femme",
        duration_minutes=45,
        price=35,
        staff_assignment_mode="optional",
    )

    db_session.add(service)
    db_session.commit()
    db_session.refresh(service)

    db_session.add_all(
        [
            StaffService(
                staff_member_id=staff_member.id,
                service_id=service.id,
            ),
            Availability(
                business_id=business.id,
                staff_member_id=staff_member.id,
                weekday=0,
                start_time=time(9, 0),
                end_time=time(11, 0),
            ),
            OpeningHour(
                business_id=business.id,
                weekday=0,
                start_time=time(9, 0),
                end_time=time(11, 0),
            ),
        ]
    )
    db_session.commit()

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        slots_url = (
            f"/businesses/{business.id}/appointments/available-slots"
        )

        response_before = client.get(
            slots_url,
            params={
                "service_id": service.id,
                "target_date": "2026-09-28",
                "staff_member_id": staff_member.id,
            },
        )

        assert response_before.status_code == 200
        assert any(
            slot["start_datetime"] == "2026-09-28T09:00:00"
            for slot in response_before.json()
        )

        booking_response = client.post(
            f"/businesses/{business.id}/appointments",
            json={
                "service_id": service.id,
                "staff_member_id": staff_member.id,
                "customer_name": "Marie Dupont",
                "customer_email": "marie@example.com",
                "customer_phone": "0600000000",
                "start_datetime": "2026-09-28T09:00:00",
            },
        )

        assert booking_response.status_code == 200

        response_after = client.get(
            slots_url,
            params={
                "service_id": service.id,
                "target_date": "2026-09-28",
                "staff_member_id": staff_member.id,
            },
        )

        assert response_after.status_code == 200
        assert not any(
            slot["start_datetime"] == "2026-09-28T09:00:00"
            for slot in response_after.json()
        )

    finally:
        app.dependency_overrides.clear()