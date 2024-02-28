from datetime import datetime, timedelta

from resy_bot.logging import logging, Slogger
from resy_bot.errors import NoSlotsError, ExhaustedRetriesError
from resy_bot.constants import (
    N_RETRIES,
    SECONDS_TO_WAIT_BETWEEN_RETRIES,
)
from resy_bot.models import (
    ResyConfig,
    ReservationRequest,
    TimedReservationRequest,
    WaitlistReservationRequest,
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
logger.setLevel("INFO")

slogger = Slogger()

class ResyManager:
    @classmethod
    def build(cls, config: ResyConfig) -> "ResyManager":
        api_access = ResyApiAccess.build(config)
        selector = SimpleSelector()
        retry_config = ReservationRetriesConfig(
            seconds_between_retries=SECONDS_TO_WAIT_BETWEEN_RETRIES,
            n_retries=N_RETRIES,
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

    def format_notification_request(self, request_info):
        pass

    def make_reservation(self, reservation_request: ReservationRequest) -> str:
        body = build_find_request_body(reservation_request)

        slots = self.api_access.find_booking_slots(body)
        logger.info(f"Returned: {slots}")

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
        for _ in range(self.retry_config.n_retries):
            try:
                return self.make_reservation(reservation_request)

            except NoSlotsError:
                logger.info(
                    f"no slots, retrying; currently {datetime.now().isoformat()}"
                )

        raise ExhaustedRetriesError(
            f"Retried {self.retry_config.n_retries} times, " "without finding a slot"
        )

    def _get_drop_time(self, reservation_request: TimedReservationRequest) -> datetime:
        now = datetime.now()
        return datetime(
            year=now.year,
            month=now.month,
            day=now.day,
            hour=reservation_request.reservation_request.expected_drop_hour,
            minute=reservation_request.reservation_request.expected_drop_minute,
        )

    def make_reservation_at_opening_time(
        self, reservation_request: TimedReservationRequest
    ) -> str:
        """
        cycle until we hit the opening time, then run & return the reservation
        """
        drop_time = self._get_drop_time(reservation_request)
        last_check = datetime.now()

        slogger(f"Starting up the droptime engine for {reservation_request["venue_name"]} -- waiting until drop time")

        while True:
            if datetime.now() < drop_time:
                if datetime.now() - last_check > timedelta(seconds=10):
                    logger.info(f"{datetime.now()}: still waiting")
                    last_check = datetime.now()
                continue
            elif datetime.now() > drop_time + timedelta(hours=1):
                if datetime.now() - last_check > timedelta(seconds=10):
                    logger.info(f"{datetime.now()}: still waiting")
                    last_check = datetime.now()
                continue

            logger.info(f"time reached, making a reservation now! {datetime.now()}")
            slogger(f"It's go time -- trying to make a reservation for {reservation_request["venue_name"]}")
            return self.make_reservation_with_retries(
                reservation_request.reservation_request
            )

    def make_reservation_now(
        self, reservation_request: WaitlistReservationRequest
    ) -> str:
        """
        cycle until we hit the opening time, then run & return the reservation
        """
        while True:
            logger.info(f"making a reservation now! {datetime.now()}")
            return self.make_reservation_with_retries(
                reservation_request.reservation_request
            )
