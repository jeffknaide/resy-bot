from apscheduler.schedulers.background import BackgroundScheduler
from resy_bot.logging import logging

def initialize():
    logger = logging.getLogger("Scheduler")
    logger.setLevel("INFO")
    scheduler = BackgroundScheduler(logger=logger, timezone='America/New_York')
    scheduler.start()
    return scheduler