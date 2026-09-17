from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Business, ScheduleOverride, StaffMember
from app.schemas import ScheduleOverrideCreate


def create_schedule_override(
    db: Session,
    business_id: int,
    staff_member_id: int,
    schedule_override: ScheduleOverrideCreate,
) -> ScheduleOverride:

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
        db.query(ScheduleOverride)
        .filter(
            ScheduleOverride.business_id == business_id,
            ScheduleOverride.staff_member_id == staff_member_id,
            ScheduleOverride.date == schedule_override.date,
            ScheduleOverride.start_time < schedule_override.end_time,
            ScheduleOverride.end_time > schedule_override.start_time,
        )
        .first()
    )

    if overlapping:
        raise HTTPException(
            status_code=409,
            detail="This schedule override overlaps an existing time range",
        )

    db_schedule_override = ScheduleOverride(
        business_id=business_id,
        staff_member_id=staff_member_id,
        date=schedule_override.date,
        start_time=schedule_override.start_time,
        end_time=schedule_override.end_time,
    )

    db.add(db_schedule_override)
    db.commit()
    db.refresh(db_schedule_override)

    return db_schedule_override

def get_schedule_overrides_by_staff_member(
    db: Session,
    business_id: int,
    staff_member_id: int,
) -> list[ScheduleOverride]:

    return (
        db.query(ScheduleOverride)
        .filter(
            ScheduleOverride.business_id == business_id,
            ScheduleOverride.staff_member_id == staff_member_id,
        )
        .order_by(
            ScheduleOverride.date,
            ScheduleOverride.start_time,
        )
        .all()
    )