from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.crud import create_service, get_services_by_business
from app.dependencies import get_db
from app.schemas import ServiceCreate, ServiceRead

router = APIRouter(
    prefix="/businesses/{business_id}/services",
    tags=["services"],
)


@router.post("", response_model=ServiceRead)
def create_service_endpoint(
    business_id: int,
    service: ServiceCreate,
    db: Session = Depends(get_db),
):
    return create_service(db, business_id, service)


@router.get("", response_model=list[ServiceRead])
def get_services_endpoint(
    business_id: int,
    db: Session = Depends(get_db),
):
    return get_services_by_business(db, business_id)