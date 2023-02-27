from datetime import date

from tests.factories import (
    ReservationRequestFactory,
    SlotFactory,
    ResyConfigFactory,
    DetailsResponseBodyFactory,
)
from resy_bot.models import (
    FindRequestBody,
    DetailsRequestBody,
    AuthRequestBody,
    BookRequestBody,
)
from resy_bot.model_builders import (
    build_find_request_body,
    build_get_slot_details_body,
    build_auth_request_body,
    build_book_request_body,
)


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
