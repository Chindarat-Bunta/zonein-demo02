"""
URL configuration for zonein02 project.
"""

from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

from web import urls as web_urls

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("web.api.urls")),
    path("", include("web.urls", namespace="web")),
    path("", include((web_urls.urlpatterns, ""))),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

