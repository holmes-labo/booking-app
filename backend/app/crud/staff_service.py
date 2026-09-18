from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import StaffService
from app.services.service_catalog import get_service_or_404
from app.services.staff_service import get_staff_member_or_404


def assign_service_to_staff_member(
    db: Session,
    business_id: int,
    staff_member_id: int,
    service_id: int,
) -> StaffService:

    get_staff_member_or_404(
        db,
        business_id,
        staff_member_id,
    )

    get_service_or_404(
        db,
        business_id,
        service_id,
    )

    existing_assignment = db.get(
        StaffService,
        (staff_member_id, service_id),
    )

    if existing_assignment is not None:
        raise HTTPException(
            status_code=409,
            detail="Service is already assigned to this staff member",
        )

    assignment = StaffService(
        staff_member_id=staff_member_id,
        service_id=service_id,
    )

    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    return assignment