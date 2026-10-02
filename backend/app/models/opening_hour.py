from datetime import time
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.business import Business


class OpeningHour(Base):
    """
    Plage d'ouverture habituelle d'une entreprise.

    Plusieurs plages peuvent exister pour un même jour afin de gérer,
    par exemple, une fermeture entre midi et deux.
    """

    __tablename__ = "opening_hours"

    id: Mapped[int] = mapped_column(primary_key=True)

    business_id: Mapped[int] = mapped_column(
        ForeignKey("businesses.id"),
        nullable=False,
    )

    # Même convention que datetime.weekday() :
    # lundi = 0, ..., dimanche = 6.
    weekday: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    start_time: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )

    end_time: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )

    business: Mapped["Business"] = relationship(
        "Business",
        back_populates="opening_hours",
    )