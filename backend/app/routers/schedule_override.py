from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.crud import (
    create_schedule_override,
    get_schedule_overrides_by_staff_member,
)
from app.dependencies import get_db
from app.schemas import (
    ScheduleOverrideCreate,
    ScheduleOverrideRead,
)


router = APIRouter(
    prefix="/businesses/{business_id}/staff-members/{staff_member_id}/schedule-overrides",
    tags=["schedule-overrides"],
)


@router.post("", response_model=ScheduleOverrideRead)
def create_schedule_override_endpoint(
    business_id: int,
    staff_member_id: int,
    schedule_override: ScheduleOverrideCreate,
    db: Session = Depends(get_db),
):
    return create_schedule_override(
        db,
        business_id,
        staff_member_id,
        schedule_override,
    )


@router.get("", response_model=list[ScheduleOverrideRead])
def get_schedule_overrides_endpoint(
    business_id: int,
    staff_member_id: int,
    db: Session = Depends(get_db),
):
    return get_schedule_overrides_by_staff_member(
        db,
        business_id,
        staff_member_id,
    )