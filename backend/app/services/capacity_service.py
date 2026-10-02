from datetime import date, datetime, time, timedelta

from sqlalchemy.orm import Session

from app.models import Absence

from app.models import Absence, StaffMember
from app.services.scheduling_service import get_staff_schedule_for_date


def subtract_absence_from_intervals(
    intervals: list[tuple[datetime, datetime]],
    absence_start: datetime,
    absence_end: datetime,
) -> list[tuple[datetime, datetime]]:
    """
    Retire une période d'absence d'une liste de plages disponibles.

    Une absence peut :
    - ne pas chevaucher une plage ;
    - couper une plage en deux ;
    - supprimer le début ou la fin d'une plage ;
    - supprimer entièrement une plage.

    Exemple :
        disponibilité : 09:00 -> 17:00
        absence       : 12:00 -> 14:00

        résultat :
            09:00 -> 12:00
            14:00 -> 17:00
    """
    remaining_intervals = []

    for interval_start, interval_end in intervals:
        # Calcule uniquement la partie commune entre l'absence
        # et la plage actuellement disponible.
        overlap_start = max(interval_start, absence_start)
        overlap_end = min(interval_end, absence_end)

        # Aucun chevauchement : la plage reste intacte.
        if overlap_start >= overlap_end:
            remaining_intervals.append(
                (interval_start, interval_end)
            )
            continue

        # Conserve la partie située avant l'absence.
        if interval_start < overlap_start:
            remaining_intervals.append(
                (interval_start, overlap_start)
            )

        # Conserve la partie située après l'absence.
        if overlap_end < interval_end:
            remaining_intervals.append(
                (overlap_end, interval_end)
            )

    return remaining_intervals


def get_staff_absences_for_date(
    db: Session,
    business_id: int,
    staff_member_id: int,
    target_date: date,
) -> list[Absence]:
    """
    Retourne toutes les absences d'un professionnel qui chevauchent
    la journée demandée.

    Une absence commencée la veille est donc incluse si elle continue
    après minuit. De même, une absence qui commence pendant la journée
    et se termine le lendemain est prise en compte.
    """
    day_start = datetime.combine(
        target_date,
        time.min,
    )
    day_end = day_start + timedelta(days=1)

    return (
        db.query(Absence)
        .filter(
            Absence.business_id == business_id,
            Absence.staff_member_id == staff_member_id,

            # Une absence chevauche la journée si elle commence avant
            # sa fin et se termine après son début.
            Absence.start_datetime < day_end,
            Absence.end_datetime > day_start,
        )
        .all()
    )

def get_scheduled_minutes_for_date(
    db: Session,
    business_id: int,
    target_date: date,
) -> int:
    """
    Calcule la capacité de travail planifiée pour une entreprise
    à une date donnée.

    Seuls les professionnels actifs sont pris en compte.

    Les horaires utilisés sont ceux retournés par le moteur de planning :
    un horaire exceptionnel remplace donc l'horaire hebdomadaire lorsqu'il
    existe pour la date demandée.

    Les absences ne sont pas déduites ici. Cette fonction représente
    uniquement la capacité théorique planifiée.
    """
    staff_members = (
        db.query(StaffMember)
        .filter(
            StaffMember.business_id == business_id,
            StaffMember.active.is_(True),
        )
        .all()
    )

    total_minutes = 0

    for staff_member in staff_members:
        schedule = get_staff_schedule_for_date(
            db,
            business_id,
            staff_member.id,
            target_date,
        )

        for start_time, end_time in schedule:
            start_datetime = datetime.combine(
                target_date,
                start_time,
            )
            end_datetime = datetime.combine(
                target_date,
                end_time,
            )

            total_minutes += int(
                (end_datetime - start_datetime).total_seconds()
                / 60
            )

    return total_minutes

def get_available_minutes_for_date(
    db: Session,
    business_id: int,
    target_date: date,
) -> int:
    """
    Calcule la capacité réellement disponible de l'entreprise pour une journée.

    Le calcul :
    1. récupère les professionnels actifs ;
    2. récupère leurs horaires effectifs pour la date ;
    3. récupère les absences qui chevauchent cette journée ;
    4. retire ces absences des plages de travail ;
    5. additionne les minutes restantes.

    Le résultat représente donc la capacité utilisable pour recevoir
    des rendez-vous, et non simplement la durée de travail planifiée.
    """
    staff_members = (
        db.query(StaffMember)
        .filter(
            StaffMember.business_id == business_id,
            StaffMember.active.is_(True),
        )
        .all()
    )

    total_minutes = 0

    for staff_member in staff_members:
        schedule = get_staff_schedule_for_date(
            db,
            business_id,
            staff_member.id,
            target_date,
        )

        absences = get_staff_absences_for_date(
            db,
            business_id,
            staff_member.id,
            target_date,
        )

        for start_time, end_time in schedule:
            schedule_start = datetime.combine(target_date, start_time)
            schedule_end = datetime.combine(target_date, end_time)

            available_intervals = [
                (schedule_start, schedule_end)
            ]

            for absence in absences:
                available_intervals = subtract_absence_from_intervals(
                    available_intervals,
                    absence.start_datetime,
                    absence.end_datetime,
                )

            total_minutes += sum(
                int(
                    (interval_end - interval_start).total_seconds()
                    / 60
                )
                for interval_start, interval_end in available_intervals
            )

    return total_minutes