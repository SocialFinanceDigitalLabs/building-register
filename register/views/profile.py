from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotAllowed
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache

from register.forms import ContactDetailsForm
from register.models import LongLivedToken


@login_required
@never_cache
def profile(request):
    if request.method == "POST":
        form = ContactDetailsForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
    else:
        form = ContactDetailsForm(instance=request.user)

    return render(request, "register/profile.html", dict(form=form))


@login_required
@never_cache
def create_url(request):
    if request.method == "POST":
        LongLivedToken.objects.create_token(request.user)
        return redirect("profile")
    else:
        return HttpResponseNotAllowed(["POST"])
