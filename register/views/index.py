import logging

from django import dispatch
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect
from django.utils.timezone import now
from django.views.decorators.cache import never_cache
from register.models import SignInRecord, AuditRecord

logger = logging.getLogger(__name__)

user_signed_in = dispatch.Signal()
user_signed_out = dispatch.Signal()


@transaction.atomic
def _handle_sign_in_out(request):
    signed_in = SignInRecord.objects.user(request.user).today().open()
    audit = AuditRecord.objects.create_from_request(request)
    action = request.POST.get('action')
    date = request.POST.get('date')
    today = now().date().isoformat()
    if date != today:
        return messages.ERROR, f"Sorry, you attempted to {action} for the wrong date."

    if action == "sign-in" and signed_in.count() == 0:
        SignInRecord.objects.create(user=request.user, sign_in=audit)
        user_signed_in.send_robust(sender=SignInRecord, request=request, user=request.user, audit=audit)
        return messages.SUCCESS, "You have successfully signed in. Don't forget to sign out when you leave."
    elif action == "sign-out":
        signed_in.sign_out(audit)
        user_signed_out.send_robust(sender=SignInRecord, request=request, user=request.user, audit=audit)
        return messages.SUCCESS, "You have successfully signed out. See you again soon!"


@login_required
@never_cache
def index(request):
    context = {}
    if request.method == 'POST':
        level, text = _handle_sign_in_out(request)
        messages.add_message(request, level, text)
        return redirect('index')

    todays_records = SignInRecord.objects.user(request.user).today()
    signed_in_records = todays_records.open()

    return render(request, 'register/index.html', dict(
        today=now().date().isoformat(),
        todays_records=todays_records,
        signed_in_records=signed_in_records,
        user=request.user,
        **context,
    ))
