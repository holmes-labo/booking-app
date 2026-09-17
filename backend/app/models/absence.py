from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Absence(Base):
    __tablename__ = "absences"

    id: Mapped[int] = mapped_column(primary_key=True)

    business_id: Mapped[int] = mapped_column(
        ForeignKey("businesses.id"),
        nullable=False,
    )

    staff_member_id: Mapped[int] = mapped_column(
        ForeignKey("staff_members.id"),
        nullable=False,
    )

    start_datetime: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    end_datetime: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    reason: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )