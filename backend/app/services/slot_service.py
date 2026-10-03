from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session

from app.crud.opening_hour import get_business_opening_hours
from app.services.scheduling_service import (
    get_staff_schedule_for_date,
    is_staff_available_for_appointment,
)

def generate_candidate_slots(
    start_datetime: datetime,
    end_datetime: datetime,
    service_duration_minutes: int,
    interval_minutes: int = 15,
) -> list[datetime]:

    slots = []

    current_slot = start_datetime
    service_duration = timedelta(minutes=service_duration_minutes)
    interval = timedelta(minutes=interval_minutes)

    while current_slot + service_duration <= end_datetime:
        slots.append(current_slot)
        current_slot += interval

    return slots

def filter_available_slots(
    db: Session,
    business_id: int,
    staff_member_id: int,
    candidate_slots: list[datetime],
    service_duration_minutes: int,
) -> list[datetime]:
    available_slots = []
    service_duration = timedelta(minutes=service_duration_minutes)

    for start_datetime in candidate_slots:
        end_datetime = start_datetime + service_duration

        if is_staff_available_for_appointment(
            db=db,
            business_id=business_id,
            staff_member_id=staff_member_id,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
        ):
            available_slots.append(start_datetime)

    return available_slots


def intersect_time_ranges(
    first_ranges: list[tuple],
    second_ranges: list[tuple],
) -> list[tuple]:
    """
    Retourne les portions communes entre deux ensembles de plages horaires.

    Exemple :
    salarié 09:00-19:00 + entreprise 10:00-18:00
    donne 10:00-18:00.
    """
    intersections = []

    for first_start, first_end in first_ranges:
        for second_start, second_end in second_ranges:
            start_time = max(first_start, second_start)
            end_time = min(first_end, second_end)

            if start_time < end_time:
                intersections.append((start_time, end_time))

    return intersections


def get_available_slots_for_staff(
    db: Session,
    business_id: int,
    staff_member_id: int,
    target_date: date,
    service_duration_minutes: int,
    interval_minutes: int = 15,
) -> list[datetime]:
    schedule = get_staff_schedule_for_date(
        db=db,
        business_id=business_id,
        staff_member_id=staff_member_id,
        target_date=target_date,
    )

    opening_hours = get_business_opening_hours(
        db=db,
        business_id=business_id,
    )

    # Même convention que datetime.weekday() :
    # lundi = 0 ... dimanche = 6.
    business_schedule = [
        (opening_hour.start_time, opening_hour.end_time)
        for opening_hour in opening_hours
        if opening_hour.weekday == target_date.weekday()
    ]

    schedule = intersect_time_ranges(
        schedule,
        business_schedule,
    )

    candidate_slots = []

    for start_time, end_time in schedule:
        start_datetime = datetime.combine(target_date, start_time)
        end_datetime = datetime.combine(target_date, end_time)

        candidate_slots.extend(
            generate_candidate_slots(
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                service_duration_minutes=service_duration_minutes,
                interval_minutes=interval_minutes,
            )
        )

    return filter_available_slots(
        db=db,
        business_id=business_id,
        staff_member_id=staff_member_id,
        candidate_slots=candidate_slots,
        service_duration_minutes=service_duration_minutes,
    )