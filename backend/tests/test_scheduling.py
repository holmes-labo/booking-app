from datetime import datetime, time

import pytest
from fastapi import HTTPException

from app.models import (
    Absence,
    Appointment,
    Availability,
    ScheduleOverride,
    Service,
)

from app.services.scheduling_service import (
    check_appointment_conflict,
    check_staff_absence,
    check_staff_availability,
)


def test_appointment_outside_staff_availability(
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

    availability = Availability(
        business_id=business.id,
        staff_member_id=staff_member.id,
        weekday=0,
        start_time=time(9, 0),
        end_time=time(18, 0),
    )

    db_session.add(availability)
    db_session.commit()

    start_datetime = datetime(2026, 9, 28, 8, 0)
    end_datetime = datetime(2026, 9, 28, 8, 45)

    with pytest.raises(HTTPException) as exception:
        check_staff_availability(
            db_session,
            business.id,
            staff_member.id,
            start_datetime,
            end_datetime,
        )

    assert exception.value.status_code == 409
    assert (
        exception.value.detail
        == "Appointment is outside staff member availability"
    )



def test_appointment_inside_staff_availability(
    db_session,
    business_and_staff,
):
    business, staff_member = business_and_staff

    availability = Availability(
        business_id=business.id,
        staff_member_id=staff_member.id,
        weekday=0,
        start_time=time(9, 0),
        end_time=time(18, 0),
    )

    db_session.add(availability)
    db_session.commit()

    check_staff_availability(
        db_session,
        business.id,
        staff_member.id,
        datetime(2026, 9, 28, 14, 0),
        datetime(2026, 9, 28, 14, 45),
    )


def test_appointment_during_staff_absence(db_session, business_and_staff):
    business, staff_member = business_and_staff

    absence = Absence(
        business_id=business.id,
        staff_member_id=staff_member.id,
        start_datetime=datetime(2026, 9, 28, 14, 0),
        end_datetime=datetime(2026, 9, 28, 16, 0),
        reason="Personal",
    )

    db_session.add(absence)
    db_session.commit()

    with pytest.raises(HTTPException) as exception:
        check_staff_absence(
            db_session,
            business.id,
            staff_member.id,
            datetime(2026, 9, 28, 15, 0),
            datetime(2026, 9, 28, 15, 45),
        )

    assert exception.value.status_code == 409
    assert (
        exception.value.detail
        == "Staff member is unavailable during this time"
    )



def test_overlapping_appointment_is_rejected(
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

    existing_appointment = Appointment(
        business_id=business.id,
        service_id=service.id,
        staff_member_id=staff_member.id,
        customer_name="Client 1",
        customer_email="client1@example.com",
        start_datetime=datetime(2026, 9, 28, 14, 0),
        end_datetime=datetime(2026, 9, 28, 14, 45),
        status="confirmed",
    )

    db_session.add(existing_appointment)
    db_session.commit()

    with pytest.raises(HTTPException) as exception:
        check_appointment_conflict(
            db_session,
            business.id,
            staff_member.id,
            datetime(2026, 9, 28, 14, 15),
            datetime(2026, 9, 28, 15, 0),
        )

    assert exception.value.status_code == 409
    assert (
        exception.value.detail
        == "Staff member already has an appointment during this time"
    )


def test_schedule_override_allows_appointment(
    db_session,
    business_and_staff,
):
    business, staff_member = business_and_staff

    schedule_override = ScheduleOverride(
        business_id=business.id,
        staff_member_id=staff_member.id,
        date=datetime(2026, 9, 29).date(),
        start_time=time(9, 0),
        end_time=time(12, 0),
    )

    db_session.add(schedule_override)
    db_session.commit()

    check_staff_availability(
        db_session,
        business.id,
        staff_member.id,
        datetime(2026, 9, 29, 10, 0),
        datetime(2026, 9, 29, 10, 45),
    )


def test_schedule_override_allows_appointment(
    db_session,
    business_and_staff,
):
    business, staff_member = business_and_staff

    schedule_override = ScheduleOverride(
        business_id=business.id,
        staff_member_id=staff_member.id,
        date=datetime(2026, 9, 29).date(),
        start_time=time(9, 0),
        end_time=time(12, 0),
    )

    db_session.add(schedule_override)
    db_session.commit()

    check_staff_availability(
        db_session,
        business.id,
        staff_member.id,
        datetime(2026, 9, 29, 10, 0),
        datetime(2026, 9, 29, 10, 45),
    )