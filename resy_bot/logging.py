import logging
import sys
import requests

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

class Slogger:
    def __init__(self, slack_url) -> None:
        self.slack_url = slack_url
        self.headers = {"Content-Type": "application/json"}


    def slog(self, message):
        url = self.slack_url
        headers = self.headers
        data = {"text": message}
        r = requests.post(url, headers=headers,  json=data)
        return r