from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.postgres.aggregates import StringAgg
from django.db import transaction
from django.db.models import Q, Max, Count
from django.db.models.functions import Lower

from .models import ContactDetails, ContactValidationCode, SignInRecord, AuditRecord, LongLivedToken, UserSettings

User = get_user_model()


class AuditRecordAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'ip', 'user_agent', 'sign_in_count', 'sign_out_count', 'contact_details_count')
    ordering = ('-timestamp',)

    def sign_in_count(self, obj):
        return obj.sign_in.count()

    def sign_out_count(self, obj):
        return obj.sign_out.count()

    def contact_details_count(self, obj):
        return obj.contact_details.count()


class ContactDetailsAdmin(admin.ModelAdmin):
    list_display = ('value', 'method', 'user', 'audit')


class ContactValidationCodeAdmin(admin.ModelAdmin):
    list_display = ('details', 'expires')


class SignInAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'sign_in', 'sign_out')


@admin.action(description='Merge users')
@transaction.atomic
def merge_users(modeladmin, request, queryset):
    users = queryset.order_by("date_joined")
    first_user = users[0]
    remainder = users[1:]

    ContactDetails.objects.filter(user__in=remainder).update(user=first_user)
    SignInRecord.objects.filter(user__in=remainder).update(user=first_user)

    User.objects.filter(id__in=[r.id for r in remainder]).delete()


@admin.action(description='Create token')
@transaction.atomic
def create_token(modeladmin, request, queryset):
    for user in queryset:
        LongLivedToken.objects.create_token(user)


class ContactDetailsInline(admin.TabularInline):
    model = ContactDetails
    fields = ('value', 'method', 'audit')

    extra = 0

    def has_change_permission(self, *args):
        return False


class UserSettingsInline(admin.TabularInline):
    model = UserSettings
    fields = ('ricked', )


class LongLivedTokenInline(admin.TabularInline):
    model = LongLivedToken
    fields = ('token', 'created')
    readonly_fields = ('token', 'created')


class LastActivityField(admin.DateFieldListFilter):
    pass


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'emails', 'phone', 'last_activity', 'is_staff', 'tokens')
    actions = (merge_users, create_token)
    inlines = (ContactDetailsInline, UserSettingsInline, LongLivedTokenInline)
    search_fields = ('username', 'first_name', 'last_name', 'emails', 'phone')
    readonly_fields = ('email',)

    @admin.display(description="Email", ordering='emails')
    def emails(self, obj):
        email = obj.emails
        if email:
            email = email.lower().replace('@socialfinance.org.uk', '@soc...')
        return email

    @admin.display(ordering='phone')
    def phone(self, obj):
        phone = obj.phone
        if phone:
            phone = phone.replace('+44', '0')
        return phone

    @admin.display(ordering='last_activity')
    def last_activity(self, obj):
        return obj.last_activity

    @admin.display(description="# Tokens", ordering='tokens')
    def tokens(self, obj):
        return obj.tokens if obj.tokens else ""

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(
            emails=StringAgg(Lower('contactdetails__value'), delimiter=', ',
                             filter=Q(contactdetails__method='email'), distinct=True),
            phone=StringAgg(Lower('contactdetails__value'), delimiter=', ',
                             filter=Q(contactdetails__method='sms'), distinct=True),
            last_activity=Max('signinrecord__date'),
            tokens=Count('longlivedtoken', distinct=True),
        )
        return qs


# Register your models here.
admin.site.register(ContactDetails, ContactDetailsAdmin)
admin.site.register(ContactValidationCode, ContactValidationCodeAdmin)
admin.site.register(SignInRecord, SignInAdmin)
admin.site.register(AuditRecord, AuditRecordAdmin)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
