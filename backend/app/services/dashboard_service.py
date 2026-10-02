from datetime import date, datetime, time, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.appointment import Appointment
from app.models.service import Service

from app.services.capacity_service import get_available_minutes_for_date


def count_appointments_for_date(
    db: Session,
    business_id: int,
    target_date: date,
) -> int:
    start_datetime = datetime.combine(
        target_date,
        time.min,
    )

    end_datetime = start_datetime + timedelta(days=1)

    statement = (
        select(func.count(Appointment.id))
        .where(
            Appointment.business_id == business_id,
            Appointment.start_datetime >= start_datetime,
            Appointment.start_datetime < end_datetime,
            Appointment.status == "confirmed",
        )
    )

    return db.scalar(statement) or 0


def get_revenue_for_date(
    db: Session,
    business_id: int,
    target_date: date,
) -> float:
    start_datetime = datetime.combine(
        target_date,
        time.min,
    )

    end_datetime = start_datetime + timedelta(days=1)

    statement = (
        select(func.coalesce(func.sum(Service.price), 0))
        .join(
            Appointment,
            Appointment.service_id == Service.id,
        )
        .where(
            Appointment.business_id == business_id,
            Appointment.start_datetime >= start_datetime,
            Appointment.start_datetime < end_datetime,
            Appointment.status == "confirmed",
        )
    )

    return float(db.scalar(statement) or 0)


def count_clients_for_date(
    db: Session,
    business_id: int,
    target_date: date,
) -> int:
    start_datetime = datetime.combine(
        target_date,
        time.min,
    )

    end_datetime = start_datetime + timedelta(days=1)

    statement = (
        select(
            func.count(
                func.distinct(Appointment.customer_email)
            )
        )
        .where(
            Appointment.business_id == business_id,
            Appointment.start_datetime >= start_datetime,
            Appointment.start_datetime < end_datetime,
            Appointment.status == "confirmed",
        )
    )

    return db.scalar(statement) or 0

def get_booked_minutes_for_date(
    db: Session,
    business_id: int,
    target_date: date,
) -> int:
    start_datetime = datetime.combine(
        target_date,
        time.min,
    )
    end_datetime = start_datetime + timedelta(days=1)

    statement = select(
        Appointment.start_datetime,
        Appointment.end_datetime,
    ).where(
        Appointment.business_id == business_id,
        Appointment.start_datetime >= start_datetime,
        Appointment.start_datetime < end_datetime,
        Appointment.status == "confirmed",
    )

    appointments = db.execute(statement).all()

    return sum(
        int((end - start).total_seconds() / 60)
        for start, end in appointments
    )



def get_occupancy_rate_for_date(
    db: Session,
    business_id: int,
    target_date: date,
) -> float:
    booked_minutes = get_booked_minutes_for_date(
        db,
        business_id,
        target_date,
    )

    available_minutes = get_available_minutes_for_date(
        db,
        business_id,
        target_date,
    )

    if available_minutes == 0:
        return 0.0

    return round(
        booked_minutes / available_minutes * 100,
        1,
    )