from datetime import date, time

from pydantic import BaseModel, model_validator


class ScheduleOverrideCreate(BaseModel):
    date: date
    start_time: time
    end_time: time

    @model_validator(mode="after")
    def validate_times(self):
        if self.end_time <= self.start_time:
            raise ValueError(
                "end_time must be later than start_time"
            )
        return self


class ScheduleOverrideRead(ScheduleOverrideCreate):
    id: int
    business_id: int
    staff_member_id: int

    model_config = {"from_attributes": True}