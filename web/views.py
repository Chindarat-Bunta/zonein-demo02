from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Product


@require_http_methods(["GET"])
def api_root_view(request):
    """API overview endpoint."""
    return JsonResponse({
        "name": "Rating & Review API",
        "endpoints": {
            "reviews_list_create": "/api/reviews/",
            "review_detail": "/api/reviews/<id>/",
            "reviews_summary": "/api/reviews/summary/?target_id=<id>",
            "users_list": "/api/users/?q=<search>",
            "products_list": "/api/products/",
        }
    })


@require_http_methods(["GET"])
def products_api_view(request):
    """Return list of reviewed targets/products."""
    products = Product.objects.all().order_by("id")
    data = [
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "price": float(p.price),
            "image_url": p.image_url,
            "average_rating": p.average_rating,
            "review_count": p.review_count,
        }
        for p in products
    ]
    return JsonResponse({"products": data})
