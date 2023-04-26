import os

SLACK_WEBHOOKS = [
    url for url in os.environ.get("SLACK_SIGNIN_WEBHOOKS", "").split(" ") if url
]
