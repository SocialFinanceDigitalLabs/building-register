from django.contrib.auth import login
from django.contrib.auth.backends import BaseBackend

from register.models import LongLivedToken


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
