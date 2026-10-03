from datetime import date, datetime, time, timedelta

from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.models import Appointment, Service, StaffMember

from app.schemas import AppointmentCreate

from app.services.business_service import get_business_or_404
from app.services.service_catalog import get_service_or_404
from app.services.staff_service import (
    check_staff_can_perform_service,
    get_staff_member_or_404,
    get_staff_members_for_service,
)

from app.services.scheduling_service import (
    check_appointment_conflict,
    check_business_opening_hours,
    check_staff_absence,
    check_staff_availability,
    is_staff_available_for_appointment,
)



def get_appointments_for_date(
    db: Session,
    business_id: int,
    target_date: date,
):
    """
    Retourne les rendez-vous d'une entreprise pour une journée donnée.

    Le service et le professionnel sont récupérés dans la même requête
    afin de fournir directement les informations nécessaires à l'agenda.
    Les rendez-vous sont triés chronologiquement.
    """
    day_start = datetime.combine(target_date, time.min)
    day_end = day_start + timedelta(days=1)

    return (
        db.query(Appointment, Service, StaffMember)
        .join(
            Service,
            Service.id == Appointment.service_id,
        )
        .join(
            StaffMember,
            StaffMember.id == Appointment.staff_member_id,
        )
        .filter(
            Appointment.business_id == business_id,
            Appointment.start_datetime >= day_start,
            Appointment.start_datetime < day_end,
        )
        .order_by(Appointment.start_datetime)
        .all()
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

    # Vérifier que la prestation existe
    service = get_service_or_404(
        db,
        business_id,
        appointment.service_id,
    )

    staff_member_id = appointment.staff_member_id

    if (
        service.staff_assignment_mode == "automatic"
        and staff_member_id is not None
    ):
        raise HTTPException(
            status_code=422,
            detail="A staff member cannot be selected for this service",
        )

    if (
        service.staff_assignment_mode == "customer_choice"
        and appointment.staff_member_id is None
    ):

        raise HTTPException(
            status_code=422,
            detail="A staff member must be selected for this service",
        )

    if (
        service.staff_assignment_mode in ("automatic", "optional")
        and staff_member_id is None
    ):
        end_datetime = appointment.start_datetime + timedelta(
            minutes=service.duration_minutes
        )

        candidates = get_staff_members_for_service(
            db,
            business_id,
            appointment.service_id,
        )

        selected_staff_member = None

        for candidate in candidates:
            if is_staff_available_for_appointment(
                db,
                business_id,
                candidate.id,
                appointment.start_datetime,
                end_datetime,
            ):
                selected_staff_member = candidate
                break

        if selected_staff_member is None:
            raise HTTPException(
                status_code=409,
                detail="No staff member is available for this time slot",
            )  
        
        staff_member_id = selected_staff_member.id

    get_staff_member_or_404(
        db,
        business_id,
        staff_member_id,
    )

    check_staff_can_perform_service(
        db,
        staff_member_id,
        appointment.service_id,
    )

    # Calculer automatiquement l'heure de fin
    end_datetime = appointment.start_datetime + timedelta(
        minutes=service.duration_minutes
    )
    # Un rendez-vous doit rester entièrement dans les horaires
    # d'ouverture de l'entreprise.
    check_business_opening_hours(
        db,
        business_id,
        appointment.start_datetime,
        end_datetime,
    )
    

    check_staff_availability(
        db,
        business_id,
        staff_member_id,
        appointment.start_datetime,
        end_datetime,
    )

    check_staff_absence(
        db,
        business_id,
        staff_member_id,
        appointment.start_datetime,
        end_datetime,
    )

    check_appointment_conflict(
        db,
        business_id,
        staff_member_id,
        appointment.start_datetime,
        end_datetime,
    )

    # Créer le rendez-vous
    db_appointment = Appointment(
        business_id=business_id,
        service_id=appointment.service_id,
        staff_member_id=staff_member_id,
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