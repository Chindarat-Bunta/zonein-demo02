from django.urls import path, include

urlpatterns = [
    path("api/", include("web.api.urls")),
]
