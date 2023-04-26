import logging
from datetime import timedelta

from dateutil.utils import today
from django.contrib.auth import get_user_model

from register.models import AuditRecord, ContactDetails, SignInRecord
from register.util.tokens import get_token_method

User = get_user_model()


logger = logging.getLogger(__name__)


def send_reminders(send=False, template="reminder"):
    signed_in = SignInRecord.objects.today().open().values("user")
    detail_query = ContactDetails.objects.filter(
        user__in=signed_in, audit__isnull=False
    )

    for detail in detail_query:
        if send:
            try:
                method = get_token_method(detail.method)
                method.send_message(detail.value, template)
            except:
                logger.exception(f"Could not send reminder to: {detail}")
        else:
            logger.info(detail)


def clean_old_records(days=30):
    start_date = today() - timedelta(days=days)
    records = SignInRecord.objects.filter(date__lt=start_date).delete()
    logger.info("Cleaned %s sign-in records older than %s", records, start_date)

    records = User.objects.filter(
        signinrecord__isnull=True, groups__isnull=True
    ).delete()
    logger.info("Cleaned %s user records older than %s", records, start_date)

    records = AuditRecord.objects.filter(
        sign_in__isnull=True,
        sign_out__isnull=True,
        contact_details__isnull=True,
    ).delete()

    logger.info("Cleaned %s audit records older than %s", records, start_date)
