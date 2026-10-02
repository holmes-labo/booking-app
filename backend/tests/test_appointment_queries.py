from datetime import date, datetime

from app.crud.appointment import get_appointments_for_date
from app.models import Appointment, Service


def test_get_appointments_for_date(
    db_session,
    business_and_staff,
):
    """
    Vérifie que seuls les rendez-vous de la journée demandée sont retournés
    et qu'ils sont triés chronologiquement.
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

    # Insertion volontairement non chronologique pour vérifier
    # que la requête applique elle-même le tri.
    appointments = [
        Appointment(
            business_id=business.id,
            service_id=service.id,
            staff_member_id=staff_member.id,
            customer_name="Client 15h",
            customer_email="15h@example.com",
            start_datetime=datetime(2026, 10, 2, 15, 0),
            end_datetime=datetime(2026, 10, 2, 15, 45),
            status="confirmed",
        ),
        Appointment(
            business_id=business.id,
            service_id=service.id,
            staff_member_id=staff_member.id,
            customer_name="Client lendemain",
            customer_email="tomorrow@example.com",
            start_datetime=datetime(2026, 10, 3, 10, 0),
            end_datetime=datetime(2026, 10, 3, 10, 45),
            status="confirmed",
        ),
        Appointment(
            business_id=business.id,
            service_id=service.id,
            staff_member_id=staff_member.id,
            customer_name="Client 10h",
            customer_email="10h@example.com",
            start_datetime=datetime(2026, 10, 2, 10, 0),
            end_datetime=datetime(2026, 10, 2, 10, 45),
            status="confirmed",
        ),
    ]

    db_session.add_all(appointments)
    db_session.commit()

    result = get_appointments_for_date(
        db_session,
        business.id,
        date(2026, 10, 2),
    )

    assert len(result) == 2

    first_appointment, first_service, first_staff = result[0]
    second_appointment, second_service, second_staff = result[1]

    assert first_appointment.customer_name == "Client 10h"
    assert first_service.name == "Coupe femme"
    assert first_staff.id == staff_member.id

    assert second_appointment.customer_name == "Client 15h"
    assert second_service.name == "Coupe femme"
    assert second_staff.id == staff_member.id