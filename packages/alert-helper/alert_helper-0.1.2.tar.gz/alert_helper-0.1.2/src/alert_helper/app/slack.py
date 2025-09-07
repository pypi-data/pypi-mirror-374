import os
import requests


def call_slack(text: str):
    url = os.environ.get("SLACK_WEBHOOK_URL", None)
    requests.post(url, json={"text": text})
