from typing import List

from django.utils.module_loading import import_string

DEFAULT_SERVICES = [
    "register.util.tokens.DevelopmentConsoleService",
    "register.util.tokens.Office365EmailService",
    "register.util.tokens.TwilioSMSService",
]

__cached_services = None


def __load_services():
    global __cached_services
    __cached_services = {
        s.code: s
        for s in [import_string(srv)() for srv in DEFAULT_SERVICES]
        if s.configured
    }


def get_services() -> List["register.util.tokens.TokenService"]:
    if not __cached_services:
        __load_services()
    return __cached_services


def get_token_method(method: str) -> "register.util.tokens.TokenService":
    if not __cached_services:
        __load_services()
    return __cached_services[method]
