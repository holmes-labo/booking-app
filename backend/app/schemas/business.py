from pydantic import BaseModel


class BusinessCreate(BaseModel):
    name: str
    profession: str


class BusinessRead(BusinessCreate):
    id: int

    model_config = {
        "from_attributes": True
    }