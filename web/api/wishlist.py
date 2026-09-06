from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from web.models import Place, Wishlist
from .views import parse_json_body


@csrf_exempt
def wishlist_list(request):
    """
    Endpoint: /api/wishlist/
    - GET: Retrieve wishlist items for the current user
    """
    if request.method != "GET":
        return JsonResponse({"success": False, "error": "GET method required"}, status=405)

    user = request.user if request.user.is_authenticated else None
    if not user:
        user = User.objects.first()
        if not user:
            return JsonResponse({"success": True, "count": 0, "wishlist": []})

    items = Wishlist.objects.filter(user=user).select_related("place").order_by("-created_at")
    data = []
    for item in items:
        p = item.place
        data.append({
            "id": item.id,
            "place_id": p.id,
            "name": p.name,
            "category": p.category,
            "category_display": p.get_category_display(),
            "cover_image_url": p.cover_image_url,
            "average_rating": p.average_rating,
            "saved_at": item.created_at.isoformat(),
        })

    return JsonResponse({
        "success": True,
        "count": len(data),
        "wishlist": data,
    })


@csrf_exempt
def wishlist_toggle(request):
    """
    Endpoint: /api/wishlist/toggle/
    - POST: Toggle (add or remove) a place in user's wishlist
    """
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "POST method required"}, status=405)

    payload = parse_json_body(request)
    if payload is None:
        payload = request.POST.dict()

    place_id = payload.get("place_id")
    if not place_id:
        return JsonResponse({"success": False, "error": "place_id จำเป็นต้องระบุ"}, status=400)

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

    existing = Wishlist.objects.filter(user=user, place=place).first()
    if existing:
        existing.delete()
        is_saved = False
        message = "นำออกจากรายการโปรดแล้ว"
    else:
        Wishlist.objects.create(user=user, place=place)
        is_saved = True
        message = "เพิ่มลงในรายการโปรดเรียบร้อยแล้ว"

    return JsonResponse({
        "status": "success",
        "success": True,
        "action": "added" if is_saved else "removed",
        "is_saved": is_saved,
        "is_wishlisted": is_saved,
        "message": message,
        "place_id": place.id,
        "total_count": Wishlist.objects.filter(user=user).count(),
        "total_wishlisted": place.wishlist_count,
    })
