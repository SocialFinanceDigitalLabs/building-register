import random
import secrets
import string
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.timezone import now
from ipware import get_client_ip

User = get_user_model()


class ContactValidationCodeManager(models.Manager):
    def create_code(
        self, details: "ContactDetails", expires: int = 15
    ) -> "ContactValidationCode":
        return super().create(
            details=details,
            code=100000 + secrets.randbelow(900000),
            expires=now() + timedelta(minutes=expires),
        )

    def validate_code(self, details: "ContactDetails", code: int):
        try:
            instance = super().get(details=details, code=code)
            instance.delete()
            return True
        except ContactValidationCode.DoesNotExist:
            return False


class ContactValidationCode(models.Model):
    details = models.ForeignKey("ContactDetails", on_delete=models.CASCADE)
    code = models.IntegerField()
    expires = models.DateTimeField()

    objects = ContactValidationCodeManager()


class ContactDetails(models.Model):
    value = models.CharField(max_length=200)
    method = models.CharField(max_length=5)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    audit = models.ForeignKey(
        "AuditRecord",
        on_delete=models.CASCADE,
        null=True,
        related_name="contact_details",
    )

    class Meta:
        unique_together = [["value", "method"]]
        verbose_name_plural = "Contact details"

    def __str__(self):
        return f"[{self.id}]: {self.method}={self.value} ({self.user})"


class AuditRecordManager(models.Manager):
    def create_from_request(self, request) -> "AuditRecord":
        ip, is_routable = get_client_ip(request)
        return super().create(ip=ip, user_agent=request.META.get("HTTP_USER_AGENT"))


class AuditRecord(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    ip = models.GenericIPAddressField(null=True)
    user_agent = models.CharField(max_length=255, null=True)

    objects = AuditRecordManager()

    def __str__(self):
        if self.ip:
            return f"{self.timestamp:%-d %b %Y %H:%M} ({self.ip})"
        return f"{self.timestamp}"


class SignInQueryset(models.QuerySet):
    def today(self):
        return self.filter(date=now())

    def open(self):
        return self.filter(sign_out__isnull=True)

    def closed(self):
        return self.filter(sign_out__isnull=False)

    def user(self, user):
        return self.filter(user=user)

    def sign_out(self, audit: AuditRecord):
        return self.update(sign_out=audit)


class SignInRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    sign_in = models.ForeignKey(
        AuditRecord, on_delete=models.CASCADE, related_name="sign_in"
    )
    sign_out = models.ForeignKey(
        AuditRecord, on_delete=models.CASCADE, null=True, related_name="sign_out"
    )

    @property
    def is_open(self):
        return self.sign_out is None

    objects = SignInQueryset().as_manager()

    class Meta:
        ordering = ["sign_in__timestamp"]
        get_latest_by = ["sign_in__timestamp"]
        permissions = [("view_report", "Can view reports of all records")]


class LongLivedTokenManager(models.Manager):
    word_tokens = string.ascii_letters + string.digits + "-_.~"

    def create_token(self, user: User) -> "LongLivedToken":
        token_text = "".join(random.choices(self.word_tokens, k=50))
        token, created = super().get_or_create(
            user=user, defaults=dict(token=token_text)
        )
        if not created:
            token.token = token_text
            token.save()
        return token


class LongLivedToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    token = models.CharField(max_length=50, unique=True, null=False, blank=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    objects = LongLivedTokenManager()


class UserSettings(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True, related_name="settings"
    )
    ricked = models.BooleanField(default=False)
