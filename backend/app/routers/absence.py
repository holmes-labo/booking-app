from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.crud import (
    create_absence,
    get_absences_by_staff_member,
)
from app.dependencies import get_db
from app.schemas import AbsenceCreate, AbsenceRead


router = APIRouter(
    prefix="/businesses/{business_id}/staff-members/{staff_member_id}/absences",
    tags=["absences"],
)


@router.post("", response_model=AbsenceRead)
def create_absence_endpoint(
    business_id: int,
    staff_member_id: int,
    absence: AbsenceCreate,
    db: Session = Depends(get_db),
):
    return create_absence(
        db,
        business_id,
        staff_member_id,
        absence,
    )

@router.get("", response_model=list[AbsenceRead])
def get_absences_endpoint(
    business_id: int,
    staff_member_id: int,
    db: Session = Depends(get_db),
):
    return get_absences_by_staff_member(
        db,
        business_id,
        staff_member_id,
    )