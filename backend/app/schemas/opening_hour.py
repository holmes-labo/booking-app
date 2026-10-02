from datetime import time

from pydantic import BaseModel, Field, model_validator


class OpeningHourCreate(BaseModel):
    """Plage horaire d'ouverture habituelle d'une entreprise."""

    weekday: int = Field(ge=0, le=6)
    start_time: time
    end_time: time

    @model_validator(mode="after")
    def validate_time_range(self):
        if self.end_time <= self.start_time:
            raise ValueError(
                "end_time must be later than start_time"
            )

        return self


class OpeningHourRead(OpeningHourCreate):
    id: int
    business_id: int

    model_config = {"from_attributes": True}