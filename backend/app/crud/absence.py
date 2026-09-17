from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Absence, Business, StaffMember
from app.schemas import AbsenceCreate


def create_absence(
    db: Session,
    business_id: int,
    staff_member_id: int,
    absence: AbsenceCreate,
) -> Absence:

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

    db_absence = Absence(
        business_id=business_id,
        staff_member_id=staff_member_id,
        start_datetime=absence.start_datetime,
        end_datetime=absence.end_datetime,
        reason=absence.reason,
    )

    db.add(db_absence)
    db.commit()
    db.refresh(db_absence)

    return db_absence

def get_absences_by_staff_member(
    db: Session,
    business_id: int,
    staff_member_id: int,
) -> list[Absence]:

    return (
        db.query(Absence)
        .filter(
            Absence.business_id == business_id,
            Absence.staff_member_id == staff_member_id,
        )
        .order_by(Absence.start_datetime)
        .all()
    )