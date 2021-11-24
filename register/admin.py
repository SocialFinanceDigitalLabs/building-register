from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.db import transaction

from .models import ContactDetails, ContactValidationCode, SignInRecord, AuditRecord, LongLivedToken

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


class LongLivedTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'created', 'modified')


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


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'is_staff')
    actions = (merge_users, create_token)
    inlines = (ContactDetailsInline,)


# Register your models here.
admin.site.register(ContactDetails, ContactDetailsAdmin)
admin.site.register(ContactValidationCode, ContactValidationCodeAdmin)
admin.site.register(SignInRecord, SignInAdmin)
admin.site.register(AuditRecord, AuditRecordAdmin)
admin.site.register(LongLivedToken, LongLivedTokenAdmin)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
