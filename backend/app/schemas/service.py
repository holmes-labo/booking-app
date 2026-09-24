from typing import Literal

from pydantic import BaseModel


class ServiceCreate(BaseModel):
    name: str
    duration_minutes: int
    price: float
    staff_assignment_mode: Literal[
        "customer_choice",
        "automatic",
        "optional",
    ] = "optional"


class ServiceRead(ServiceCreate):
    id: int
    business_id: int

    model_config = {
        "from_attributes": True
    }