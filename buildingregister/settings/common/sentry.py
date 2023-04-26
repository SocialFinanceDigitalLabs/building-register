import os

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_dsn = os.environ.get("SENTRY_DSN")
sentry_sample_rate = float(os.environ.get("SENTRY_SAMPLE_RATE", "1.0"))

if sentry_dsn:
    sentry_sdk.init(
        dsn=sentry_dsn,
        integrations=[DjangoIntegration()],
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=sentry_sample_rate,
        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        send_default_pii=True,
    )
