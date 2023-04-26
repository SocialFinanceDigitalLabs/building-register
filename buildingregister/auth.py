import logging

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.contrib.auth.backends import BaseBackend

from register.models import LongLivedToken

User = get_user_model()
logger = logging.getLogger(__name__)


class BearerTokenAuthenticationMiddleware(BaseBackend):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.authenticate(request)
        response = self.get_response(request)
        return response

    def authenticate(self, request, **credentials):
        user = None
        try:
            header_value = request.headers["Authorization"]
        except KeyError:
            pass
        else:
            token_type, token = header_value.split(" ", 1)
            if token_type == "Bearer":
                try:
                    token_value = jwt.decode(
                        token, settings.SECRET_KEY, algorithms=["HS256"], verify=True
                    )
                except jwt.InvalidTokenError:
                    logger.exception("Invalid token")
                else:
                    user_id = token_value["sub"]
                    user = User.objects.get(id=user_id)
                    login(request, user)
                    print("User logged in via Bearer token", user)

        return user


class LongLivedTokenAuthenticationMiddleware(BaseBackend):
    """
    Allows for using long-lived tokens for authentication.

    Supply the token in the "Authorization" header, prepended with the string "LLToken ".
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.authenticate(request)
        response = self.get_response(request)
        return response

    def authenticate(self, request, **credentials):
        user = None
        try:
            header_value = request.headers["Authorization"]
        except KeyError:
            pass
        else:
            if header_value.startswith("LLToken "):
                token = header_value[8:]
                try:
                    user = LongLivedToken.objects.get(token=token).user
                    login(request, user)
                except LongLivedToken.DoesNotExist:
                    pass
                else:
                    login(request, user)

        return user
