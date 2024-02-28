import logging
import sys
import requests
from config import Config

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

config = Config()
SLACK_URL = config.SLACK_URL

class Slogger:
    def __init__(self) -> None:
        self.slack_url = SLACK_URL
        self.headers = {"Content-Type": "application/json"}


    def slog(self, message):
        url = self.slack_url
        headers = self.headers
        data = {"text": message}
        r = requests.post(url, headers=headers,  json=data)
        return r