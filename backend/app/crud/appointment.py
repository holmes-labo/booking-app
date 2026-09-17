from datetime import timedelta

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import (
    Appointment,
    Availability,
    Business,
    Service,
    StaffMember,
    Absence,
)
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

    staff_member = db.get(
        StaffMember,
        appointment.staff_member_id,
    )

    if staff_member is None:
        raise HTTPException(
            status_code=404,
            detail="Staff member not found",
        )

    if staff_member.business_id != business_id:
        raise HTTPException(
            status_code=400,
            detail="Staff member does not belong to this business",
        )

    if not staff_member.active:
        raise HTTPException(
            status_code=409,
            detail="Staff member is inactive",
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
            Availability.staff_member_id == appointment.staff_member_id,
            Availability.weekday == weekday,
            Availability.start_time <= appointment.start_datetime.time(),
            Availability.end_time >= end_datetime.time(),
        )
        .first()
    )

    if availability is None:
        raise HTTPException(
            status_code=409,
            detail="Appointment is outside staff member availability",
        )


    absence = (
        db.query(Absence)
        .filter(
            Absence.business_id == business_id,
            Absence.staff_member_id == appointment.staff_member_id,
            Absence.start_datetime < end_datetime,
            Absence.end_datetime > appointment.start_datetime,
        )
        .first()
    )

    if absence:
        raise HTTPException(
            status_code=409,
            detail="Staff member is unavailable during this time",
        )


    overlapping_appointment = (
        db.query(Appointment)
        .filter(
            Appointment.business_id == business_id,
            Appointment.staff_member_id == appointment.staff_member_id,
            Appointment.status != "cancelled",
            Appointment.start_datetime < end_datetime,
            Appointment.end_datetime > appointment.start_datetime,
        )
        .first()
    )

    if overlapping_appointment:
        raise HTTPException(
            status_code=409,
            detail="Staff member already has an appointment during this time",
        )

    # Créer le rendez-vous
    db_appointment = Appointment(
        business_id=business_id,
        service_id=appointment.service_id,
        staff_member_id=appointment.staff_member_id,
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