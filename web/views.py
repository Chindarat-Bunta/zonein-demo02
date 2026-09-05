import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from .models import Category, Location, Place, Wishlist


def get_user_or_session_key(request):
    if request.user.is_authenticated:
        return request.user, None
    if not request.session.session_key:
        request.session.create()
    return None, request.session.session_key


def get_user_wishlist_place_ids(request):
    user, session_key = get_user_or_session_key(request)
    if user:
        return set(Wishlist.objects.filter(user=user).values_list("place_id", flat=True))
    elif session_key:
        return set(Wishlist.objects.filter(session_key=session_key).values_list("place_id", flat=True))
    return set()


def filter_places_queryset(request):
    queryset = Place.objects.select_related("category", "location").all()

    # Search keyword
    q = request.GET.get("q", "").strip()
    if q:
        queryset = queryset.filter(
            Q(name__icontains=q)
            | Q(description__icontains=q)
            | Q(address__icontains=q)
            | Q(tags__icontains=q)
        )

    # Category filter (slug or id)
    category_param = request.GET.get("category", "").strip()
    if category_param and category_param != "all":
        if category_param.isdigit():
            queryset = queryset.filter(category_id=int(category_param))
        else:
            queryset = queryset.filter(category__slug=category_param)

    # Location filter (slug or id)
    location_param = request.GET.get("location", "").strip()
    if location_param and location_param != "all":
        if location_param.isdigit():
            queryset = queryset.filter(location_id=int(location_param))
        else:
            queryset = queryset.filter(location__slug=location_param)

    # Min rating
    min_rating = request.GET.get("min_rating", "").strip()
    if min_rating:
        try:
            queryset = queryset.filter(rating__gte=float(min_rating))
        except ValueError:
            pass

    # Sort
    sort_by = request.GET.get("sort", "rating")
    if sort_by == "rating":
        queryset = queryset.order_by("-rating", "-review_count")
    elif sort_by == "reviews":
        queryset = queryset.order_by("-review_count", "-rating")
    elif sort_by == "newest":
        queryset = queryset.order_by("-created_at")
    elif sort_by == "name":
        queryset = queryset.order_by("name")

    return queryset, {
        "q": q,
        "category": category_param,
        "location": location_param,
        "min_rating": min_rating,
        "sort": sort_by,
    }


def index_view(request):
    categories = Category.objects.all()
    locations = Location.objects.all()
    places, current_filters = filter_places_queryset(request)
    wishlist_ids = get_user_wishlist_place_ids(request)

    context = {
        "categories": categories,
        "locations": locations,
        "places": places,
        "total_count": places.count(),
        "all_places_count": Place.objects.count(),
        "filters": current_filters,
        "wishlist_ids": wishlist_ids,
    }
    return render(request, "index.html", context)


def api_places_view(request):
    places, current_filters = filter_places_queryset(request)
    wishlist_ids = get_user_wishlist_place_ids(request)
    data = []
    for p in places:
        data.append(
            {
                "id": p.id,
                "name": p.name,
                "slug": p.slug,
                "description": p.description,
                "address": p.address,
                "image_url": p.image_url or "https://images.unsplash.com/photo-1554118811-1e0d58224f24?w=600&auto=format&fit=crop&q=80",
                "category": {
                    "id": p.category.id if p.category else None,
                    "name": p.category.name if p.category else "ทั่วไป",
                    "slug": p.category.slug if p.category else "",
                    "icon": p.category.icon if p.category else "fa-tag",
                    "color": p.category.color if p.category else "#3b82f6",
                }
                if p.category
                else None,
                "location": {
                    "id": p.location.id if p.location else None,
                    "city": p.location.city if p.location else "",
                    "zone": p.location.zone if p.location else "",
                    "slug": p.location.slug if p.location else "",
                    "display": str(p.location) if p.location else "",
                }
                if p.location
                else None,
                "rating": float(p.rating),
                "review_count": p.review_count,
                "price_level": p.price_level,
                "price_display": p.price_display,
                "tags": p.tag_list,
                "is_featured": p.is_featured,
                "is_wishlisted": p.id in wishlist_ids,
            }
        )

    return JsonResponse(
        {
            "status": "success",
            "count": len(data),
            "total": Place.objects.count(),
            "filters": current_filters,
            "places": data,
        }
    )


def place_detail_view(request, slug):
    place = get_object_or_404(Place.objects.select_related("category", "location"), slug=slug)
    related_places = Place.objects.filter(
        category=place.category
    ).exclude(id=place.id)[:3]
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


def wishlist_page_view(request):
    wishlist_ids = get_user_wishlist_place_ids(request)
    places = Place.objects.filter(id__in=wishlist_ids).select_related("category", "location")
    all_places = Place.objects.select_related("category", "location").all()

    return render(
        request,
        "wishlist.html",
        {
            "places": places,
            "all_places": all_places,
            "total_wishlist_count": places.count(),
            "wishlist_ids": wishlist_ids,
        },
    )


@csrf_exempt
def api_wishlist_toggle_view(request):
    if request.method not in ["POST", "GET"]:
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

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
        return JsonResponse({"status": "error", "message": "Missing place_id"}, status=400)

    try:
        place = Place.objects.get(id=int(place_id))
    except (Place.DoesNotExist, ValueError):
        return JsonResponse({"status": "error", "message": "Place not found"}, status=404)

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
        wishlist_item = Wishlist.objects.filter(session_key=session_key, place=place).first()
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
    wishlist_ids = get_user_wishlist_place_ids(request)
    places = Place.objects.filter(id__in=wishlist_ids).select_related("category", "location")
    data = []
    for p in places:
        data.append(
            {
                "id": p.id,
                "name": p.name,
                "slug": p.slug,
                "description": p.description,
                "address": p.address,
                "image_url": p.image_url or "https://images.unsplash.com/photo-1554118811-1e0d58224f24?w=600&auto=format&fit=crop&q=80",
                "category": {
                    "name": p.category.name if p.category else "ทั่วไป",
                    "slug": p.category.slug if p.category else "",
                    "icon": p.category.icon if p.category else "fa-tag",
                    "color": p.category.color if p.category else "#3b82f6",
                }
                if p.category
                else None,
                "location": {
                    "city": p.location.city if p.location else "",
                    "zone": p.location.zone if p.location else "",
                    "display": str(p.location) if p.location else "",
                }
                if p.location
                else None,
                "rating": float(p.rating),
                "review_count": p.review_count,
                "price_level": p.price_level,
                "price_display": p.price_display,
                "tags": p.tag_list,
                "is_featured": p.is_featured,
            }
        )

    return JsonResponse(
        {
            "status": "success",
            "count": len(data),
            "place_ids": list(wishlist_ids),
            "places": data,
        }
    )
