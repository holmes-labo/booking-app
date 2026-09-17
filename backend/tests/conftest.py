import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models import Base

TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)



@pytest.fixture
def business_and_staff(db_session):
    from app.models import Business, StaffMember

    business = Business(
        name="Test Business",
        profession="Coiffure",
    )

    db_session.add(business)
    db_session.commit()
    db_session.refresh(business)

    staff_member = StaffMember(
        business_id=business.id,
        first_name="Sarah",
        active=True,
    )

    db_session.add(staff_member)
    db_session.commit()
    db_session.refresh(staff_member)

    return business, staff_member