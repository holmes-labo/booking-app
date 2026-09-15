from datetime import timedelta

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Appointment, Availability, Business, Service
from app.schemas import AppointmentCreate


def create_appointment(
    db: Session,
    business_id: int,
    appointment: AppointmentCreate,
) -> Appointment:

    # Vérifier que l'entreprise existe
    business = db.get(Business, business_id)

    if business is None:
        raise HTTPException(
            status_code=404,
            detail="Business not found",
        )

    # Vérifier que la prestation existe
    service = db.get(Service, appointment.service_id)

    if service is None:
        raise HTTPException(
            status_code=404,
            detail="Service not found",
        )

    # Vérifier que la prestation appartient bien à cette entreprise
    if service.business_id != business_id:
        raise HTTPException(
            status_code=400,
            detail="Service does not belong to this business",
        )

    # Calculer automatiquement l'heure de fin
    end_datetime = appointment.start_datetime + timedelta(
        minutes=service.duration_minutes
    )

    # Vérifier que le rendez-vous est dans les horaires d'ouverture
    weekday = appointment.start_datetime.weekday()

    availability = (
        db.query(Availability)
        .filter(
            Availability.business_id == business_id,
            Availability.weekday == weekday,
            Availability.start_time <= appointment.start_datetime.time(),
            Availability.end_time >= end_datetime.time(),
        )
        .first()
    )

    if availability is None:
        raise HTTPException(
            status_code=409,
            detail="Appointment is outside business availability",
        )

    # Créer le rendez-vous
    db_appointment = Appointment(
        business_id=business_id,
        service_id=appointment.service_id,
        customer_name=appointment.customer_name,
        customer_email=appointment.customer_email,
        customer_phone=appointment.customer_phone,
        start_datetime=appointment.start_datetime,
        end_datetime=end_datetime,
        status="confirmed",
    )

    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)

    return db_appointment