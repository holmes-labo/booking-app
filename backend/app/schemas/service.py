from pydantic import BaseModel


class ServiceCreate(BaseModel):
    name: str
    duration_minutes: int
    price: float


class ServiceRead(ServiceCreate):
    id: int
    business_id: int

    model_config = {
        "from_attributes": True
    }