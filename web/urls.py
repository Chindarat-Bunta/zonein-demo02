from django.urls import path
from . import api_views, views

app_name = "web"

urlpatterns = [
    # UI Traveler Feed
    path("", views.home_view, name="home"),

    # Travel Posts & Reviews APIs (CRUD, 1-5 Star Ratings, Place Tags)
    path("api/posts/", api_views.travel_posts_list_create_view, name="api_posts"),
    path("api/posts/<int:post_id>/", api_views.travel_post_detail_view, name="api_post_detail"),
    path("api/posts/<int:post_id>/like/", api_views.toggle_post_like_view, name="api_post_like"),
    path("api/posts/<int:post_id>/likes/", api_views.post_likes_list_view, name="api_post_likes"),

    # Backward compatibility aliases
    path("api/reviews/", api_views.travel_posts_list_create_view, name="api_reviews"),
    path("api/reviews/<int:post_id>/", api_views.travel_post_detail_view, name="api_review_detail"),
]


