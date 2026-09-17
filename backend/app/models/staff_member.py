from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class StaffMember(Base):
    __tablename__ = "staff_members"

    id: Mapped[int] = mapped_column(primary_key=True)

    business_id: Mapped[int] = mapped_column(
        ForeignKey("businesses.id"),
        nullable=False,
    )

    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    last_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    business: Mapped["Business"] = relationship(
        "Business",
        back_populates="staff_members",
    )