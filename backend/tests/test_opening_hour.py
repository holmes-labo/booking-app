from datetime import time

import pytest
from fastapi import HTTPException

from app.crud.opening_hour import (
    create_opening_hour,
    delete_opening_hour,
    get_business_opening_hours,
    update_opening_hour,
)
from app.models import Business
from app.schemas import OpeningHourCreate


def test_create_and_get_business_opening_hours(db_session):
    business = Business(
        name="Studio Test",
        profession="Coiffure",
    )
    db_session.add(business)
    db_session.commit()
    db_session.refresh(business)

    morning = create_opening_hour(
        db_session,
        business.id,
        OpeningHourCreate(
            weekday=0,
            start_time=time(9, 0),
            end_time=time(12, 0),
        ),
    )

    afternoon = create_opening_hour(
        db_session,
        business.id,
        OpeningHourCreate(
            weekday=0,
            start_time=time(14, 0),
            end_time=time(18, 0),
        ),
    )

    result = get_business_opening_hours(
        db_session,
        business.id,
    )

    assert len(result) == 2
    assert result[0].id == morning.id
    assert result[1].id == afternoon.id


def test_create_opening_hour_rejects_overlap(db_session):
    business = Business(
        name="Studio Test",
        profession="Coiffure",
    )
    db_session.add(business)
    db_session.commit()
    db_session.refresh(business)

    create_opening_hour(
        db_session,
        business.id,
        OpeningHourCreate(
            weekday=0,
            start_time=time(9, 0),
            end_time=time(13, 0),
        ),
    )

    with pytest.raises(HTTPException) as exc_info:
        create_opening_hour(
            db_session,
            business.id,
            OpeningHourCreate(
                weekday=0,
                start_time=time(12, 0),
                end_time=time(18, 0),
            ),
        )

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "Opening hours cannot overlap"



def test_create_opening_hour_allows_adjacent_ranges(db_session):
    business = Business(
        name="Studio Test",
        profession="Coiffure",
    )
    db_session.add(business)
    db_session.commit()
    db_session.refresh(business)

    create_opening_hour(
        db_session,
        business.id,
        OpeningHourCreate(
            weekday=0,
            start_time=time(9, 0),
            end_time=time(12, 0),
        ),
    )

    second_range = create_opening_hour(
        db_session,
        business.id,
        OpeningHourCreate(
            weekday=0,
            start_time=time(12, 0),
            end_time=time(18, 0),
        ),
    )

    assert second_range.start_time == time(12, 0)
    assert second_range.end_time == time(18, 0)


def test_delete_opening_hour(db_session):
    business = Business(
        name="Studio Test",
        profession="Coiffure",
    )
    db_session.add(business)
    db_session.commit()
    db_session.refresh(business)

    opening_hour = create_opening_hour(
        db_session,
        business.id,
        OpeningHourCreate(
            weekday=0,
            start_time=time(9, 0),
            end_time=time(18, 0),
        ),
    )

    delete_opening_hour(
        db_session,
        business.id,
        opening_hour.id,
    )

    result = get_business_opening_hours(
        db_session,
        business.id,
    )

    assert result == []


def test_update_opening_hour(db_session):
    business = Business(
        name="Studio Test",
        profession="Coiffure",
    )
    db_session.add(business)
    db_session.commit()
    db_session.refresh(business)

    opening_hour = create_opening_hour(
        db_session,
        business.id,
        OpeningHourCreate(
            weekday=0,
            start_time=time(9, 0),
            end_time=time(18, 0),
        ),
    )

    updated = update_opening_hour(
        db_session,
        business.id,
        opening_hour.id,
        OpeningHourCreate(
            weekday=0,
            start_time=time(10, 0),
            end_time=time(19, 0),
        ),
    )

    assert updated.start_time == time(10, 0)
    assert updated.end_time == time(19, 0)



def test_update_opening_hour_rejects_overlap(db_session):
    business = Business(
        name="Studio Test",
        profession="Coiffure",
    )
    db_session.add(business)
    db_session.commit()
    db_session.refresh(business)

    first_range = create_opening_hour(
        db_session,
        business.id,
        OpeningHourCreate(
            weekday=0,
            start_time=time(9, 0),
            end_time=time(12, 0),
        ),
    )

    create_opening_hour(
        db_session,
        business.id,
        OpeningHourCreate(
            weekday=0,
            start_time=time(14, 0),
            end_time=time(18, 0),
        ),
    )

    with pytest.raises(HTTPException) as exc_info:
        update_opening_hour(
            db_session,
            business.id,
            first_range.id,
            OpeningHourCreate(
                weekday=0,
                start_time=time(9, 0),
                end_time=time(15, 0),
            ),
        )

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "Opening hours cannot overlap"