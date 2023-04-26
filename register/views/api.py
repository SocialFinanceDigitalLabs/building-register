import json
import logging
import os

import jwt
import requests
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseForbidden, JsonResponse
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt

from register.models import AuditRecord, ContactDetails, SignInRecord
from register.util.auth import create_jwt_token, login

from .index import user_signed_in, user_signed_out

User = get_user_model()

logger = logging.getLogger(__name__)

VERIFY_APP_ID = os.environ.get("VERIFY_APP_ID")


@never_cache
def app_login(request):
    """
    Swaps a token from the Microsoft Graph API for a token from the Django auth system.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return HttpResponseForbidden("No Authorization header found")

    token_type, token_value = auth_header.split(" ", 1)
    if token_type != "Bearer":
        return HttpResponseForbidden("Invalid Authorization header type")

    try:
        token_fields = jwt.decode(token_value, options={"verify_signature": False})
    except jwt.DecodeError:
        logger.exception("Unable to decode token")
        return HttpResponseForbidden("Unable to decode token")

    if VERIFY_APP_ID and token_fields.get("appid") != VERIFY_APP_ID:
        logger.error(f"Incorrect appid in token: {token_fields.get('appid')}")
        return HttpResponseForbidden("Invalid token")

    response = requests.get(
        "https://graph.microsoft.com/v1.0/me", headers={"Authorization": auth_header}
    )
    response.raise_for_status()

    user_data = response.json()
    email = user_data["mail"].lower().strip()

    details, created = ContactDetails.objects.get_or_create(value=email, method="email")
    user = login(request, details, user_data["givenName"], user_data["surname"])

    return JsonResponse(
        dict(
            user_id=user.username,
            user_first_name=user.first_name,
            user_last_name=user.last_name,
            token=create_jwt_token(user),
        )
    )


@never_cache
@login_required
@csrf_exempt
@transaction.atomic
def app_status(request):
    """
    Returns the status of the signed-in-user.
    """
    signed_in = SignInRecord.objects.user(request.user).today().open()

    status_updated = False
    if request.method == "POST":
        request_data = json.loads(request.body)
        action = request_data.get("action")

        if action == "enter" and signed_in.count() == 0:
            audit = AuditRecord.objects.create_from_request(request)
            SignInRecord.objects.create(user=request.user, sign_in=audit)
            user_signed_in.send_robust(
                sender=SignInRecord, request=request, user=request.user, audit=audit
            )
            status_updated = True
        elif action == "exit" and signed_in.count() > 0:
            audit = AuditRecord.objects.create_from_request(request)
            signed_in.sign_out(audit)
            user_signed_out.send_robust(
                sender=SignInRecord, request=request, user=request.user, audit=audit
            )
            status_updated = True

    return JsonResponse(
        dict(
            in_office=signed_in.count() > 0,
            first_name=request.user.first_name,
            last_name=request.user.last_name,
            timestamp=timezone.now(),
            token=create_jwt_token(request.user),
            status_updated=status_updated,
        )
    )
