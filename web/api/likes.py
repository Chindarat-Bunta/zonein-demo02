from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from web.models import Place, PlaceLike


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

    user = request.user if request.user.is_authenticated else None
    if not user:
        user, _ = User.objects.get_or_create(
            username="zonein_user",
            defaults={"first_name": "Zone In User"}
        )

    like = PlaceLike.objects.filter(user=user, place=place).first()
    if like:
        like.delete()
        is_liked = False
        message = "ยกเลิกถูกใจแล้ว"
    else:
        PlaceLike.objects.create(user=user, place=place)
        is_liked = True
        message = "ถูกใจสถานที่นี้แล้ว"

    return JsonResponse({
        "success": True,
        "is_liked": is_liked,
        "message": message,
        "place_id": place.id,
        "total_likes": place.likes_count,
    })
