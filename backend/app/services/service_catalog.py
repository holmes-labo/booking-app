from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Service


def get_service_or_404(
    db: Session,
    business_id: int,
    service_id: int,
) -> Service:

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

    return service