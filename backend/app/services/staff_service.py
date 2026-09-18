from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import StaffMember, StaffService


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

def check_staff_can_perform_service(
    db: Session,
    staff_member_id: int,
    service_id: int,
) -> None:

    assignment = db.get(
        StaffService,
        (staff_member_id, service_id),
    )

    if assignment is None:
        raise HTTPException(
            status_code=409,
            detail="Staff member cannot perform this service",
        )