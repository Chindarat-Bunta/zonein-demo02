from django.urls import include, path
from . import views

app_name = "web"

urlpatterns = [
    # Pages
    path("", views.home_view, name="index"),
    path("home/", views.home_view, name="home"),
    path("feed/", views.home_view, name="feed"),
    path("search/", views.search_view, name="search"),
    path("explore/", views.search_view, name="explore"),
    path("wishlist/", views.wishlist_page_view, name="wishlist"),
    path("profile/", views.profile_view, name="profile"),
    path("profile/settings/", views.profile_settings_view, name="profile_settings"),
    path("profile/<str:username>/", views.profile_view, name="profile_user"),
    path("places/", views.home_view, name="places_list"),
    path("signin/", views.signin_view, name="signin"),
    path("login/", views.signin_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),
    path("social-login/<str:provider>/", views.social_login_view, name="social_login"),
    path(
        "social-login/<str:provider>/callback/",
        views.social_login_callback_view,
        name="social_login_callback",
    ),
    path(
        "social-login/<str:provider>/consent/",
        views.social_login_consent_view,
        name="social_login_consent",
    ),
    path("privacy-policy/", views.privacy_policy_view, name="privacy_policy"),
    path("terms/", views.terms_view, name="terms"),
    # REST APIs
    path("api/profile/update/", views.update_profile_api, name="update_profile_api"),
    path("api/places/", views.api_places_view, name="api_places"),
    path("api/places/popular/", views.api_popular_places, name="api_popular_places"),
    path("api/places/<int:place_id>/", views.api_place_detail, name="api_place_detail"),
    path("api/reviews/recent/", views.api_recent_reviews, name="api_recent_reviews"),
    path(
        "api/reviews/<int:review_id>/",
        views.api_review_detail,
        name="api_review_detail",
    ),
    path(
        "api/reviews/<int:review_id>/comments/",
        views.api_add_comment,
        name="api_add_comment",
    ),
    path(
        "api/comments/<int:comment_id>/edit/",
        views.api_edit_comment,
        name="api_edit_comment",
    ),
    path(
        "api/comments/<int:comment_id>/delete/",
        views.api_delete_comment,
        name="api_delete_comment",
    ),
    path(
        "api/reviews/<int:review_id>/edit/",
        views.api_edit_review,
        name="api_edit_review",
    ),
    path(
        "api/reviews/<int:review_id>/delete/",
        views.api_delete_review,
        name="api_delete_review",
    ),
    path("api/wishlist/", views.api_wishlist_list_view, name="api_wishlist_list"),
    path(
        "api/wishlist/toggle/",
        views.api_wishlist_toggle_view,
        name="api_wishlist_toggle",
    ),
    path(
        "api/places/<int:place_id>/like/",
        views.api_place_like_toggle,
        name="api_place_like",
    ),
    path(
        "api/posts/<int:place_id>/like/",
        views.api_place_like_toggle,
        name="api_post_like",
    ),
    path(
        "api/reviews/<int:review_id>/like/",
        views.api_review_like_toggle,
        name="api_review_like",
    ),
    # User Follow APIs
    path(
        "api/users/<int:user_id>/follow/",
        views.api_toggle_follow,
        name="api_toggle_follow",
    ),
    path(
        "api/users/<int:user_id>/followers/",
        views.api_user_followers,
        name="api_user_followers",
    ),
    path(
        "api/users/<int:user_id>/following/",
        views.api_user_following,
        name="api_user_following",
    ),
    path(
        "api/notifications/read-all/",
        views.api_mark_notifications_read,
        name="api_mark_notifications_read",
    ),
    # Place Details
    path("places/<int:place_id>/", views.place_detail, name="place_detail_id"),
    path("places/<slug:slug>/", views.place_detail, name="place_detail"),
]
