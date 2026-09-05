from django.http import JsonResponse


def home_view(request):
    """Clean Backend API Root overview."""
    return JsonResponse({
        "service": "ZoneIn Backend API",
        "status": "ready",
        "version": "1.0.0",
        "endpoints": {
            "posts": "/api/posts/",
            "post_detail": "/api/posts/<post_id>/",
            "toggle_like": "/api/posts/<post_id>/like/",
            "post_likes": "/api/posts/<post_id>/likes/",
            "comments": "/api/posts/<post_id>/comments/",
            "delete_comment": "/api/posts/<post_id>/comments/<comment_id>/",
            "toggle_follow": "/api/users/<user_id>/follow/",
            "follow_status": "/api/users/<user_id>/follow-status/",
            "followers": "/api/users/<user_id>/followers/",
            "following": "/api/users/<user_id>/following/",
        },
    })

