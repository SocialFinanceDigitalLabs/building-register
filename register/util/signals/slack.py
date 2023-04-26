import logging

from django.conf import settings
from django.dispatch import receiver
from slack_sdk import WebhookClient

from register.models import SignInRecord
from register.views.index import user_signed_in, user_signed_out

logger = logging.getLogger(__name__)


def _send_message(user, direction):
    signed_in_users = SignInRecord.objects.today().open()
    message = (
        f"User {user.first_name} {user.last_name} signed {direction}. "
        f"There are now {signed_in_users.count()} users signed in."
    )
    for webhook in settings.SLACK_WEBHOOKS:
        client = WebhookClient(webhook)
        client.send(text=message)


@receiver(user_signed_in)
def slack_send_signin(sender, user=None, **kwargs):
    _send_message(user, "in")


@receiver(user_signed_out)
def slack_send_signout(sender, user=None, **kwargs):
    _send_message(user, "out")
