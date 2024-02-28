import argparse
import json
import dateparser
import datetime
import os

import resy_bot.scheduler as ap_scheduler

from config import Config

from resy_bot.logging import logging, Slogger
from resy_bot.models import ResyConfig, TimedReservationRequest, WaitlistReservationRequest
from resy_bot.manager import ResyManager

from flask import Flask, request, Response

config = Config()

RESY_USER_CONFIG = config.RESY_USER_CONFIG

logger = logging.getLogger(__name__)
logger.setLevel("INFO")

app = Flask(__name__)

scheduler = ap_scheduler.initialize()

slogger = Slogger()

## initialize scheduler
#scheduler = APScheduler()
#scheduler.api_enabled = True
#scheduler.init_app(app)
#scheduler.start()

### TODO create function to load from new config files
def load_reservations(reservation_config_path: str) -> str:
    logger.info("loading reservation requests")
    
    config_data = json.loads(RESY_USER_CONFIG)

    with open(reservation_config_path, "r") as f:
        reservation_data = json.load(f)

    config = ResyConfig(**config_data)
    manager = ResyManager.build(config)

    print("checking scheduled reservations")
    scheduled_reservations = reservation_data["scheduled"]
    restaurants = scheduled_reservations.keys()
    job_ids = []
    for r in restaurants:
        reservation_request = scheduled_reservations[r]
        logger.info(reservation_request)
        logger.info(f"Making a scheduled reservation drop for {reservation_request}")
        timed_request = TimedReservationRequest(**reservation_request)
        scheduler.add_job(manager.make_reservation_at_opening_time, args=[timed_request], trigger="cron", hour="7", id=r, replace_existing=True)
        job_ids.append(r)
    
    return job_ids

    #timed_request = TimedReservationRequest(**reservation_data)

    #return manager.make_reservation_at_opening_time(timed_request)


def get_waitlisted_table(resy_config_path: str, reservation_config_path: str, 
                         notification):
    
    logger.info("Looking for a reservation from incoming webhook")

    config_data = json.loads(RESY_USER_CONFIG)

    with open(reservation_config_path, "r") as f:
        reservation_config = json.load(f)

    venue_name = notification[0].lower().replace(" ", "_")
    reservation_request = reservation_config["waitlisted"][venue_name]
    ideal_date = dateparser.parse(notification[1])
    party_size = int(notification[2].strip(" Guests"))
    
    reservation_request["reservation_request"]["ideal_date"] = ideal_date
    reservation_request["reservation_request"]["party_size"] = party_size

    config = ResyConfig(**config_data)
    manager = ResyManager.build(config)

    slogger.slog(f"We've got a live one, making a request for {venue_name} on {ideal_date} for {party_size} -- fingers crossed!")
    ### Make request
    waitlist_request = WaitlistReservationRequest(**reservation_request)

    logger.info(waitlist_request)
    return manager.make_reservation_now(waitlist_request)

### Routes for Flask app
@app.route('/table-notification', methods=['POST'])
def respond():
    notification = request.json["available_table"]
    data = notification.split("|")
    notification = [x.strip(" \n") for x in data]
    
    get_waitlisted_table(RESY_USER_CONFIG, "reservation_configs/reservations.json", notification)
    return Response(status=200)


if __name__ == "__main__":

    ### wait_for_drop_time(args.resy_config_path, args.reservation_config_path)
    load_reservations("reservation_configs/reservations.json")
    app.run(debug = True, host = "0.0.0.0", port = 3000)