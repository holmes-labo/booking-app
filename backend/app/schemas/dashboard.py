from pydantic import BaseModel



class DashboardSummaryRead(BaseModel):
    appointments_today: int
    revenue_today: float
    clients_today: int
    occupancy_rate: float