from datetime import datetime, time

from app.crud.appointment import create_appointment
from app.models import Availability, Service, StaffService
from app.schemas import AppointmentCreate

import pytest
from fastapi import HTTPException



def test_create_valid_appointment(
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

    availability = Availability(
        business_id=business.id,
        staff_member_id=staff_member.id,
        weekday=0,
        start_time=time(9, 0),
        end_time=time(18, 0),
    )

    db_session.add_all([service, availability])
    db_session.commit()
    db_session.refresh(service)

    staff_service = StaffService(
        staff_member_id=staff_member.id,
        service_id=service.id,
    )

    db_session.add(staff_service)
    db_session.commit()

    appointment_data = AppointmentCreate(
        service_id=service.id,
        staff_member_id=staff_member.id,
        customer_name="Marie Dupont",
        customer_email="marie@example.com",
        customer_phone="0600000000",
        start_datetime=datetime(2026, 9, 28, 14, 0),
    )

    appointment = create_appointment(
        db_session,
        business.id,
        appointment_data,
    )

    assert appointment.id is not None
    assert appointment.business_id == business.id
    assert appointment.service_id == service.id
    assert appointment.staff_member_id == staff_member.id
    assert appointment.start_datetime == datetime(2026, 9, 28, 14, 0)
    assert appointment.end_datetime == datetime(2026, 9, 28, 14, 45)
    assert appointment.status == "confirmed"

def test_create_overlapping_appointment_is_rejected(
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

    availability = Availability(
        business_id=business.id,
        staff_member_id=staff_member.id,
        weekday=0,
        start_time=time(9, 0),
        end_time=time(18, 0),
    )

    db_session.add_all([service, availability])
    db_session.commit()
    db_session.refresh(service)

    staff_service = StaffService(
        staff_member_id=staff_member.id,
        service_id=service.id,
    )

    db_session.add(staff_service)
    db_session.commit()

    first_appointment = AppointmentCreate(
        service_id=service.id,
        staff_member_id=staff_member.id,
        customer_name="Client 1",
        customer_email="client1@example.com",
        start_datetime=datetime(2026, 9, 28, 14, 0),
    )

    create_appointment(
        db_session,
        business.id,
        first_appointment,
    )

    overlapping_appointment = AppointmentCreate(
        service_id=service.id,
        staff_member_id=staff_member.id,
        customer_name="Client 2",
        customer_email="client2@example.com",
        start_datetime=datetime(2026, 9, 28, 14, 15),
    )

    with pytest.raises(HTTPException) as exception:
        create_appointment(
            db_session,
            business.id,
            overlapping_appointment,
        )

    assert exception.value.status_code == 409
    assert (
        exception.value.detail
        == "Staff member already has an appointment during this time"
    )


def test_create_appointment_is_rejected_when_service_not_assigned_to_staff(
    db_session,
    business_and_staff,
):
    business, staff_member = business_and_staff

    service = Service(
        business_id=business.id,
        name="Coloration",
        duration_minutes=60,
        price=50,
    )

    availability = Availability(
        business_id=business.id,
        staff_member_id=staff_member.id,
        weekday=0,
        start_time=time(9, 0),
        end_time=time(18, 0),
    )

    db_session.add_all([service, availability])
    db_session.commit()
    db_session.refresh(service)

    appointment_data = AppointmentCreate(
        service_id=service.id,
        staff_member_id=staff_member.id,
        customer_name="Client test",
        customer_email="client@example.com",
        start_datetime=datetime(2026, 9, 28, 14, 0),
    )

    with pytest.raises(HTTPException) as exception:
        create_appointment(
            db_session,
            business.id,
            appointment_data,
        )

    assert exception.value.status_code == 409
    assert (
        exception.value.detail
        == "Staff member cannot perform this service"
    )