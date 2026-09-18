from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.crud.staff_service import assign_service_to_staff_member
from app.dependencies import get_db
from app.schemas import StaffServiceRead


router = APIRouter(
    prefix="/businesses/{business_id}/staff-members/{staff_member_id}/services",
    tags=["staff-services"],
)


@router.post(
    "/{service_id}",
    response_model=StaffServiceRead,
)
def assign_service_to_staff_member_endpoint(
    business_id: int,
    staff_member_id: int,
    service_id: int,
    db: Session = Depends(get_db),
):
    return assign_service_to_staff_member(
        db,
        business_id,
        staff_member_id,
        service_id,
    )