from datetime import datetime

from pydantic import BaseModel


class AvailableSlotRead(BaseModel):
    start_datetime: datetime
    end_datetime: datetime
    staff_member_id: int | None = None