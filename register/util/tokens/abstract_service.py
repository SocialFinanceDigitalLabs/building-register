from abc import ABC, abstractmethod

from django import forms
from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import redirect, render

from register.forms import NoSpaceCharField
from register.models import ContactDetails, ContactValidationCode
from register.util.auth import login

User = get_user_model()


class TokenService(ABC):
    template = "register/login_form.html"

    @property
    @abstractmethod
    def icon(self):
        return NotImplemented

    @property
    @abstractmethod
    def code(self):
        return NotImplemented

    @property
    @abstractmethod
    def label(self):
        return NotImplemented

    @property
    @abstractmethod
    def default_form(self):
        return NotImplemented

    @abstractmethod
    def handle_post(self, request):
        return NotImplemented

    def get_extra_context(self, request, form):
        return {}

    def handle_request(self, request):
        if request.method == "POST":
            return self.handle_post(request)
        else:
            form = self.default_form
            return self.form_response(request, form)

    def form_response(self, request, form, **kwargs):
        extra_context = {**kwargs, **self.get_extra_context(request, form)}
        return render(
            request, self.template, dict(form=form, method=self, **extra_context)
        )


class SendCodeForm(forms.Form):
    contact_value = NoSpaceCharField(max_length=200, label="Contact Details")
    action = forms.CharField(
        widget=forms.HiddenInput(), required=False, initial="register"
    )


class ValidateCodeForm(forms.Form):
    code = forms.IntegerField()
    action = forms.CharField(
        widget=forms.HiddenInput(), required=False, initial="validate"
    )
    contact_id = forms.IntegerField(widget=forms.HiddenInput())


class ValidateCodeWithContactForm(forms.ModelForm, ValidateCodeForm):
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    contact_form = forms.BooleanField(widget=forms.HiddenInput(), initial=True)

    class Meta:
        fields = ["first_name", "last_name"]
        model = User


class PingPongTokenService(TokenService):

    default_form = SendCodeForm
    validate_code_form = ValidateCodeForm
    validate_code_with_contact_form = ValidateCodeWithContactForm

    default_message = "Please enter your contact details to receive a token."
    validate_code_message = "Your code has now been printed on the console. Please enter your code to log in."
    validate_code_with_contact_message = (
        "Your code has now been sent. "
        "Please enter your name and code to set up your account."
    )

    @abstractmethod
    def send_code(self, request, code):
        return NotImplemented

    @abstractmethod
    def send_message(self, recipient, template, **context):
        return NotImplemented

    def get_extra_context(self, request, form):
        context = dict(**super().get_extra_context(request, form))
        if isinstance(form, self.validate_code_with_contact_form):
            context["message"] = self.validate_code_with_contact_message
        elif isinstance(form, self.validate_code_form):
            context["message"] = self.validate_code_message
        else:
            context["message"] = self.default_message

        return context

    def handle_post(self, request):
        action = request.POST.get("action")
        if action == "register":
            return self.handle_register(request)
        elif action == "validate":
            return self.handle_validate(request)
        else:
            return self.form_response(request, self.default_form)

    @transaction.atomic
    def handle_register(self, request):
        form = self.default_form(request.POST)
        if form.is_valid():
            contact_value = self.validate_contact_value(form)
            if contact_value is not None:
                details, created = ContactDetails.objects.get_or_create(
                    value=contact_value, method=self.code
                )
                code = ContactValidationCode.objects.create_code(details)
                self.send_code(request, code)
                if details.user:
                    form = self.validate_code_form(initial=dict(contact_id=details.pk))
                else:
                    form = self.validate_code_with_contact_form(
                        initial=dict(contact_id=details.pk)
                    )

        return self.form_response(request, form)

    def handle_validate(self, request):
        if request.POST.get("contact_form"):
            form = self.validate_code_with_contact_form(request.POST)
        else:
            form = self.validate_code_form(request.POST)

        if form.is_valid():
            details_pk = form.cleaned_data["contact_id"]
            details = ContactDetails.objects.get(pk=details_pk)
            code = form.cleaned_data["code"]
            if ContactValidationCode.objects.validate_code(details, code):
                login(
                    request,
                    details,
                    form.cleaned_data.get("first_name"),
                    form.cleaned_data.get("last_name"),
                )
                return redirect("index")
            else:
                form.add_error("code", "Code not found.")
        return self.form_response(request, form)

    def validate_contact_value(self, form):
        return form.cleaned_data["contact_value"]
