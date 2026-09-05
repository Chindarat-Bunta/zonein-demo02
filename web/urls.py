from django.urls import path
from . import api_views, views

app_name = "web"

urlpatterns = [
    # API Root
    path("", views.api_root_view, name="api_root"),

    # Products API (Reviewed targets)
    path("api/products/", views.products_api_view, name="api_products"),

    # Users API for friend tagging
    path("api/users/", api_views.users_list_api_view, name="api_users"),

    # Rating & Review API Endpoints
    path("api/reviews/", api_views.reviews_list_create_view, name="api_reviews_list_create"),
    path("api/reviews/summary/", api_views.reviews_summary_view, name="api_reviews_summary"),
    path("api/reviews/<int:review_id>/", api_views.review_detail_view, name="api_review_detail"),
]
