from datetime import date, datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import (
    Absence,
    Appointment,
    Availability,
    OpeningHour,
    ScheduleOverride,
)


def check_business_opening_hours(
    db: Session,
    business_id: int,
    start_datetime: datetime,
    end_datetime: datetime,
) -> None:
    """
    Vérifie que le rendez-vous est entièrement compris dans
    une plage d'ouverture de l'entreprise.
    """
    opening_hour = (
        db.query(OpeningHour)
        .filter(
            OpeningHour.business_id == business_id,
            OpeningHour.weekday == start_datetime.weekday(),
            OpeningHour.start_time <= start_datetime.time(),
            OpeningHour.end_time >= end_datetime.time(),
        )
        .first()
    )

    if opening_hour is None:
        raise HTTPException(
            status_code=409,
            detail="Appointment is outside business opening hours",
        )

def check_staff_availability(
    db: Session,
    business_id: int,
    staff_member_id: int,
    start_datetime: datetime,
    end_datetime: datetime,
) -> None:
    schedule_overrides = (
        db.query(ScheduleOverride)
        .filter(
            ScheduleOverride.business_id == business_id,
            ScheduleOverride.staff_member_id == staff_member_id,
            ScheduleOverride.date == start_datetime.date(),
        )
        .all()
    )

    if schedule_overrides:
        matching_override = next(
            (
                override
                for override in schedule_overrides
                if (
                    override.start_time <= start_datetime.time()
                    and override.end_time >= end_datetime.time()
                )
            ),
            None,
        )

        if matching_override is None:
            raise HTTPException(
                status_code=409,
                detail="Appointment is outside staff member availability",
            )

        return

    availability = (
        db.query(Availability)
        .filter(
            Availability.business_id == business_id,
            Availability.staff_member_id == staff_member_id,
            Availability.weekday == start_datetime.weekday(),
            Availability.start_time <= start_datetime.time(),
            Availability.end_time >= end_datetime.time(),
        )
        .first()
    )

    if availability is None:
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


def is_staff_available_for_appointment(
    db: Session,
    business_id: int,
    staff_member_id: int,
    start_datetime: datetime,
    end_datetime: datetime,
) -> bool:

    try:
        check_business_opening_hours(
            db,
            business_id,
            start_datetime,
            end_datetime,
        )

        check_staff_availability(
            db,
            business_id,
            staff_member_id,
            start_datetime,
            end_datetime,
        )

        check_staff_absence(
            db,
            business_id,
            staff_member_id,
            start_datetime,
            end_datetime,
        )

        check_appointment_conflict(
            db,
            business_id,
            staff_member_id,
            start_datetime,
            end_datetime,
        )

    except HTTPException:
        return False

    return True


def get_staff_schedule_for_date(
    db: Session,
    business_id: int,
    staff_member_id: int,
    target_date: date,
) -> list[tuple]:
    schedule_overrides = (
        db.query(ScheduleOverride)
        .filter(
            ScheduleOverride.business_id == business_id,
            ScheduleOverride.staff_member_id == staff_member_id,
            ScheduleOverride.date == target_date,
        )
        .order_by(ScheduleOverride.start_time)
        .all()
    )

    if schedule_overrides:
        return [
            (override.start_time, override.end_time)
            for override in schedule_overrides
        ]

    availabilities = (
        db.query(Availability)
        .filter(
            Availability.business_id == business_id,
            Availability.staff_member_id == staff_member_id,
            Availability.weekday == target_date.weekday(),
        )
        .order_by(Availability.start_time)
        .all()
    )

    return [
        (availability.start_time, availability.end_time)
        for availability in availabilities
    ]