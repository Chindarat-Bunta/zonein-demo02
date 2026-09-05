from django.urls import path
from . import views, places, reviews, wishlist, likes, profile

urlpatterns = [
    # API Documentation & Health Check
    path("", views.api_root, name="api_root"),
    path("health/", views.health_check, name="api_health"),

    # Places / Posts
    path("places/", places.places_list_create, name="api_places"),
    path("places/<int:place_id>/", places.place_detail, name="api_place_detail"),

    # Reviews & Ratings
    path("places/<int:place_id>/reviews/", reviews.place_reviews_list_create, name="api_place_reviews"),

    # Likes & Hearts
    path("places/<int:place_id>/like/", likes.like_toggle, name="api_place_like"),

    # Wishlist (Favorites)
    path("wishlist/", wishlist.wishlist_list, name="api_wishlist"),
    path("wishlist/toggle/", wishlist.wishlist_toggle, name="api_wishlist_toggle"),

    # Profile
    path("profile/", profile.profile_detail_update, name="api_profile"),
]
