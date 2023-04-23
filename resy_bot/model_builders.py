from datetime import date, timedelta
from resy_bot.models import (
    ReservationRequest,
    TimedReservationRequest,
    TimedRepeatedReservationRequest,
    AuthRequestBody,
    FindRequestBody,
    DetailsRequestBody,
    Slot,
    DetailsResponseBody,
    BookRequestBody,
    ResyConfig,
    PaymentMethod,
)


def build_timed_reservation_request(
    repeat_request: TimedRepeatedReservationRequest,
) -> TimedReservationRequest:
    repeat_request_dict = repeat_request.reservation_request.dict()
    days_from_now = repeat_request_dict.pop("days_from_now")
    ideal_date = date.today() + timedelta(days=days_from_now)
    request = ReservationRequest(ideal_date=ideal_date, **repeat_request_dict)

    return TimedReservationRequest(
        reservation_request=request,
        expected_drop_hour=repeat_request.expected_drop_hour,
        expected_drop_minute=repeat_request.expected_drop_minute,
    )


def build_find_request_body(reservation: ReservationRequest) -> FindRequestBody:

    day = date.strftime(reservation.ideal_date, "%Y-%m-%d")

    return FindRequestBody(
        venue_id=reservation.venue_id, party_size=reservation.party_size, day=day
    )


def build_get_slot_details_body(
    reservation: ReservationRequest, slot: Slot
) -> DetailsRequestBody:

    day = date.strftime(reservation.ideal_date, "%Y-%m-%d")
    config_id = slot.config.token

    return DetailsRequestBody(
        config_id=config_id,
        day=day,
        party_size=reservation.party_size,
    )


def build_auth_request_body(config: ResyConfig) -> AuthRequestBody:
    return AuthRequestBody(email=config.email, password=config.password)


def build_book_request_body(
    details: DetailsResponseBody, config: ResyConfig
) -> BookRequestBody:
    payment_method = PaymentMethod(id=config.payment_method_id)
    return BookRequestBody(
        book_token=details.book_token.value, struct_payment_method=payment_method
    )
