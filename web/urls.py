from django.urls import path
from . import views

app_name = "web"

urlpatterns = [
    path("", views.index_view, name="index"),
    path("places/", views.index_view, name="places_list"),
    path("places/<slug:slug>/", views.place_detail_view, name="place_detail"),
    path("api/places/", views.api_places_view, name="api_places"),
]
