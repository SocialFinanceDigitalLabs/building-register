import logging

from django.http import HttpResponseNotFound, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, logout as auth_logout, login as auth_login
from django.views.decorators.cache import never_cache

from register.models import LongLivedToken
from register.util.tokens.resolver import token_services, get_token_method

User = get_user_model()

logger = logging.getLogger(__name__)


@never_cache
def login(request):
    return render(request, 'register/login.html', dict(methods=token_services))


@never_cache
def logout(request):
    auth_logout(request)
    return redirect("index")


@never_cache
def login_form(request, method):
    method = get_token_method(method)
    if not method:
        return HttpResponseNotFound('<h1>Login method not found</h1>')

    return method.handle_request(request)


@never_cache
def login_token(request, token: str):
    try:
        token = LongLivedToken.objects.get(token=token)
    except LongLivedToken.DoesNotExist:
        return HttpResponseForbidden()

    auth_login(request, token.user)
    return redirect('index')
