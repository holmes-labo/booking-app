from datetime import datetime

from pydantic import BaseModel, model_validator


class AbsenceCreate(BaseModel):
    start_datetime: datetime
    end_datetime: datetime
    reason: str | None = None

    @model_validator(mode="after")
    def validate_datetimes(self):
        if self.end_datetime <= self.start_datetime:
            raise ValueError(
                "end_datetime must be later than start_datetime"
            )
        return self


class AbsenceRead(AbsenceCreate):
    id: int
    business_id: int
    staff_member_id: int

    model_config = {"from_attributes": True}