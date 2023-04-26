from django.conf import settings
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string

from register.util.tokens.abstract_service import PingPongTokenService, SendCodeForm

User = get_user_model()


class DevelopmentConsoleService(PingPongTokenService):
    code = "dev"
    icon = "engineering"
    label = "Development"

    default_message = """
    You are registering using a development token. To get this token you need console access on the development server.
    To emulate a token validation failure, use the details 'fail'.
    """

    validate_code_message = """
    Your code has now been printed on the console. Please enter your code to log in.
    """

    validate_code_with_contact_message = """
    Your code has now been printed on the console. Please enter your name and code to set up your account.
    """

    @property
    def configured(self):
        return settings.DEBUG

    def validate_contact_value(self, form):
        contact_value = form.cleaned_data["contact_value"]
        if contact_value == "fail":
            form.add_error("contact_value", "This is a sample validation error")
            return None
        return contact_value

    def send_code(self, request, code):
        self.send_message(code.details.value, "login", code=code.code)

    def send_message(self, recipient, template, **context):
        body_content = render_to_string(
            f"register/messaging/dev/{template}.txt", context
        )
        print(f"{recipient}: {body_content}")
