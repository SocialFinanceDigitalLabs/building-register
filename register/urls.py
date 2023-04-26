from django.urls import path

from . import views
from .views import auth, profile, report

urlpatterns = [
    path("accounts/login/", auth.login, name="login"),
    path("accounts/logout/", auth.logout, name="logout"),
    path("accounts/login/<str:method>", auth.login_form, name="login_form"),
    path("accounts/token/<str:token>", auth.login_token, name="login_token"),
    path("profile", profile.profile, name="profile"),
    path("profile/createurl", profile.create_url, name="profile_create_url"),
    path("report", report.report, name="report"),
    path("report.json", report.report_json, name="report_json"),
    path("", views.index, name="index"),
]
