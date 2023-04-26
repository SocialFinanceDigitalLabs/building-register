from django import forms
from django.conf import settings
from django.template.loader import render_to_string
from twilio.base.exceptions import TwilioRestException

from register.util.tokens.abstract_service import PingPongTokenService, SendCodeForm

SENDER_NAME = "SF-REG"


class TwilioCodeForm(SendCodeForm):
    contact_value = forms.CharField(max_length=15, label="Phone Number")


class TwilioSMSService(PingPongTokenService):
    code = "sms"
    icon = "smartphone"
    label = "Text Message"

    default_form = TwilioCodeForm

    default_message = """
    You are registering using text message. Please enter a UK phone number to receive your one-time token.
    """

    validate_code_message = f"""
    Your code has now been sent. Keep a look out for a message from '{SENDER_NAME}'.
    Please enter your code to log in.
    """

    validate_code_with_contact_message = f"""
    Your code has now been sent. Keep a look out for a message from '{SENDER_NAME}'. 
    Please enter your name and code to set up your account.
    """

    @property
    def configured(self):
        return hasattr(settings, "TWILIO_CLIENT")

    def validate_contact_value(self, form):
        contact_value = form.cleaned_data["contact_value"]
        try:
            result = settings.TWILIO_CLIENT.lookups.phone_numbers(contact_value).fetch(
                country_code="gb"
            )
            return result.phone_number
        except TwilioRestException as e:
            form.add_error(
                "contact_value",
                "This does not appear to be a correctly formatted UK phone number",
            )
            return None

    def send_code(self, request, code):
        self.send_message(code.details.value, "login", code=code.code)

    def send_message(self, recipient, template, **context):
        body_content = render_to_string(
            f"register/messaging/sms/{template}.txt", context
        )
        settings.TWILIO_CLIENT.messages.create(
            body=body_content, from_=SENDER_NAME, to=recipient
        )
