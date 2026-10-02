from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.crud.opening_hour import (
    create_opening_hour,
    delete_opening_hour,
    get_business_opening_hours,
    update_opening_hour,
)
from app.dependencies import get_db
from app.schemas import OpeningHourCreate, OpeningHourRead


router = APIRouter(
    prefix="/businesses/{business_id}/opening-hours",
    tags=["opening-hours"],
)


@router.get(
    "",
    response_model=list[OpeningHourRead],
)
def get_business_opening_hours_endpoint(
    business_id: int,
    db: Session = Depends(get_db),
):
    """Retourne les horaires d'ouverture habituels de l'entreprise."""
    return get_business_opening_hours(
        db,
        business_id,
    )


@router.post(
    "",
    response_model=OpeningHourRead,
    status_code=201,
)
def create_opening_hour_endpoint(
    business_id: int,
    opening_hour_data: OpeningHourCreate,
    db: Session = Depends(get_db),
):
    """Ajoute une plage d'ouverture habituelle à l'entreprise."""
    return create_opening_hour(
        db,
        business_id,
        opening_hour_data,
    )


@router.delete(
    "/{opening_hour_id}",
    status_code=204,
)
def delete_opening_hour_endpoint(
    business_id: int,
    opening_hour_id: int,
    db: Session = Depends(get_db),
):
    """Supprime une plage d'ouverture de l'entreprise."""
    delete_opening_hour(
        db,
        business_id,
        opening_hour_id,
    )


@router.put(
    "/{opening_hour_id}",
    response_model=OpeningHourRead,
)
def update_opening_hour_endpoint(
    business_id: int,
    opening_hour_id: int,
    opening_hour_data: OpeningHourCreate,
    db: Session = Depends(get_db),
):
    """Modifie une plage d'ouverture de l'entreprise."""
    return update_opening_hour(
        db,
        business_id,
        opening_hour_id,
        opening_hour_data,
    )