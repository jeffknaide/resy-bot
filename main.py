import argparse
import json
import dateparser
import datetime
import os

from resy_bot.logging import logging
from resy_bot.models import ResyConfig, TimedReservationRequest, WaitlistReservationRequest
from resy_bot.manager import ResyManager

from flask import Flask, request, Response

RESY_USER_CONFIG = os.getenv('RESY_USER_CONFIG')

logger = logging.getLogger(__name__)
logger.setLevel("INFO")

app = Flask(__name__)

### check for scheduled reserveations
def check_scheduled_reservations(reservation_data) -> str:
    scheduled_reservations = reservation_data["scheduled"]
    for restaurant in scheduled_reservations.items():
        pass
    return scheduled_reservations

### TODO create function to load from new config files
def load_reservations(resy_config_path: str, reservation_config_path: str) -> str:
    logger.info("loading reservation requests")
    
    config_data = json.load(RESY_USER_CONFIG)

    with open(reservation_config_path, "r") as f:
        reservation_data = json.load(f)

    config = ResyConfig(**config_data)
    manager = ResyManager.build(config)

    check_scheduled_reservations(reservation_data)

    #timed_request = TimedReservationRequest(**reservation_data)

    #return manager.make_reservation_at_opening_time(timed_request)


def wait_for_drop_time(resy_config_path: str, reservation_config_path: str) -> str:
    logger.info("waiting for drop time!")

    config_data = json.load(RESY_USER_CONFIG)

    with open(reservation_config_path, "r") as f:
        reservation_data = json.load(f)

    config = ResyConfig(**config_data)
    manager = ResyManager.build(config)

    timed_request = TimedReservationRequest(**reservation_data)

    return manager.make_reservation_at_opening_time(timed_request)

def get_waitlisted_table(resy_config_path: str, reservation_config_path: str, 
                         notification):
    
    logger.info("Looking for a reservation from incoming webhook")

    config_data = json.load(RESY_USER_CONFIG)

    with open(reservation_config_path, "r") as f:
        reservation_config = json.load(f)

    venue_name = notification[0].lower().replace(" ", "_")
    reservation_request = reservation_config["waitlisted"][venue_name]
    
    reservation_request["reservation_request"]["ideal_date"] = dateparser.parse(notification[1])
    reservation_request["reservation_request"]["party_size"] = int(notification[2].strip("Party of "))

    config = ResyConfig(**config_data)
    manager = ResyManager.build(config)

    ### Make request
    waitlist_request = WaitlistReservationRequest(**reservation_request)

    print(waitlist_request)
    #return manager.make_reservation_now(waitlist_request)

### Routes for Flask app
@app.route('/table-notification', methods=['POST'])
def respond():
    notification = request.json["available_table"]
    data = notification.split("|")
    notification = [x.strip(" \n") for x in data]
    
    get_waitlisted_table(RESY_USER_CONFIG, "reservation_configs/reservations.json", notification)
    return Response(status=200)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="ResyBot",
        description="Wait until reservation drop time and make one",
    )

    parser.add_argument("resy_config_path")
    parser.add_argument("reservation_config_path")

    args = parser.parse_args()

    ### wait_for_drop_time(args.resy_config_path, args.reservation_config_path)
    load_reservations(args.resy_config_path, args.reservation_config_path)
    
    app.run(debug = True, host = "0.0.0.0", port = 3000)