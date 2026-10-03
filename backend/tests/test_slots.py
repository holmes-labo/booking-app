import pytest

from datetime import date, datetime, time

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models import (
    Appointment,
    Availability,
    Base,
    Business,
    OpeningHour,
    Service,
    StaffMember,
    ScheduleOverride,
)

from app.services.slot_service import (
    filter_available_slots,
    generate_candidate_slots,
    get_available_slots_for_staff,
)
from app.services.scheduling_service import get_staff_schedule_for_date



TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def test_generate_candidate_slots():
    slots = generate_candidate_slots(
        start_datetime=datetime(2026, 9, 28, 9, 0),
        end_datetime=datetime(2026, 9, 28, 11, 0),
        service_duration_minutes=45,
        interval_minutes=15,
    )

    assert slots == [
        datetime(2026, 9, 28, 9, 0),
        datetime(2026, 9, 28, 9, 15),
        datetime(2026, 9, 28, 9, 30),
        datetime(2026, 9, 28, 9, 45),
        datetime(2026, 9, 28, 10, 0),
        datetime(2026, 9, 28, 10, 15),
    ]


def test_generate_candidate_slots_when_service_does_not_fit():
    slots = generate_candidate_slots(
        start_datetime=datetime(2026, 9, 28, 9, 0),
        end_datetime=datetime(2026, 9, 28, 9, 30),
        service_duration_minutes=45,
        interval_minutes=15,
    )

    assert slots == []


def test_filter_available_slots_removes_conflicting_appointments(db):
    business = Business(
        name="Salon Test",
        profession="Coiffure",
    )
    db.add(business)
    db.flush()

    service = Service(
        business_id=business.id,
        name="Coupe",
        duration_minutes=45,
        price=35,
        staff_assignment_mode="optional",
    )
    db.add(service)

    staff_member = StaffMember(
        business_id=business.id,
        first_name="Léa",
        last_name="Martin",
        active=True,
    )
    db.add(staff_member)
    db.flush()

    availability = Availability(
        business_id=business.id,
        staff_member_id=staff_member.id,
        weekday=0,
        start_time=time(9, 0),
        end_time=time(12, 0),
    )

    opening_hour = OpeningHour(
        business_id=business.id,
        weekday=0,
        start_time=time(9, 0),
        end_time=time(12, 0),
    )

    db.add_all([availability, opening_hour])

    appointment = Appointment(
        business_id=business.id,
        service_id=service.id,
        staff_member_id=staff_member.id,
        customer_name="Client Test",
        customer_email="client@example.com",
        start_datetime=datetime(2026, 9, 28, 10, 0),
        end_datetime=datetime(2026, 9, 28, 10, 45),
        status="confirmed",
    )
    db.add(appointment)
    db.commit()

    candidate_slots = generate_candidate_slots(
        start_datetime=datetime(2026, 9, 28, 9, 0),
        end_datetime=datetime(2026, 9, 28, 12, 0),
        service_duration_minutes=45,
        interval_minutes=15,
    )

    available_slots = filter_available_slots(
        db=db,
        business_id=business.id,
        staff_member_id=staff_member.id,
        candidate_slots=candidate_slots,
        service_duration_minutes=45,
    )

    assert available_slots == [
        datetime(2026, 9, 28, 9, 0),
        datetime(2026, 9, 28, 9, 15),
        datetime(2026, 9, 28, 10, 45),
        datetime(2026, 9, 28, 11, 0),
        datetime(2026, 9, 28, 11, 15),
    ]



def test_get_staff_schedule_for_date_uses_weekly_availability(db):
    business = Business(
        name="Salon Test",
        profession="Coiffure",
    )
    db.add(business)
    db.flush()

    staff_member = StaffMember(
        business_id=business.id,
        first_name="Léa",
        last_name="Martin",
        active=True,
    )
    db.add(staff_member)
    db.flush()

    availability = Availability(
        business_id=business.id,
        staff_member_id=staff_member.id,
        weekday=0,
        start_time=time(9, 0),
        end_time=time(12, 0),
    )
    db.add(availability)
    db.commit()

    schedule = get_staff_schedule_for_date(
        db=db,
        business_id=business.id,
        staff_member_id=staff_member.id,
        target_date=date(2026, 9, 28),
    )

    assert schedule == [
        (time(9, 0), time(12, 0)),
    ]



def test_get_staff_schedule_for_date_uses_override_instead_of_weekly_availability(db):
    business = Business(
        name="Salon Test",
        profession="Coiffure",
    )
    db.add(business)
    db.flush()

    staff_member = StaffMember(
        business_id=business.id,
        first_name="Léa",
        last_name="Martin",
        active=True,
    )
    db.add(staff_member)
    db.flush()

    availability = Availability(
        business_id=business.id,
        staff_member_id=staff_member.id,
        weekday=0,
        start_time=time(9, 0),
        end_time=time(12, 0),
    )
    db.add(availability)

    schedule_override = ScheduleOverride(
        business_id=business.id,
        staff_member_id=staff_member.id,
        date=date(2026, 9, 28),
        start_time=time(14, 0),
        end_time=time(17, 0),
    )
    db.add(schedule_override)
    db.commit()

    schedule = get_staff_schedule_for_date(
        db=db,
        business_id=business.id,
        staff_member_id=staff_member.id,
        target_date=date(2026, 9, 28),
    )

    assert schedule == [
        (time(14, 0), time(17, 0)),
    ]



def test_get_available_slots_for_staff(db):
    business = Business(
        name="Salon Test",
        profession="Coiffure",
    )
    db.add(business)
    db.flush()

    service = Service(
        business_id=business.id,
        name="Coupe",
        duration_minutes=45,
        price=35,
        staff_assignment_mode="optional",
    )
    db.add(service)

    staff_member = StaffMember(
        business_id=business.id,
        first_name="Léa",
        last_name="Martin",
        active=True,
    )
    db.add(staff_member)
    db.flush()

    availability = Availability(
        business_id=business.id,
        staff_member_id=staff_member.id,
        weekday=0,
        start_time=time(9, 0),
        end_time=time(12, 0),
    )

    opening_hour = OpeningHour(
        business_id=business.id,
        weekday=0,
        start_time=time(9, 0),
        end_time=time(12, 0),
    )

    db.add_all([availability, opening_hour])

    appointment = Appointment(
        business_id=business.id,
        service_id=service.id,
        staff_member_id=staff_member.id,
        customer_name="Client Test",
        customer_email="client@example.com",
        start_datetime=datetime(2026, 9, 28, 10, 0),
        end_datetime=datetime(2026, 9, 28, 10, 45),
        status="confirmed",
    )
    db.add(appointment)
    db.commit()

    slots = get_available_slots_for_staff(
        db=db,
        business_id=business.id,
        staff_member_id=staff_member.id,
        target_date=date(2026, 9, 28),
        service_duration_minutes=45,
        interval_minutes=15,
    )

    assert slots == [
        datetime(2026, 9, 28, 9, 0),
        datetime(2026, 9, 28, 9, 15),
        datetime(2026, 9, 28, 10, 45),
        datetime(2026, 9, 28, 11, 0),
        datetime(2026, 9, 28, 11, 15),
    ]



def test_available_slots_respect_business_opening_hours(db):
    business = Business(
        name="Salon Test",
        profession="Coiffure",
    )
    db.add(business)
    db.flush()

    staff_member = StaffMember(
        business_id=business.id,
        first_name="Léa",
        last_name="Martin",
        active=True,
    )
    db.add(staff_member)
    db.flush()

    # L'entreprise ouvre de 10 h à 18 h le lundi.
    opening_hour = OpeningHour(
        business_id=business.id,
        weekday=0,
        start_time=time(10, 0),
        end_time=time(18, 0),
    )

    # Léa travaille de 9 h à 19 h.
    availability = Availability(
        business_id=business.id,
        staff_member_id=staff_member.id,
        weekday=0,
        start_time=time(9, 0),
        end_time=time(19, 0),
    )

    db.add_all([opening_hour, availability])
    db.commit()

    slots = get_available_slots_for_staff(
        db=db,
        business_id=business.id,
        staff_member_id=staff_member.id,
        target_date=date(2026, 9, 28),  # lundi
        service_duration_minutes=60,
        interval_minutes=60,
    )

    assert slots == [
        datetime(2026, 9, 28, 10, 0),
        datetime(2026, 9, 28, 11, 0),
        datetime(2026, 9, 28, 12, 0),
        datetime(2026, 9, 28, 13, 0),
        datetime(2026, 9, 28, 14, 0),
        datetime(2026, 9, 28, 15, 0),
        datetime(2026, 9, 28, 16, 0),
        datetime(2026, 9, 28, 17, 0),
    ]



def test_available_slots_respect_split_business_opening_hours(db):
    business = Business(
        name="Salon Test",
        profession="Coiffure",
    )
    db.add(business)
    db.flush()

    staff_member = StaffMember(
        business_id=business.id,
        first_name="Léa",
        last_name="Martin",
        active=True,
    )
    db.add(staff_member)
    db.flush()

    opening_hours = [
        OpeningHour(
            business_id=business.id,
            weekday=0,
            start_time=time(9, 0),
            end_time=time(12, 0),
        ),
        OpeningHour(
            business_id=business.id,
            weekday=0,
            start_time=time(14, 0),
            end_time=time(18, 0),
        ),
    ]

    availability = Availability(
        business_id=business.id,
        staff_member_id=staff_member.id,
        weekday=0,
        start_time=time(9, 0),
        end_time=time(18, 0),
    )

    db.add_all([*opening_hours, availability])
    db.commit()

    slots = get_available_slots_for_staff(
        db=db,
        business_id=business.id,
        staff_member_id=staff_member.id,
        target_date=date(2026, 9, 28),
        service_duration_minutes=60,
        interval_minutes=60,
    )

    assert slots == [
        datetime(2026, 9, 28, 9, 0),
        datetime(2026, 9, 28, 10, 0),
        datetime(2026, 9, 28, 11, 0),
        datetime(2026, 9, 28, 14, 0),
        datetime(2026, 9, 28, 15, 0),
        datetime(2026, 9, 28, 16, 0),
        datetime(2026, 9, 28, 17, 0),
    ]



def test_available_slots_are_empty_when_business_is_closed(db):
    business = Business(
        name="Salon Test",
        profession="Coiffure",
    )
    db.add(business)
    db.flush()

    staff_member = StaffMember(
        business_id=business.id,
        first_name="Léa",
        last_name="Martin",
        active=True,
    )
    db.add(staff_member)
    db.flush()

    # Léa travaille le lundi, mais aucune plage d'ouverture
    # n'est configurée pour l'entreprise ce jour-là.
    availability = Availability(
        business_id=business.id,
        staff_member_id=staff_member.id,
        weekday=0,
        start_time=time(9, 0),
        end_time=time(18, 0),
    )

    db.add(availability)
    db.commit()

    slots = get_available_slots_for_staff(
        db=db,
        business_id=business.id,
        staff_member_id=staff_member.id,
        target_date=date(2026, 9, 28),
        service_duration_minutes=60,
        interval_minutes=60,
    )

    assert slots == []