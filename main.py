import argparse
import json
from resy_bot.logging import logging

from resy_bot.models import ResyConfig, TimedReservationRequest
from resy_bot.manager import ResyManager

logger = logging.getLogger(__name__)
logger.setLevel("INFO")


def wait_for_drop_time(resy_config_path: str, reservation_config_path: str) -> str:
    logger.info("waiting for drop time!")

    with open(resy_config_path, "r") as f:
        config_data = json.load(f)

    with open(reservation_config_path, "r") as f:
        reservation_data = json.load(f)

    config = ResyConfig(**config_data)
    manager = ResyManager.build(config)

    timed_request = TimedReservationRequest(**reservation_data)

    return manager.make_reservation_at_opening_time(timed_request)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="ResyBot",
        description="Wait until reservation drop time and make one",
    )

    parser.add_argument("resy_config_path")
    parser.add_argument("reservation_config_path")

    args = parser.parse_args()

    wait_for_drop_time(args.resy_config_path, args.reservation_config_path)
