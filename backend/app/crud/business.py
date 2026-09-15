from sqlalchemy.orm import Session

from app.models import Business
from app.schemas import BusinessCreate


def create_business(
    db: Session,
    business: BusinessCreate,
) -> Business:
    db_business = Business(
        name=business.name,
        profession=business.profession,
    )

    db.add(db_business)
    db.commit()
    db.refresh(db_business)

    return db_business


def get_businesses(db: Session) -> list[Business]:
    return db.query(Business).all()