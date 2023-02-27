import json

from resy_bot.models import ResyConfig, TimedReservationRequest
from resy_bot.manager import ResyManager


def wait_for_drop_time(reservation_config_path):
    with open("local.json", "r") as f:
        config_data = json.load(f)

    with open(reservation_config_path, "r") as f:
        reservation_data = json.load(f)

    config = ResyConfig(**config_data)
    manager = ResyManager.build(config)

    timed_request = TimedReservationRequest(**reservation_data)

    return manager.make_reservation_at_opening_time(timed_request)


# if __name__ == "__main__":
