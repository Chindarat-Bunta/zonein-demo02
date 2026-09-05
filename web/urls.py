from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("signin/", views.signin_view, name="signin"),
    path("login/", views.signin_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),
    path("social-login/<str:provider>/", views.social_login_view, name="social_login"),
    path("api/", include("web.api.urls")),
]

