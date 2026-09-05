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
    path("api/posts/<int:post_id>/comments/", api_views.post_comments_list_create_view, name="api_post_comments"),
    path("api/posts/<int:post_id>/comments/<int:comment_id>/", api_views.post_comment_delete_view, name="api_post_comment_delete"),

    # Follow / Unfollow APIs
    path("api/users/<int:user_id>/follow/", api_views.toggle_follow_view, name="api_user_follow"),
    path("api/users/<int:user_id>/follow-status/", api_views.user_follow_status_view, name="api_user_follow_status"),
    path("api/users/<int:user_id>/followers/", api_views.user_followers_list_view, name="api_user_followers"),
    path("api/users/<int:user_id>/following/", api_views.user_following_list_view, name="api_user_following"),

    # Backward compatibility aliases
    path("api/reviews/", api_views.travel_posts_list_create_view, name="api_reviews"),
    path("api/reviews/<int:post_id>/", api_views.travel_post_detail_view, name="api_review_detail"),
]


