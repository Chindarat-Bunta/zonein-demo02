from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("places/<int:place_id>/", views.place_detail, name="place_detail"),
    path("places/<slug:slug>/", views.place_detail, name="place_detail_slug"),
    path("api/places/<int:place_id>/", views.api_place_detail, name="api_place_detail"),
]
