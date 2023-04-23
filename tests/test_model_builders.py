from datetime import date
from unittest.mock import patch

from tests.factories import (
    ReservationRequestFactory,
    SlotFactory,
    ResyConfigFactory,
    DetailsResponseBodyFactory,
    TimedRepeatedReservationRequestFactory,
)
from resy_bot.models import (
    FindRequestBody,
    DetailsRequestBody,
)
from resy_bot.model_builders import (
    build_timed_reservation_request,
    build_find_request_body,
    build_get_slot_details_body,
    build_auth_request_body,
    build_book_request_body,
)


@patch("resy_bot.model_builders.date")
def test_build_timed_reservation_request(mock_date):
    mock_date.today.return_value = date(year=2000, month=4, day=28)
    repeated_request = TimedRepeatedReservationRequestFactory.create(
        reservation_request__days_from_now=5
    )
    request = build_timed_reservation_request(repeated_request)

    assert request.reservation_request.ideal_date == date(year=2000, month=5, day=3)
    assert request.expected_drop_hour == repeated_request.expected_drop_hour


def test_build_find_request_body():
    ideal_date = date(2000, 5, 3)
    request = ReservationRequestFactory.create(ideal_date=ideal_date)

    body = build_find_request_body(request)

    assert isinstance(body, FindRequestBody)
    assert body.venue_id == request.venue_id
    assert body.party_size == request.party_size
    assert body.day == "2000-05-03"


def test_build_get_slot_details_body():
    ideal_date = date(2000, 5, 3)
    request = ReservationRequestFactory.create(ideal_date=ideal_date)
    slot = SlotFactory.create()

    body = build_get_slot_details_body(request, slot)

    assert isinstance(body, DetailsRequestBody)
    assert body.config_id == slot.config.token
    assert body.day == "2000-05-03"
    assert body.party_size == request.party_size


def test_build_auth_request_body():
    config = ResyConfigFactory.create()

    body = build_auth_request_body(config)

    assert body.email == config.email
    assert body.password == config.password


def test_build_book_request_body():
    details = DetailsResponseBodyFactory.create()
    config = ResyConfigFactory.create()

    body = build_book_request_body(details, config)

    assert body.book_token == details.book_token.value
    assert body.struct_payment_method.id == config.payment_method_id
