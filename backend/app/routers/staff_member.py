from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.crud import (
    create_staff_member,
    get_staff_members_by_business,
)
from app.dependencies import get_db
from app.schemas import StaffMemberCreate, StaffMemberRead


router = APIRouter(
    prefix="/businesses/{business_id}/staff-members",
    tags=["staff-members"],
)


@router.post("", response_model=StaffMemberRead)
def create_staff_member_endpoint(
    business_id: int,
    staff_member: StaffMemberCreate,
    db: Session = Depends(get_db),
):
    return create_staff_member(
        db,
        business_id,
        staff_member,
    )


@router.get("", response_model=list[StaffMemberRead])
def get_staff_members_endpoint(
    business_id: int,
    db: Session = Depends(get_db),
):
    return get_staff_members_by_business(
        db,
        business_id,
    )