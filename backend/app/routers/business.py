from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.crud import create_business, get_businesses
from app.dependencies import get_db
from app.schemas import BusinessCreate, BusinessRead

router = APIRouter(
    prefix="/businesses",
    tags=["businesses"],
)


@router.post("", response_model=BusinessRead)
def create_business_endpoint(
    business: BusinessCreate,
    db: Session = Depends(get_db),
):
    return create_business(db, business)


@router.get("", response_model=list[BusinessRead])
def get_businesses_endpoint(
    db: Session = Depends(get_db),
):
    return get_businesses(db)