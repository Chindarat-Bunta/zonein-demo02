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
    path("places/", views.home_view, name="places_list"),
    path("signin/", views.signin_view, name="signin"),
    path("login/", views.signin_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),
    path("social-login/<str:provider>/", views.social_login_view, name="social_login"),
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
    # Place Details
    path("places/<int:place_id>/", views.place_detail, name="place_detail_id"),
    path("places/<slug:slug>/", views.place_detail, name="place_detail"),
]
