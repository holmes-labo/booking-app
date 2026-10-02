from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.database import engine

from app.routers import (
    appointment,
    availability,
    business,
    dashboard,
    schedule_override,
    service,
    staff_member,
    absence,
    staff_service,
)

app = FastAPI(title="Booking API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(business.router)
app.include_router(dashboard.router)
app.include_router(service.router)
app.include_router(availability.router)
app.include_router(schedule_override.router)
app.include_router(appointment.router)
app.include_router(staff_member.router)
app.include_router(absence.router)
app.include_router(staff_service.router)




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