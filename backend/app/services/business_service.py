from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Business


def get_business_or_404(
    db: Session,
    business_id: int,
) -> Business:

    business = db.get(Business, business_id)

    if business is None:
        raise HTTPException(
            status_code=404,
            detail="Business not found",
        )

    return business