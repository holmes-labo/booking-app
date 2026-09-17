from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.crud import (
    create_availability,
    get_availabilities_by_staff_member,
)

from app.dependencies import get_db
from app.schemas import AvailabilityCreate, AvailabilityRead

router = APIRouter(
    prefix="/businesses/{business_id}/staff-members/{staff_member_id}/availabilities",
    tags=["availabilities"],
)


@router.post("", response_model=AvailabilityRead)
def create_availability_endpoint(
    business_id: int,
    staff_member_id: int,
    availability: AvailabilityCreate,
    db: Session = Depends(get_db),
):
    return create_availability(
        db,
        business_id,
        staff_member_id,
        availability,
    )

@router.get("", response_model=list[AvailabilityRead])
def get_availabilities_endpoint(
    business_id: int,
    staff_member_id: int,
    db: Session = Depends(get_db),
):
    return get_availabilities_by_staff_member(
        db,
        business_id,
        staff_member_id,
    )