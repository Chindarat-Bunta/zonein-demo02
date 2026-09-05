import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import connection


def parse_json_body(request):
    """Safely parse JSON request body or return None."""
    try:
        if request.body:
            return json.loads(request.body.decode("utf-8"))
        return {}
    except Exception:
        return None


@require_http_methods(["GET"])
def api_root(request):
    """
    Overview of all available Zone In API endpoints.
    """
    return JsonResponse({
        "name": "Zone In API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/health/",
            "places": {
                "list_or_create": "/api/places/ [GET, POST]",
                "detail": "/api/places/<place_id>/ [GET]",
                "reviews": "/api/places/<place_id>/reviews/ [GET, POST]",
                "like": "/api/places/<place_id>/like/ [POST]",
            },
            "wishlist": {
                "list": "/api/wishlist/ [GET]",
                "toggle": "/api/wishlist/toggle/ [POST]",
            },
            "profile": {
                "detail_or_update": "/api/profile/ [GET, POST]",
            }
        }
    })


@require_http_methods(["GET"])
def health_check(request):
    """
    Health check endpoint verifying database connectivity.
    """
    db_status = "connected"
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception as e:
        db_status = f"error: {str(e)}"

    return JsonResponse({
        "status": "ok" if db_status == "connected" else "degraded",
        "database": db_status,
        "service": "Zone In API",
    })
