from django.urls import path
from . import views

app_name = "web"

urlpatterns = [
    # Home Page Feed
    path("", views.home_view, name="home"),

    # Backend APIs for Home Page Feed
    path("api/places/popular/", views.api_popular_places, name="api_popular_places"),
    path("api/places/<int:place_id>/", views.api_place_detail, name="api_place_detail"),
    path("api/reviews/recent/", views.api_recent_reviews, name="api_recent_reviews"),
    path("api/reviews/<int:review_id>/", views.api_review_detail, name="api_review_detail"),
    path("api/reviews/<int:review_id>/comments/", views.api_add_comment, name="api_add_comment"),
    path("api/reviews/<int:review_id>/edit/", views.api_edit_review, name="api_edit_review"),
    path("api/reviews/<int:review_id>/delete/", views.api_delete_review, name="api_delete_review"),
]
