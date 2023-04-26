from dateutil.parser import parse
from django.contrib.auth.decorators import permission_required
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.cache import never_cache

from register.models import SignInRecord, User


@permission_required("register.view_report")
@never_cache
def report(request):
    todays_records = SignInRecord.objects.today().order_by(
        "user__first_name", "user__last_name", "sign_in__timestamp"
    )
    signed_in_records = todays_records.open()
    signed_out_records = todays_records.closed()
    context = dict(
        todays_records=todays_records,
        signed_in_records=signed_in_records,
        signed_out_records=signed_out_records,
    )
    return render(request, "register/report.html", context)


@permission_required("register.view_report")
@never_cache
def report_json(request):
    for_date = request.GET.get("date")
    if for_date:
        for_date = parse(for_date)
    else:
        for_date = timezone.now()
    todays_users = (
        User.objects.filter(
            pk__in=SignInRecord.objects.filter(date=for_date).values_list(
                "user", flat=True
            )
        )
        .prefetch_related("contactdetails_set")
        .order_by("first_name", "last_name")
    )

    signed_in_users = User.objects.filter(
        pk__in=SignInRecord.objects.filter(date=for_date)
        .open()
        .values_list("user", flat=True)
    )
    context = dict(
        users=[
            dict(
                first_name=user.first_name,
                last_name=user.last_name,
                emails=list(
                    user.contactdetails_set.filter(method="email").values_list(
                        "value", flat=True
                    )
                ),
                phones=list(
                    user.contactdetails_set.filter(method="sms").values_list(
                        "value", flat=True
                    )
                ),
                status="signed-in" if user in signed_in_users else "signed-out",
                records=list(
                    user.signinrecord_set.filter(date=for_date)
                    .order_by("sign_in__timestamp")
                    .values("sign_in__timestamp", "sign_out__timestamp")
                ),
            )
            for user in todays_users
        ]
    )
    return JsonResponse(context)
