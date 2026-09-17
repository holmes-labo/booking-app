from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import (
    Absence,
    Appointment,
    Availability,
    ScheduleOverride,
)

def check_staff_availability(
    db: Session,
    business_id: int,
    staff_member_id: int,
    start_datetime: datetime,
    end_datetime: datetime,
) -> None:

    weekday = start_datetime.weekday()

    schedule_override = (
        db.query(ScheduleOverride)
        .filter(
            ScheduleOverride.business_id == business_id,
            ScheduleOverride.staff_member_id == staff_member_id,
            ScheduleOverride.date == start_datetime.date(),
            ScheduleOverride.start_time <= start_datetime.time(),
            ScheduleOverride.end_time >= end_datetime.time(),
        )
        .first()
    )

    availability = (
        db.query(Availability)
        .filter(
            Availability.business_id == business_id,
            Availability.staff_member_id == staff_member_id,
            Availability.weekday == weekday,
            Availability.start_time <= start_datetime.time(),
            Availability.end_time >= end_datetime.time(),
        )
        .first()
    )

    if availability is None and schedule_override is None:
        raise HTTPException(
            status_code=409,
            detail="Appointment is outside staff member availability",
        )

def check_staff_absence(
    db: Session,
    business_id: int,
    staff_member_id: int,
    start_datetime: datetime,
    end_datetime: datetime,
) -> None:

    absence = (
        db.query(Absence)
        .filter(
            Absence.business_id == business_id,
            Absence.staff_member_id == staff_member_id,
            Absence.start_datetime < end_datetime,
            Absence.end_datetime > start_datetime,
        )
        .first()
    )

    if absence:
        raise HTTPException(
            status_code=409,
            detail="Staff member is unavailable during this time",
        )

def check_appointment_conflict(
    db: Session,
    business_id: int,
    staff_member_id: int,
    start_datetime: datetime,
    end_datetime: datetime,
) -> None:

    overlapping_appointment = (
        db.query(Appointment)
        .filter(
            Appointment.business_id == business_id,
            Appointment.staff_member_id == staff_member_id,
            Appointment.status != "cancelled",
            Appointment.start_datetime < end_datetime,
            Appointment.end_datetime > start_datetime,
        )
        .first()
    )

    if overlapping_appointment:
        raise HTTPException(
            status_code=409,
            detail="Staff member already has an appointment during this time",
        )