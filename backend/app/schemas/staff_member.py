from pydantic import BaseModel


class StaffMemberCreate(BaseModel):
    first_name: str
    last_name: str | None = None


class StaffMemberRead(StaffMemberCreate):
    id: int
    business_id: int
    active: bool

    model_config = {
        "from_attributes": True
    }