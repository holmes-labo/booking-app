from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class StaffService(Base):
    __tablename__ = "staff_services"

    staff_member_id: Mapped[int] = mapped_column(
        ForeignKey("staff_members.id"),
        primary_key=True,
    )

    service_id: Mapped[int] = mapped_column(
        ForeignKey("services.id"),
        primary_key=True,
    )