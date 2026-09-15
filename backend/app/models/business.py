from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


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