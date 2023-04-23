import argparse
import json
from resy_bot.logging import logging

from resy_bot.models import (
    ResyConfig,
    TimedReservationRequest,
    TimedRepeatedReservationRequest,
)
from resy_bot.model_builders import build_timed_reservation_request
from resy_bot.manager import ResyManager

logger = logging.getLogger(__name__)


def wait_for_drop_time(
    resy_config_path: str, reservation_config_path: str, repeated_request: bool
) -> str:
    """
    top level function for executing reservation request

    :param resy_config_path:
        path to config for resy account
    :param reservation_config_path:
        path to config for restaurant
    :param repeated_request:
        allows for requests that simply specify the number of
         days until reservation date. this allows for repeated requests to the
         same restaurant if e.g. you were unsuccessful the first attempt
    :return:
    """
    logger.info("waiting for drop time!")

    with open(resy_config_path, "r") as f:
        config_data = json.load(f)

    with open(reservation_config_path, "r") as f:
        reservation_data = json.load(f)

    config = ResyConfig(**config_data)
    manager = ResyManager.build(config)

    if repeated_request:
        request = TimedRepeatedReservationRequest(**reservation_data)
        timed_request = build_timed_reservation_request(request)
    else:
        timed_request = TimedReservationRequest(**reservation_data)

    return manager.make_reservation_at_opening_time(timed_request)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="ResyBot",
        description="Wait until reservation drop time and make one",
    )

    parser.add_argument("resy_config_path")
    parser.add_argument("reservation_config_path")
    parser.add_argument(
        "--repeated_request",
        help="calculate resy date based on a time from now",
        action="store_true",
    )

    args = parser.parse_args()

    wait_for_drop_time(
        args.resy_config_path, args.reservation_config_path, args.repeated_request
    )
