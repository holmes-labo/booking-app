from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.dashboard import DashboardSummaryRead

from app.services.dashboard_service import (
    count_appointments_for_date,
    count_clients_for_date,
    get_occupancy_rate_for_date,
    get_revenue_for_date,
)

router = APIRouter(
    prefix="/businesses/{business_id}/dashboard",
    tags=["dashboard"],
)


@router.get(
    "/summary",
    response_model=DashboardSummaryRead,
)


def get_dashboard_summary(
    business_id: int,
    target_date: date,
    db: Session = Depends(get_db),
):
    appointments_today = count_appointments_for_date(
        db,
        business_id,
        target_date,
    )

    revenue_today = get_revenue_for_date(
        db,
        business_id,
        target_date,
    )

    clients_today = count_clients_for_date(
    db,
    business_id,
    target_date,
    )

    occupancy_rate = get_occupancy_rate_for_date(
        db,
        business_id,
        target_date,
    )

    return {
        "appointments_today": appointments_today,
        "revenue_today": revenue_today,
        "clients_today": count_clients_for_date(db, business_id, target_date),
        "occupancy_rate": occupancy_rate,
    }
