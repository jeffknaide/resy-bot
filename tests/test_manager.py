from datetime import datetime, timedelta
import pytest
from unittest.mock import MagicMock, patch

from resy_bot.errors import NoSlotsError, ExhaustedRetriesError
from resy_bot.api_access import ResyApiAccess
from resy_bot.models import (
    FindRequestBody,
    DetailsRequestBody,
    BookRequestBody,
    PaymentMethod,
    ReservationRetriesConfig,
)
from resy_bot.manager import ResyManager

from tests.factories import (
    ResyConfigFactory,
    SlotFactory,
    ReservationRequestFactory,
    DetailsResponseBodyFactory,
    ReservationRetriesConfigFactory,
    TimedReservationRequestFactory,
    ReservationRequestDaysInAdvanceFactory,
)


def test_build():
    config = ResyConfigFactory.create()
    manager = ResyManager.build(config)

    assert isinstance(manager, ResyManager)
    assert isinstance(manager.api_access, ResyApiAccess)


def test_make_reservation():
    config = ResyConfigFactory.create()
    retries_config = ReservationRetriesConfigFactory.create()
    request = ReservationRequestFactory.create()
    mock_api_access = MagicMock()
    slots = SlotFactory.create_batch(3)
    mock_api_access.find_booking_slots.return_value = slots

    details_response = DetailsResponseBodyFactory.create()
    mock_api_access.get_booking_token.return_value = details_response

    mock_selector = MagicMock()
    mock_selector.select.return_value = slots[0]

    manager = ResyManager(config, mock_api_access, mock_selector, retries_config)

    manager.make_reservation(request)

    expected_day = request.ideal_date.strftime("%Y-%m-%d")

    expected_find_request_body = FindRequestBody(
        venue_id=request.venue_id, party_size=request.party_size, day=expected_day
    )

    expected_details_request_body = DetailsRequestBody(
        config_id=slots[0].config.token, day=expected_day, party_size=request.party_size
    )

    expected_booking_request = BookRequestBody(
        book_token=details_response.book_token.value,
        struct_payment_method=PaymentMethod(id=config.payment_method_id),
    )

    mock_api_access.find_booking_slots.assert_called_once_with(
        expected_find_request_body
    )

    mock_selector.select.assert_called_once_with(slots, request)

    mock_api_access.get_booking_token.assert_called_once_with(
        expected_details_request_body
    )

    mock_api_access.book_slot.assert_called_once_with(expected_booking_request)


def test_make_reservation_days_in_advance():
    config = ResyConfigFactory.create()
    retries_config = ReservationRetriesConfigFactory.create()
    request = ReservationRequestDaysInAdvanceFactory.create()
    mock_api_access = MagicMock()
    slots = SlotFactory.create_batch(3)
    mock_api_access.find_booking_slots.return_value = slots

    details_response = DetailsResponseBodyFactory.create()
    mock_api_access.get_booking_token.return_value = details_response

    mock_selector = MagicMock()
    mock_selector.select.return_value = slots[0]

    manager = ResyManager(config, mock_api_access, mock_selector, retries_config)

    manager.make_reservation(request)

    expected_day = request.target_date.strftime("%Y-%m-%d")

    expected_find_request_body = FindRequestBody(
        venue_id=request.venue_id, party_size=request.party_size, day=expected_day
    )

    expected_details_request_body = DetailsRequestBody(
        config_id=slots[0].config.token, day=expected_day, party_size=request.party_size
    )

    expected_booking_request = BookRequestBody(
        book_token=details_response.book_token.value,
        struct_payment_method=PaymentMethod(id=config.payment_method_id),
    )

    mock_api_access.find_booking_slots.assert_called_once_with(
        expected_find_request_body
    )

    mock_selector.select.assert_called_once_with(slots, request)

    mock_api_access.get_booking_token.assert_called_once_with(
        expected_details_request_body
    )

    mock_api_access.book_slot.assert_called_once_with(expected_booking_request)


def test_make_reservation_no_slots():
    config = ResyConfigFactory.create()
    retries_config = ReservationRetriesConfigFactory.create()
    request = ReservationRequestFactory.create()
    mock_api_access = MagicMock()
    mock_api_access.find_booking_slots.return_value = []

    mock_selector = MagicMock()

    manager = ResyManager(config, mock_api_access, mock_selector, retries_config)

    with pytest.raises(NoSlotsError):
        manager.make_reservation(request)


@patch("resy_bot.manager.ResyManager.make_reservation")
def test_make_reservation_with_retries(mock_make_reservation):
    config = ResyConfigFactory.create()
    mock_make_reservation.side_effect = NoSlotsError
    mock_api_access = MagicMock()
    mock_selector = MagicMock()
    retry_config = ReservationRetriesConfig(
        seconds_between_retries=0.1,
        retry_duration=1,
    )

    request = ReservationRequestFactory.create()

    manager = ResyManager(config, mock_api_access, mock_selector, retry_config)

    with pytest.raises(ExhaustedRetriesError):
        manager.make_reservation_with_retries(request)

    assert mock_make_reservation.call_count == 10


def test_get_drop_time():
    config = ResyConfigFactory.create()
    mock_api_access = MagicMock()
    mock_selector = MagicMock()
    retry_config = ReservationRetriesConfig(
        seconds_between_retries=0.1,
        retry_duration=1,
    )

    request = TimedReservationRequestFactory.create()

    manager = ResyManager(config, mock_api_access, mock_selector, retry_config)

    drop_time = manager._get_drop_time(request)

    assert drop_time.hour == request.expected_drop_hour
    assert drop_time.minute == request.expected_drop_minute


@patch("resy_bot.manager.datetime")
@patch("resy_bot.manager.ResyManager.make_reservation_with_retries")
def test_make_reservation_at_opening_time(mock_make_reservation, mock_dt):
    now = datetime.now()
    mock_dt.now.return_value = now - timedelta(seconds=0.1)
    request = TimedReservationRequestFactory.create(
        expected_drop_hour=now.hour,
        expected_drop_minute=now.minute,
    )
    mock_dt.return_value = datetime(
        year=now.year,
        month=now.month,
        day=now.day,
        hour=now.hour,
        minute=now.minute,
    )

    config = ResyConfigFactory.create()
    mock_api_access = MagicMock()
    mock_selector = MagicMock()
    retry_config = ReservationRetriesConfig(
        seconds_between_retries=0.1,
        retry_duration=1,
    )

    manager = ResyManager(config, mock_api_access, mock_selector, retry_config)

    manager.make_reservation_at_opening_time(request)

    assert mock_dt.now.call_count == 3

    mock_make_reservation.assert_called_once()
