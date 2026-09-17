from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import StaffMember


def get_staff_member_or_404(
    db: Session,
    business_id: int,
    staff_member_id: int,
) -> StaffMember:

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

    if not staff_member.active:
        raise HTTPException(
            status_code=409,
            detail="Staff member is inactive",
        )

    return staff_member