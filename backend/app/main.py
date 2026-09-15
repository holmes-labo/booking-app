from fastapi import FastAPI
from sqlalchemy import text

from app.database import engine
from app.models import Base
from app.routers import appointment, availability, business, service

app = FastAPI(title="Booking API")

app.include_router(business.router)
app.include_router(service.router)
app.include_router(availability.router)
app.include_router(appointment.router)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


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