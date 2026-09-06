import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Place, Wishlist


def get_user_or_session_key(request):
    if request.user.is_authenticated:
        return request.user, None
    if not request.session.session_key:
        request.session.create()
    return None, request.session.session_key


def get_user_wishlist_place_ids(request):
    user, session_key = get_user_or_session_key(request)
    if user:
        return set(
            Wishlist.objects.filter(user=user).values_list("place_id", flat=True)
        )
    elif session_key:
        return set(
            Wishlist.objects.filter(session_key=session_key).values_list(
                "place_id", flat=True
            )
        )
    return set()


def index_view(request):
    wishlist_ids = get_user_wishlist_place_ids(request)
    total_wishlist_count = len(wishlist_ids)
    return render(
        request,
        "index.html",
        {
            "total_wishlist_count": total_wishlist_count,
            "wishlist_ids": wishlist_ids,
        },
    )


def api_places_view(request):
    wishlist_ids = get_user_wishlist_place_ids(request)
    places = Place.objects.all()
    data = []
    for p in places:
        data.append(
            {
                "id": p.id,
                "name": p.name,
                "slug": p.slug,
                "description": p.description,
                "address": p.address,
                "location": p.location,
                "category": p.category,
                "image_url": p.image_url,
                "rating": float(p.rating),
                "review_count": p.review_count,
                "price_display": p.price_display,
                "is_featured": p.is_featured,
                "is_wishlisted": p.id in wishlist_ids,
            }
        )
    return JsonResponse({"status": "success", "count": len(data), "places": data})


def wishlist_page_view(request):
    wishlist_ids = get_user_wishlist_place_ids(request)
    places = Place.objects.filter(id__in=wishlist_ids)

    return render(
        request,
        "wishlist.html",
        {
            "places": places,
            "total_wishlist_count": places.count(),
            "wishlist_ids": wishlist_ids,
        },
    )


def place_detail_view(request, slug):
    place = get_object_or_404(Place, slug=slug)
    related_places = Place.objects.filter(category=place.category).exclude(id=place.id)[:3]
    wishlist_ids = get_user_wishlist_place_ids(request)

    return render(
        request,
        "detail.html",
        {
            "place": place,
            "related_places": related_places,
            "is_wishlisted": place.id in wishlist_ids,
            "wishlist_ids": wishlist_ids,
        },
    )


@csrf_exempt
def api_wishlist_toggle_view(request):
    if request.method not in ["POST", "GET"]:
        return JsonResponse(
            {"status": "error", "message": "Method not allowed"}, status=405
        )

    place_id = None
    if request.method == "POST":
        try:
            body = json.loads(request.body.decode("utf-8")) if request.body else {}
            place_id = body.get("place_id") or request.POST.get("place_id")
        except json.JSONDecodeError:
            place_id = request.POST.get("place_id")
    else:
        place_id = request.GET.get("place_id")

    if not place_id:
        return JsonResponse(
            {"status": "error", "message": "Missing place_id"}, status=400
        )

    try:
        place = Place.objects.get(id=int(place_id))
    except (Place.DoesNotExist, ValueError):
        return JsonResponse(
            {"status": "error", "message": "Place not found"}, status=404
        )

    user, session_key = get_user_or_session_key(request)

    # Check if already in wishlist
    if user:
        wishlist_item = Wishlist.objects.filter(user=user, place=place).first()
        if wishlist_item:
            wishlist_item.delete()
            action = "removed"
        else:
            Wishlist.objects.create(user=user, place=place)
            action = "added"
        total_count = Wishlist.objects.filter(user=user).count()
    else:
        wishlist_item = Wishlist.objects.filter(
            session_key=session_key, place=place
        ).first()
        if wishlist_item:
            wishlist_item.delete()
            action = "removed"
        else:
            Wishlist.objects.create(session_key=session_key, place=place)
            action = "added"
        total_count = Wishlist.objects.filter(session_key=session_key).count()

    return JsonResponse(
        {
            "status": "success",
            "action": action,
            "place_id": place.id,
            "place_name": place.name,
            "total_count": total_count,
            "is_wishlisted": (action == "added"),
        }
    )


def api_wishlist_list_view(request):
    user, session_key = get_user_or_session_key(request)
    if user:
        wishlist_qs = Wishlist.objects.filter(user=user).select_related("place")
    elif session_key:
        wishlist_qs = Wishlist.objects.filter(session_key=session_key).select_related("place")
    else:
        wishlist_qs = Wishlist.objects.none()

    place_ids = list(wishlist_qs.values_list("place_id", flat=True))
    data = []
    for item in wishlist_qs:
        p = item.place
        data.append(
            {
                "id": p.id,
                "name": p.name,
                "slug": p.slug,
                "description": p.description,
                "address": p.address,
                "location": p.location,
                "category": p.category,
                "image_url": p.image_url,
                "rating": float(p.rating),
                "review_count": p.review_count,
                "price_display": p.price_display,
                "saved_at": item.created_at.strftime("%d/%m/%Y %H:%M"),
            }
        )

    return JsonResponse(
        {
            "status": "success",
            "count": len(data),
            "place_ids": place_ids,
            "places": data,
        }
    )
