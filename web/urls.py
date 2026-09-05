from django.urls import path
from . import views

urlpatterns = [
    path("", views.profile_settings_view, name="home"),
    path("profile/settings/", views.profile_settings_view, name="profile_settings"),
    path("api/profile/update/", views.update_profile_api, name="update_profile_api"),
]
