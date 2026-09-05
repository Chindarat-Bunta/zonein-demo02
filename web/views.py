from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from .models import Category, Location, Place


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

    context = {
        "categories": categories,
        "locations": locations,
        "places": places,
        "total_count": places.count(),
        "all_places_count": Place.objects.count(),
        "filters": current_filters,
    }
    return render(request, "web/index.html", context)


def api_places_view(request):
    places, current_filters = filter_places_queryset(request)
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

    return render(
        request,
        "web/detail.html",
        {"place": place, "related_places": related_places},
    )
