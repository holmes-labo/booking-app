from sqlalchemy.orm import Session

from app.models import OpeningHour

from fastapi import HTTPException

from app.schemas import OpeningHourCreate


def get_business_opening_hours(
    db: Session,
    business_id: int,
) -> list[OpeningHour]:
    """
    Retourne les horaires d'ouverture habituels d'une entreprise.

    Les plages sont triées par jour de la semaine puis par heure
    afin de fournir un résultat directement exploitable par l'API.
    """
    return (
        db.query(OpeningHour)
        .filter(OpeningHour.business_id == business_id)
        .order_by(
            OpeningHour.weekday,
            OpeningHour.start_time,
        )
        .all()
    )


def create_opening_hour(
    db: Session,
    business_id: int,
    opening_hour_data: OpeningHourCreate,
) -> OpeningHour:
    """
    Crée une plage d'ouverture habituelle.

    Deux plages d'une même entreprise et d'un même jour ne peuvent
    pas se chevaucher. Des plages contiguës restent autorisées :
    09:00-12:00 puis 12:00-18:00.
    """
    overlapping_opening_hour = (
        db.query(OpeningHour)
        .filter(
            OpeningHour.business_id == business_id,
            OpeningHour.weekday == opening_hour_data.weekday,
            OpeningHour.start_time < opening_hour_data.end_time,
            OpeningHour.end_time > opening_hour_data.start_time,
        )
        .first()
    )

    if overlapping_opening_hour:
        raise HTTPException(
            status_code=409,
            detail="Opening hours cannot overlap",
        )

    opening_hour = OpeningHour(
        business_id=business_id,
        **opening_hour_data.model_dump(),
    )

    db.add(opening_hour)
    db.commit()
    db.refresh(opening_hour)

    return opening_hour


def delete_opening_hour(
    db: Session,
    business_id: int,
    opening_hour_id: int,
) -> None:
    """Supprime une plage d'ouverture appartenant à l'entreprise."""
    opening_hour = (
        db.query(OpeningHour)
        .filter(
            OpeningHour.id == opening_hour_id,
            OpeningHour.business_id == business_id,
        )
        .first()
    )

    if opening_hour is None:
        raise HTTPException(
            status_code=404,
            detail="Opening hour not found",
        )

    db.delete(opening_hour)
    db.commit()



def update_opening_hour(
    db: Session,
    business_id: int,
    opening_hour_id: int,
    opening_hour_data: OpeningHourCreate,
) -> OpeningHour:
    """
    Modifie une plage d'ouverture existante.

    La plage modifiée ne peut pas chevaucher une autre plage
    du même jour pour la même entreprise.
    """
    opening_hour = (
        db.query(OpeningHour)
        .filter(
            OpeningHour.id == opening_hour_id,
            OpeningHour.business_id == business_id,
        )
        .first()
    )

    if opening_hour is None:
        raise HTTPException(
            status_code=404,
            detail="Opening hour not found",
        )

    overlapping_opening_hour = (
        db.query(OpeningHour)
        .filter(
            OpeningHour.business_id == business_id,
            OpeningHour.weekday == opening_hour_data.weekday,
            OpeningHour.id != opening_hour_id,
            OpeningHour.start_time < opening_hour_data.end_time,
            OpeningHour.end_time > opening_hour_data.start_time,
        )
        .first()
    )

    if overlapping_opening_hour:
        raise HTTPException(
            status_code=409,
            detail="Opening hours cannot overlap",
        )

    opening_hour.weekday = opening_hour_data.weekday
    opening_hour.start_time = opening_hour_data.start_time
    opening_hour.end_time = opening_hour_data.end_time

    db.commit()
    db.refresh(opening_hour)

    return opening_hour