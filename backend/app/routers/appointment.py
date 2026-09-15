from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.crud import create_appointment
from app.dependencies import get_db
from app.schemas import AppointmentCreate, AppointmentRead

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