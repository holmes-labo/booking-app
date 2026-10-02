from datetime import datetime

from pydantic import BaseModel, EmailStr


class AppointmentCreate(BaseModel):
    service_id: int
    staff_member_id: int | None = None
    customer_name: str
    customer_email: EmailStr
    customer_phone: str | None = None
    start_datetime: datetime


class AppointmentRead(AppointmentCreate):
    id: int
    business_id: int
    end_datetime: datetime
    status: str

    model_config = {
        "from_attributes": True
    }

class AppointmentAgendaRead(AppointmentRead):
    """Rendez-vous enrichi avec les informations utiles à l'agenda."""

    service_name: str
    staff_first_name: str
    staff_last_name: str | None = None