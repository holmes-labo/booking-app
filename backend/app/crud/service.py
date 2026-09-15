from sqlalchemy.orm import Session

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