from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models import Service
from app.schemas import ServiceCreate


def create_service(
    db: Session,
    business_id: int,
    service: ServiceCreate,
) -> Service:
    db_service = Service(
        business_id=business_id,
        name=service.name,
        duration_minutes=service.duration_minutes,
        price=service.price,
        staff_assignment_mode=service.staff_assignment_mode,
    )

    db.add(db_service)
    db.commit()
    db.refresh(db_service)

    return db_service


def get_services_by_business(
    db: Session,
    business_id: int,
) -> list[Service]:
    return (
        db.query(Service)
        .filter(Service.business_id == business_id)
        .all()
    )


def delete_service(
    db: Session,
    business_id: int,
    service_id: int,
) -> None:
    service = db.get(Service, service_id)

    if service is None:
        raise HTTPException(
            status_code=404,
            detail="Service not found",
        )

    if service.business_id != business_id:
        raise HTTPException(
            status_code=400,
            detail="Service does not belong to this business",
        )

    db.delete(service)
    db.commit()