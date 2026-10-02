from fastapi.testclient import TestClient

from app.dependencies import get_db
from app.main import app


from datetime import date, datetime

from app.models import Appointment, Service

from app.services.dashboard_service import (
    count_appointments_for_date,
    count_clients_for_date,
    get_booked_minutes_for_date,
    get_occupancy_rate_for_date,
    get_revenue_for_date,
)

from app.services.capacity_service import (
    get_available_minutes_for_date,
    get_scheduled_minutes_for_date,
    get_staff_absences_for_date,
    subtract_absence_from_intervals,
)



def test_count_appointments_for_date(
    db_session,
    business_and_staff,
):
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

    appointments = [
        Appointment(
            business_id=business.id,
            service_id=service.id,
            staff_member_id=staff_member.id,
            customer_name="Client 1",
            customer_email="client1@example.com",
            start_datetime=datetime(2026, 9, 30, 9, 0),
            end_datetime=datetime(2026, 9, 30, 9, 45),
            status="confirmed",
        ),
        Appointment(
            business_id=business.id,
            service_id=service.id,
            staff_member_id=staff_member.id,
            customer_name="Client 2",
            customer_email="client2@example.com",
            start_datetime=datetime(2026, 9, 30, 14, 0),
            end_datetime=datetime(2026, 9, 30, 14, 45),
            status="confirmed",
        ),
        Appointment(
            business_id=business.id,
            service_id=service.id,
            staff_member_id=staff_member.id,
            customer_name="Client lendemain",
            customer_email="client3@example.com",
            start_datetime=datetime(2026, 10, 1, 10, 0),
            end_datetime=datetime(2026, 10, 1, 10, 45),
            status="confirmed",
        ),
        Appointment(
            business_id=business.id,
            service_id=service.id,
            staff_member_id=staff_member.id,
            customer_name="Client annulé",
            customer_email="cancelled@example.com",
            start_datetime=datetime(2026, 9, 30, 16, 0),
            end_datetime=datetime(2026, 9, 30, 16, 45),
            status="cancelled",
        ),
    ]

    db_session.add_all(appointments)
    db_session.commit()

    result = count_appointments_for_date(
        db_session,
        business.id,
        date(2026, 9, 30),
    )

    assert result == 2



def test_get_dashboard_summary(
    db_session,
    business_and_staff,
):
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

    appointments = [
        Appointment(
            business_id=business.id,
            service_id=service.id,
            staff_member_id=staff_member.id,
            customer_name="Client 1",
            customer_email="client1@example.com",
            start_datetime=datetime(2026, 9, 30, 9, 0),
            end_datetime=datetime(2026, 9, 30, 9, 45),
            status="confirmed",
        ),
        Appointment(
            business_id=business.id,
            service_id=service.id,
            staff_member_id=staff_member.id,
            customer_name="Client 2",
            customer_email="client2@example.com",
            start_datetime=datetime(2026, 9, 30, 14, 0),
            end_datetime=datetime(2026, 9, 30, 14, 45),
            status="confirmed",
        ),
    ]

    db_session.add_all(appointments)
    db_session.commit()

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.get(
            f"/businesses/{business.id}/dashboard/summary",
            params={
                "target_date": "2026-09-30",
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "appointments_today": 2,
        "revenue_today": 70.0,
        "clients_today": 2,
        "occupancy_rate": 0.0,
    }


def test_get_revenue_for_date(
    db_session,
    business_and_staff,
):
    business, staff_member = business_and_staff

    service_35 = Service(
        business_id=business.id,
        name="Coupe",
        duration_minutes=45,
        price=35,
    )

    service_50 = Service(
        business_id=business.id,
        name="Coloration",
        duration_minutes=60,
        price=50,
    )

    db_session.add_all([service_35, service_50])
    db_session.commit()
    db_session.refresh(service_35)
    db_session.refresh(service_50)

    appointments = [
        Appointment(
            business_id=business.id,
            service_id=service_35.id,
            staff_member_id=staff_member.id,
            customer_name="Client 1",
            customer_email="client1@example.com",
            start_datetime=datetime(2026, 9, 30, 9, 0),
            end_datetime=datetime(2026, 9, 30, 9, 45),
            status="confirmed",
        ),
        Appointment(
            business_id=business.id,
            service_id=service_50.id,
            staff_member_id=staff_member.id,
            customer_name="Client 2",
            customer_email="client2@example.com",
            start_datetime=datetime(2026, 9, 30, 11, 0),
            end_datetime=datetime(2026, 9, 30, 12, 0),
            status="confirmed",
        ),
        Appointment(
            business_id=business.id,
            service_id=service_50.id,
            staff_member_id=staff_member.id,
            customer_name="Client annulé",
            customer_email="cancelled@example.com",
            start_datetime=datetime(2026, 9, 30, 15, 0),
            end_datetime=datetime(2026, 9, 30, 16, 0),
            status="cancelled",
        ),
    ]

    db_session.add_all(appointments)
    db_session.commit()

    result = get_revenue_for_date(
        db_session,
        business.id,
        date(2026, 9, 30),
    )

    assert result == 85.0


def test_count_clients_for_date(
    db_session,
    business_and_staff,
):
    business, staff_member = business_and_staff

    service = Service(
        business_id=business.id,
        name="Coupe",
        duration_minutes=45,
        price=35,
    )

    db_session.add(service)
    db_session.commit()
    db_session.refresh(service)

    appointments = [
        Appointment(
            business_id=business.id,
            service_id=service.id,
            staff_member_id=staff_member.id,
            customer_name="Client 1",
            customer_email="client1@example.com",
            start_datetime=datetime(2026, 9, 30, 9, 0),
            end_datetime=datetime(2026, 9, 30, 9, 45),
            status="confirmed",
        ),
        Appointment(
            business_id=business.id,
            service_id=service.id,
            staff_member_id=staff_member.id,
            customer_name="Client 1",
            customer_email="client1@example.com",
            start_datetime=datetime(2026, 9, 30, 11, 0),
            end_datetime=datetime(2026, 9, 30, 11, 45),
            status="confirmed",
        ),
        Appointment(
            business_id=business.id,
            service_id=service.id,
            staff_member_id=staff_member.id,
            customer_name="Client 2",
            customer_email="client2@example.com",
            start_datetime=datetime(2026, 9, 30, 14, 0),
            end_datetime=datetime(2026, 9, 30, 14, 45),
            status="confirmed",
        ),
    ]

    db_session.add_all(appointments)
    db_session.commit()

    result = count_clients_for_date(
        db_session,
        business.id,
        date(2026, 9, 30),
    )

    assert result == 2


def test_get_booked_minutes_for_date(
    db_session,
    business_and_staff,
):
    business, staff_member = business_and_staff

    service = Service(
        business_id=business.id,
        name="Coupe",
        duration_minutes=45,
        price=35,
    )

    db_session.add(service)
    db_session.commit()
    db_session.refresh(service)

    appointments = [
        Appointment(
            business_id=business.id,
            service_id=service.id,
            staff_member_id=staff_member.id,
            customer_name="Client 1",
            customer_email="client1@example.com",
            start_datetime=datetime(2026, 9, 30, 9, 0),
            end_datetime=datetime(2026, 9, 30, 9, 45),
            status="confirmed",
        ),
        Appointment(
            business_id=business.id,
            service_id=service.id,
            staff_member_id=staff_member.id,
            customer_name="Client 2",
            customer_email="client2@example.com",
            start_datetime=datetime(2026, 9, 30, 14, 0),
            end_datetime=datetime(2026, 9, 30, 14, 45),
            status="confirmed",
        ),
        Appointment(
            business_id=business.id,
            service_id=service.id,
            staff_member_id=staff_member.id,
            customer_name="Client annulé",
            customer_email="cancelled@example.com",
            start_datetime=datetime(2026, 9, 30, 16, 0),
            end_datetime=datetime(2026, 9, 30, 16, 45),
            status="cancelled",
        ),
    ]

    db_session.add_all(appointments)
    db_session.commit()

    result = get_booked_minutes_for_date(
        db_session,
        business.id,
        date(2026, 9, 30),
    )

    assert result == 90


def test_get_scheduled_minutes_for_date(
    db_session,
    business_and_staff,
):
    business, staff_member = business_and_staff

    from app.models import Availability

    availability = Availability(
        business_id=business.id,
        staff_member_id=staff_member.id,
        weekday=date(2026, 9, 30).weekday(),
        start_time=datetime.strptime("09:00", "%H:%M").time(),
        end_time=datetime.strptime("17:00", "%H:%M").time(),
    )

    db_session.add(availability)
    db_session.commit()

    result = get_scheduled_minutes_for_date(
        db_session,
        business.id,
        date(2026, 9, 30),
    )

    assert result == 480



def test_get_available_minutes_for_date_with_absence(
    db_session,
    business_and_staff,
):
    business, staff_member = business_and_staff

    from app.models import Absence, Availability

    target_date = date(2026, 9, 30)

    availability = Availability(
        business_id=business.id,
        staff_member_id=staff_member.id,
        weekday=target_date.weekday(),
        start_time=datetime.strptime("09:00", "%H:%M").time(),
        end_time=datetime.strptime("17:00", "%H:%M").time(),
    )

    absence = Absence(
        business_id=business.id,
        staff_member_id=staff_member.id,
        start_datetime=datetime(2026, 9, 30, 12, 0),
        end_datetime=datetime(2026, 9, 30, 14, 0),
        reason="Indisponible",
    )

    db_session.add_all([
        availability,
        absence,
    ])
    db_session.commit()

    result = get_available_minutes_for_date(
        db_session,
        business.id,
        target_date,
    )

    assert result == 360



def test_get_occupancy_rate_for_date(
    db_session,
    business_and_staff,
):
    business, staff_member = business_and_staff

    from app.models import Absence, Availability

    target_date = date(2026, 9, 30)

    availability = Availability(
        business_id=business.id,
        staff_member_id=staff_member.id,
        weekday=target_date.weekday(),
        start_time=datetime.strptime("09:00", "%H:%M").time(),
        end_time=datetime.strptime("17:00", "%H:%M").time(),
    )

    absence = Absence(
        business_id=business.id,
        staff_member_id=staff_member.id,
        start_datetime=datetime(2026, 9, 30, 12, 0),
        end_datetime=datetime(2026, 9, 30, 14, 0),
        reason="Indisponible",
    )

    service = Service(
        business_id=business.id,
        name="Coupe",
        duration_minutes=45,
        price=35,
    )

    db_session.add_all([availability, absence, service])
    db_session.commit()
    db_session.refresh(service)

    appointments = [
        Appointment(
            business_id=business.id,
            service_id=service.id,
            staff_member_id=staff_member.id,
            customer_name="Client 1",
            customer_email="client1@example.com",
            start_datetime=datetime(2026, 9, 30, 9, 0),
            end_datetime=datetime(2026, 9, 30, 9, 45),
            status="confirmed",
        ),
        Appointment(
            business_id=business.id,
            service_id=service.id,
            staff_member_id=staff_member.id,
            customer_name="Client 2",
            customer_email="client2@example.com",
            start_datetime=datetime(2026, 9, 30, 10, 0),
            end_datetime=datetime(2026, 9, 30, 10, 45),
            status="confirmed",
        ),
    ]

    db_session.add_all(appointments)
    db_session.commit()

    result = get_occupancy_rate_for_date(
        db_session,
        business.id,
        target_date,
    )

    assert result == 25.0



def test_subtract_absence_from_intervals():
    intervals = [
        (
            datetime(2026, 9, 30, 9, 0),
            datetime(2026, 9, 30, 17, 0),
        )
    ]

    result = subtract_absence_from_intervals(
        intervals,
        datetime(2026, 9, 30, 12, 0),
        datetime(2026, 9, 30, 14, 0),
    )

    assert result == [
        (
            datetime(2026, 9, 30, 9, 0),
            datetime(2026, 9, 30, 12, 0),
        ),
        (
            datetime(2026, 9, 30, 14, 0),
            datetime(2026, 9, 30, 17, 0),
        ),
    ]



def test_get_staff_absences_for_date(
    db_session,
    business_and_staff,
):
    business, staff_member = business_and_staff

    from app.models import Absence

    absences = [
        # Absence pendant la journée ciblée
        Absence(
            business_id=business.id,
            staff_member_id=staff_member.id,
            start_datetime=datetime(2026, 9, 30, 12, 0),
            end_datetime=datetime(2026, 9, 30, 14, 0),
        ),

        # Absence qui commence la veille mais déborde sur la journée
        Absence(
            business_id=business.id,
            staff_member_id=staff_member.id,
            start_datetime=datetime(2026, 9, 29, 23, 0),
            end_datetime=datetime(2026, 9, 30, 10, 0),
        ),

        # Absence hors de la journée : ne doit pas être retournée
        Absence(
            business_id=business.id,
            staff_member_id=staff_member.id,
            start_datetime=datetime(2026, 10, 1, 9, 0),
            end_datetime=datetime(2026, 10, 1, 10, 0),
        ),
    ]

    db_session.add_all(absences)
    db_session.commit()

    result = get_staff_absences_for_date(
        db_session,
        business.id,
        staff_member.id,
        date(2026, 9, 30),
    )

    assert len(result) == 2