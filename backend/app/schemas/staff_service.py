from pydantic import BaseModel


class StaffServiceRead(BaseModel):
    staff_member_id: int
    service_id: int

    model_config = {"from_attributes": True}