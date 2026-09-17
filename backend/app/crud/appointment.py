from datetime import timedelta

from sqlalchemy.orm import Session

from app.models import Appointment

from app.schemas import AppointmentCreate

from app.services.business_service import get_business_or_404
from app.services.service_catalog import get_service_or_404
from app.services.staff_service import get_staff_member_or_404
from app.services.scheduling_service import (
    check_appointment_conflict,
    check_staff_absence,
    check_staff_availability,
)



def create_appointment(
    db: Session,
    business_id: int,
    appointment: AppointmentCreate,
) -> Appointment:

    # Vérifier que l'entreprise existe
    get_business_or_404(
        db,
        business_id,
    )

    get_staff_member_or_404(
        db,
        business_id,
        appointment.staff_member_id,
    )

    # Vérifier que la prestation existe
    service = get_service_or_404(
        db,
        business_id,
        appointment.service_id,
    )

    # Calculer automatiquement l'heure de fin
    end_datetime = appointment.start_datetime + timedelta(
        minutes=service.duration_minutes
    )

    check_staff_availability(
        db,
        business_id,
        appointment.staff_member_id,
        appointment.start_datetime,
        end_datetime,
    )

    check_staff_absence(
        db,
        business_id,
        appointment.staff_member_id,
        appointment.start_datetime,
        end_datetime,
    )

    check_appointment_conflict(
        db,
        business_id,
        appointment.staff_member_id,
        appointment.start_datetime,
        end_datetime,
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