from fastapi import FastAPI
from sqlalchemy import text

from app.database import engine

from app.routers import (
    appointment,
    availability,
    business,
    schedule_override,
    service,
    staff_member,
    absence,
)

app = FastAPI(title="Booking API")

app.include_router(business.router)
app.include_router(service.router)
app.include_router(availability.router)
app.include_router(schedule_override.router)
app.include_router(appointment.router)
app.include_router(staff_member.router)
app.include_router(absence.router)



@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/health/db")
def health_db():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {
        "status": "ok",
        "database": "connected",
    }