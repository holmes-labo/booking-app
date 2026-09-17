from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models import Availability, Business, StaffMember

from app.schemas import AvailabilityCreate


def create_availability(
    db: Session,
    business_id: int,
    staff_member_id: int,
    availability: AvailabilityCreate,
) -> Availability:

    business = db.get(Business, business_id)

    if business is None:
        raise HTTPException(
            status_code=404,
            detail="Business not found",
        )

    staff_member = db.get(StaffMember, staff_member_id)

    if staff_member is None:
        raise HTTPException(
            status_code=404,
            detail="Staff member not found",
        )

    if staff_member.business_id != business_id:
        raise HTTPException(
            status_code=400,
            detail="Staff member does not belong to this business",
        )

    overlapping = (
        db.query(Availability)
        .filter(
            Availability.business_id == business_id,
            Availability.weekday == availability.weekday,
            Availability.start_time < availability.end_time,
            Availability.end_time > availability.start_time,
            Availability.staff_member_id == staff_member_id,
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
        staff_member_id=staff_member_id,
        weekday=availability.weekday,
        start_time=availability.start_time,
        end_time=availability.end_time,
    )

    db.add(db_availability)
    db.commit()
    db.refresh(db_availability)

    return db_availability


def get_availabilities_by_staff_member(
    db: Session,
    business_id: int,
    staff_member_id: int,
) -> list[Availability]:
    return (
        db.query(Availability)
        .filter(
            Availability.business_id == business_id,
            Availability.staff_member_id == staff_member_id,
        )
        .order_by(
            Availability.weekday,
            Availability.start_time,
        )
        .all()
    )