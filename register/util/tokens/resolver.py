from django.utils.module_loading import import_string

DEFAULT_SERVICES = [
    "register.util.tokens.DevelopmentConsoleService",
    "register.util.tokens.Office365EmailService",
    "register.util.tokens.TwilioSMSService",
]

token_services = {
    s.code: s
    for s in [import_string(srv)() for srv in DEFAULT_SERVICES]
    if s.configured
}


def get_token_method(method: str) -> "register.util.tokens.TokenService":
    return token_services[method]
