from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Business, StaffMember
from app.schemas import StaffMemberCreate


def create_staff_member(
    db: Session,
    business_id: int,
    staff_member: StaffMemberCreate,
) -> StaffMember:

    business = db.get(Business, business_id)

    if business is None:
        raise HTTPException(
            status_code=404,
            detail="Business not found",
        )

    db_staff_member = StaffMember(
        business_id=business_id,
        first_name=staff_member.first_name,
        last_name=staff_member.last_name,
        active=True,
    )

    db.add(db_staff_member)
    db.commit()
    db.refresh(db_staff_member)

    return db_staff_member


def get_staff_members_by_business(
    db: Session,
    business_id: int,
) -> list[StaffMember]:

    return (
        db.query(StaffMember)
        .filter(
            StaffMember.business_id == business_id,
            StaffMember.active.is_(True),
        )
        .order_by(
            StaffMember.first_name,
            StaffMember.last_name,
        )
        .all()
    )