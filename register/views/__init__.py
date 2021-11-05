import logging

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render
from ipware import get_client_ip

from register.forms import ContactDetailsForm
from register.models import SignInRecord, AuditRecord

logger = logging.getLogger(__name__)


@transaction.atomic
def _handle_sign_in_out(request):
    ip, is_routable = get_client_ip(request)
    signed_in = SignInRecord.objects.user(request.user).today().open()
    audit = AuditRecord.objects.create(ip=ip, user_agent=request.META.get('HTTP_USER_AGENT'))
    action = request.POST.get('action')

    if action == "sign-in" and signed_in.count() == 0:
        form = ContactDetailsForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            SignInRecord.objects.create(user=request.user, sign_in=audit)
        return form

    elif action == "sign-out":
        signed_in.sign_out(audit)


@login_required
def index(request):
    form = None
    if request.method == 'POST':
        form = _handle_sign_in_out(request)

    if form is None:
        form = ContactDetailsForm(instance=request.user)

    todays_records = SignInRecord.objects.user(request.user).today()
    signed_in_records = todays_records.open()

    return render(request, 'register/index.html', dict(
        form=form,
        todays_records=todays_records,
        signed_in_records=signed_in_records,
        user=request.user,
    ))
