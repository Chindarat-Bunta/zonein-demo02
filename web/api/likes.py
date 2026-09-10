from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from web.models import Place, PlaceLike, Notification


@csrf_exempt
def like_toggle(request, place_id):
    """
    Endpoint: /api/places/<place_id>/like/
    - POST: Toggle (like / unlike) a place
    """
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "POST method required"}, status=405)

    try:
        place = Place.objects.get(id=place_id)
    except Place.DoesNotExist:
        return JsonResponse({"success": False, "error": "ไม่พบสถานที่นี้"}, status=404)

    if not request.user.is_authenticated:
        return JsonResponse(
            {"success": False, "error": "unauthorized", "message": "กรุณาเข้าสู่ระบบเพื่อกดถูกใจ"},
            status=401,
        )

    user = request.user

    like = PlaceLike.objects.filter(user=user, place=place).first()
    if like:
        like.delete()
        is_liked = False
        message = "ยกเลิกถูกใจแล้ว"
    else:
        PlaceLike.objects.create(user=user, place=place)
        is_liked = True
        message = "ถูกใจสถานที่นี้แล้ว"
        if place.author and place.author != user:
            profile = getattr(user, "profile", None)
            actor_name = profile.get_display_name() if profile else (user.first_name or user.username)
            actor_tag = f"{actor_name} (@{user.username})" if actor_name and actor_name != user.username else f"@{user.username}"
            Notification.objects.create(
                actor=user,
                recipient=place.author,
                action_type="like",
                post=place,
                message=f"{actor_tag} ได้กดถูกใจโพสต์ '{place.name}'",
            )

    return JsonResponse({
        "success": True,
        "is_liked": is_liked,
        "liked": is_liked,
        "likes_count": place.likes_count,
        "message": message,
        "place_id": place.id,
        "total_likes": place.likes_count,
    })
