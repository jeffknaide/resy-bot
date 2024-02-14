import argparse
import json
import dateparser
from resy_bot.logging import logging

from resy_bot.models import ResyConfig, TimedReservationRequest, WaitlistReservationRequest
from resy_bot.manager import ResyManager

from flask import Flask, request, Response


logger = logging.getLogger(__name__)
logger.setLevel("INFO")

app = Flask(__name__)

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

def get_waitlisted_table(resy_config_path: str, waitlist_config_path: str, notification_data) -> str:
    logger.info("Looking for a reservation from incoming webhook")

    with open(resy_config_path, "r") as f:
        config_data = json.load(f)

    with open(waitlist_config_path, "r") as f:
        waitlist_data = json.load(f)

    venue_name = notification_data[0].lower().replace(" ", "_")
    venue_id = waitlist_data[venue_name]["venue_id"]
    reservation_date = dateparser.parse(notification_data[1])
    party_size = notification_data[2].strip("Party of ")

    waitlist_data["party_size"] = party_size

    print(reservation_date.hour, reservation_date.minute)
    print(notification_data, venue_name, venue_id, reservation_date, party_size, waitlist_data)
    config = ResyConfig(**config_data)
    manager = ResyManager.build(config)



    ### Make request
    waitlist_request = WaitlistReservationRequest(**reservation_data)

    return manager.make_reservation_now(waitlist_request)

### Routes for Flask app
@app.route('/table-notification', methods=['POST'])
def respond():
    notification = request.json["available_table"]
    data = notification.split("|")
    reservation_info = [x.strip(" \n") for x in data]
    
    get_waitlisted_table("local.json", "reservation_configs/waitlist.json", reservation_info)
    print(request.json)
    return Response(status=200)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="ResyBot",
        description="Wait until reservation drop time and make one",
    )

    parser.add_argument("resy_config_path")
    parser.add_argument("reservation_config_path")

    args = parser.parse_args()

    app.run(debug = True, host = "0.0.0.0", port = 3000)


    ### wait_for_drop_time(args.resy_config_path, args.reservation_config_path)
