from datetime import datetime, timedelta
import time

from resy_bot.logging import logging
from resy_bot.errors import NoSlotsError, ExhaustedRetriesError
from resy_bot.constants import (
    SECONDS_TO_KEEP_RETRYING,
    SECONDS_TO_WAIT_BETWEEN_RETRIES,
)
from resy_bot.models import (
    ResyConfig,
    ReservationRequest,
    TimedReservationRequest,
    ReservationRetriesConfig,
)
from resy_bot.model_builders import (
    build_find_request_body,
    build_get_slot_details_body,
    build_book_request_body,
)
from resy_bot.api_access import ResyApiAccess
from resy_bot.selectors import AbstractSelector, SimpleSelector

logger = logging.getLogger(__name__)


class ResyManager:
    @classmethod
    def build(cls, config: ResyConfig) -> "ResyManager":
        api_access = ResyApiAccess.build(config)
        selector = SimpleSelector()
        retry_config = ReservationRetriesConfig(
            seconds_between_retries=SECONDS_TO_WAIT_BETWEEN_RETRIES,
            retry_duration=SECONDS_TO_KEEP_RETRYING,
        )
        return cls(config, api_access, selector, retry_config)

    def __init__(
        self,
        config: ResyConfig,
        api_access: ResyApiAccess,
        slot_selector: AbstractSelector,
        retry_config: ReservationRetriesConfig,
    ):
        self.config = config
        self.api_access = api_access
        self.selector = slot_selector
        self.retry_config = retry_config

    def get_venue_id(self, address: str):
        """
        TODO: get venue id from string address
            will use geolocator to get lat/long
        :return:
        """
        pass

    def make_reservation(self, reservation_request: ReservationRequest) -> str:
        body = build_find_request_body(reservation_request)

        slots = self.api_access.find_booking_slots(body)

        if len(slots) == 0:
            raise NoSlotsError("No Slots Found")
        else:
            logger.info(len(slots))
            logger.info(slots)

        selected_slot = self.selector.select(slots, reservation_request)

        logger.info(selected_slot)
        details_request = build_get_slot_details_body(
            reservation_request, selected_slot
        )
        logger.info(details_request)
        token = self.api_access.get_booking_token(details_request)

        booking_request = build_book_request_body(token, self.config)

        resy_token = self.api_access.book_slot(booking_request)

        return resy_token

    def make_reservation_with_retries(
        self, reservation_request: ReservationRequest
    ) -> str:
        cutoff = datetime.now() + timedelta(seconds=self.retry_config.retry_duration)
        # don't want microsecond rounding to have us requesting early
        while datetime.now() < cutoff:
            try:
                return self.make_reservation(reservation_request)

            except NoSlotsError:
                logger.info(
                    f"no slots, retry in {self.retry_config.seconds_between_retries} seconds"
                )
                time.sleep(self.retry_config.seconds_between_retries)

        raise ExhaustedRetriesError(
            f"Retried {self.retry_config.retry_duration} seconds, "
            "without finding a slot"
        )

    def _get_drop_time(self, reservation_request: TimedReservationRequest) -> datetime:
        now = datetime.now()
        return datetime(
            year=now.year,
            month=now.month,
            day=now.day,
            hour=reservation_request.expected_drop_hour,
            minute=reservation_request.expected_drop_minute,
        )

    def make_reservation_at_opening_time(
        self, reservation_request: TimedReservationRequest
    ) -> str:
        """
        cycle until we hit the opening time, then run & return the reservation
        """

        drop_time = self._get_drop_time(reservation_request)

        while True:
            early_start_td = timedelta(
                milliseconds=self.retry_config.seconds_between_retries
            )
            if datetime.now() < (drop_time - early_start_td):
                continue

            logger.info(f"time reached, making a reservation now! {datetime.now()}")
            return self.make_reservation_with_retries(
                reservation_request.reservation_request
            )
