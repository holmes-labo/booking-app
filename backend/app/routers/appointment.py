from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud import create_appointment
from app.dependencies import get_db
from app.schemas import AppointmentCreate, AppointmentRead, AvailableSlotRead
from app.services.service_catalog import get_service_or_404
from app.services.staff_service import (
    check_staff_can_perform_service,
    get_staff_member_or_404,
    get_staff_members_for_service,
)
from app.services.slot_service import get_available_slots_for_staff

router = APIRouter(
    prefix="/businesses/{business_id}/appointments",
    tags=["appointments"],
)


@router.post("", response_model=AppointmentRead)
def create_appointment_endpoint(
    business_id: int,
    appointment: AppointmentCreate,
    db: Session = Depends(get_db),
):
    return create_appointment(db, business_id, appointment)

@router.get(
    "/available-slots",
    response_model=list[AvailableSlotRead],
)


def get_available_slots_endpoint(
    business_id: int,
    service_id: int,
    target_date: date,
    staff_member_id: int | None = None,
    db: Session = Depends(get_db),
):
    service = get_service_or_404(
        db,
        business_id,
        service_id,
    )

    if (
        service.staff_assignment_mode == "automatic"
        and staff_member_id is not None
    ):
        raise HTTPException(
            status_code=422,
            detail="A staff member cannot be selected for this service",
        )


    if staff_member_id is not None:
        staff_member = get_staff_member_or_404(
            db,
            business_id,
            staff_member_id,
        )


        check_staff_can_perform_service(
            db,
            staff_member.id,
            service.id,
        )

        slots = get_available_slots_for_staff(
            db=db,
            business_id=business_id,
            staff_member_id=staff_member.id,
            target_date=target_date,
            service_duration_minutes=service.duration_minutes,
        )

        return [
            AvailableSlotRead(
                start_datetime=start_datetime,
                end_datetime=start_datetime
                + timedelta(minutes=service.duration_minutes),
                staff_member_id=staff_member.id,
            )
            for start_datetime in slots
        ]

    if service.staff_assignment_mode == "customer_choice":
        raise HTTPException(
            status_code=422,
            detail="A staff member must be selected for this service",
        )

    staff_members = get_staff_members_for_service(
        db=db,
        business_id=business_id,
        service_id=service.id,
    )

    available_slots = []
    automatic_start_times = set()

    for staff_member in staff_members:
        slots = get_available_slots_for_staff(
            db=db,
            business_id=business_id,
            staff_member_id=staff_member.id,
            target_date=target_date,
            service_duration_minutes=service.duration_minutes,
        )

        for start_datetime in slots:
            if service.staff_assignment_mode == "automatic":
                if start_datetime in automatic_start_times:
                    continue

                automatic_start_times.add(start_datetime)

                available_slots.append(
                    AvailableSlotRead(
                        start_datetime=start_datetime,
                        end_datetime=start_datetime
                        + timedelta(minutes=service.duration_minutes),
                        staff_member_id=None,
                    )
                )
            else:
                available_slots.append(
                    AvailableSlotRead(
                        start_datetime=start_datetime,
                        end_datetime=start_datetime
                        + timedelta(minutes=service.duration_minutes),
                        staff_member_id=staff_member.id,
                    )
                )

    return available_slots