import os
import requests

from .base import BaseApp


class Slack(BaseApp):
    def _alert(self, text):
        url = os.environ.get("SLACK_WEBHOOK_URL", None)
        requests.post(url, json={"text": text})
