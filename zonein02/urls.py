"""
URL configuration for zonein02 project.
"""

from django.contrib import admin
from django.urls import include, path
from web import urls as web_urls

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("web.api.urls")),
    path("", include("web.urls", namespace="web")),
    path("", include((web_urls.urlpatterns, ""))),
]
