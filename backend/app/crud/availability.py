from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models import Availability, Business
from app.schemas import AvailabilityCreate


def create_availability(
    db: Session,
    business_id: int,
    availability: AvailabilityCreate,
) -> Availability:

    business = db.get(Business, business_id)

    if business is None:
        raise HTTPException(
            status_code=404,
            detail="Business not found",
        )

    overlapping = (
        db.query(Availability)
        .filter(
            Availability.business_id == business_id,
            Availability.weekday == availability.weekday,
            Availability.start_time < availability.end_time,
            Availability.end_time > availability.start_time,
        )
        .first()
    )

    if overlapping:
        raise HTTPException(
            status_code=409,
            detail="This availability overlaps an existing time range",
        )

    db_availability = Availability(
        business_id=business_id,
        weekday=availability.weekday,
        start_time=availability.start_time,
        end_time=availability.end_time,
    )

    db.add(db_availability)
    db.commit()
    db.refresh(db_availability)

    return db_availability


def get_availabilities_by_business(
    db: Session,
    business_id: int,
) -> list[Availability]:
    return (
        db.query(Availability)
        .filter(Availability.business_id == business_id)
        .order_by(
            Availability.weekday,
            Availability.start_time,
        )
        .all()
    )