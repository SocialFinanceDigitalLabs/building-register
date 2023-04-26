import re

from django.contrib.auth import get_user_model
from django.contrib.auth import login as auth_login
from django.db import transaction

from register.models import AuditRecord, ContactDetails

_username_pattern = re.compile(r"[^a-zA-Z09]")

User = get_user_model()


def get_username(first_name: str, last_name: str) -> str:
    first_name = _username_pattern.sub("", first_name).lower()
    last_name = _username_pattern.sub("", last_name).lower()
    return f"{first_name}.{last_name}"


def get_unique_username(first_name: str, last_name: str) -> str:
    username = get_username(first_name, last_name)
    unique_username = (0, username)
    while User.objects.filter(username=unique_username[1]).count() > 0:
        sequence = unique_username[0] + 1
        unique_username = (sequence, f"{username}.{sequence}")
    return unique_username[1]


@transaction.atomic
def login(request, details: ContactDetails, first_name: str, last_name: str) -> User:
    # Sign-in or create the current user
    if details.user is None:
        username = get_unique_username(first_name, last_name)
        details.user = User.objects.create(
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
    audit = AuditRecord.objects.create_from_request(request)
    details.audit = audit
    details.save()

    auth_login(request, details.user)
    return details.user
