from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.opening_hour import OpeningHour

if TYPE_CHECKING:
    from app.models.service import Service
    from app.models.staff_member import StaffMember
    from app.models.opening_hour import OpeningHour


class Business(Base):
    __tablename__ = "businesses"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    profession: Mapped[str] = mapped_column(String(100), nullable=False)

    services: Mapped[list["Service"]] = relationship(
        "Service",
        back_populates="business",
        cascade="all, delete-orphan",
    )

    staff_members: Mapped[list["StaffMember"]] = relationship(
        "StaffMember",
        back_populates="business",
        cascade="all, delete-orphan",
    )

    opening_hours: Mapped[list["OpeningHour"]] = relationship(
        "OpeningHour",
        back_populates="business",
        cascade="all, delete-orphan",
    )