from django import forms
from django.contrib.auth import get_user_model

from register.models import ContactDetails, ContactValidationCode

User = get_user_model()


class NoSpaceCharField(forms.CharField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_python(self, value):
        value = super().to_python(value)
        if value is not None:
            value = value.replace(" ", "")
        return value


class RegisterForm(forms.Form):
    contact_value = NoSpaceCharField(max_length=200, min_length=5)
    action = forms.CharField(widget=forms.HiddenInput(), required=False, initial="Test")


class ContactDetailsForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)

    class Meta:
        model = User
        fields = ["first_name", "last_name"]
