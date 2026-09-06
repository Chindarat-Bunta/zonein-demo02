from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from decimal import Decimal, InvalidOperation
from web.models import Place, PlaceImage
from .views import parse_json_body


@csrf_exempt
def places_list_create(request):
    """
    Endpoint: /api/places/
    - GET: Retrieve a list of places (supports filtering by category and search keyword)
    - POST: Create a new place post
    """
    if request.method == "GET":
        category = request.GET.get("category", "").strip()
        search_q = request.GET.get("q", "").strip()

        queryset = Place.objects.select_related("author").prefetch_related("reviews", "likes").all()

        if category:
            queryset = queryset.filter(category__iexact=category)
        if search_q:
            queryset = queryset.filter(name__icontains=search_q)

        data = []
        for place in queryset:
            data.append({
                "id": place.id,
                "name": place.name,
                "slug": place.slug,
                "category": place.category,
                "category_display": place.get_category_display(),
                "description": place.description,
                "address": place.address,
                "latitude": float(place.latitude) if place.latitude else None,
                "longitude": float(place.longitude) if place.longitude else None,
                "cover_image_url": place.cover_image_url,
                "author": {
                    "id": place.author.id if place.author else None,
                    "username": place.author.username if place.author else "ZoneIn",
                    "name": (place.author.first_name or place.author.username) if place.author else "ZoneIn",
                },
                "average_rating": place.average_rating,
                "review_count": place.review_count,
                "likes_count": place.likes_count,
                "created_at": place.created_at.isoformat(),
            })

        return JsonResponse({"success": True, "count": len(data), "data": data})

    elif request.method == "POST":
        payload = parse_json_body(request)
        if payload is None:
            # Fallback to form-data / POST params
            payload = request.POST.dict()

        name = payload.get("name", "").strip()
        if not name:
            return JsonResponse({"success": False, "error": "ชื่อสถานที่ (name) จำเป็นต้องระบุ"}, status=400)

        category = payload.get("category", "cafe").strip()
        description = payload.get("description", "").strip()
        address = payload.get("address", "").strip()
        cover_image_url = payload.get("cover_image_url", "").strip()
        cover_image_public_id = payload.get("cover_image_public_id", "").strip()

        # Parse coordinates safely
        lat = None
        lng = None
        try:
            if payload.get("latitude"):
                lat = Decimal(str(payload.get("latitude")))
            if payload.get("longitude"):
                lng = Decimal(str(payload.get("longitude")))
        except (InvalidOperation, ValueError):
            return JsonResponse({"success": False, "error": "พิกัด latitude / longitude ไม่ถูกต้อง"}, status=400)

        # Author resolution
        user = request.user if request.user.is_authenticated else None
        if not user:
            # Get or create a default demo user for API requests
            user, _ = User.objects.get_or_create(
                username="zonein_explorer",
                defaults={"first_name": "Zone In Explorer", "email": "explorer@zonein.app"}
            )

        place = Place.objects.create(
            author=user,
            name=name,
            category=category,
            description=description,
            address=address,
            latitude=lat,
            longitude=lng,
            cover_image_url=cover_image_url,
            cover_image_public_id=cover_image_public_id
        )

        return JsonResponse({
            "success": True,
            "message": "สร้างสถานที่เรียบร้อยแล้ว",
            "place": {
                "id": place.id,
                "name": place.name,
                "slug": place.slug,
                "category": place.category,
                "latitude": float(place.latitude) if place.latitude else None,
                "longitude": float(place.longitude) if place.longitude else None,
                "cover_image_url": place.cover_image_url,
                "created_at": place.created_at.isoformat(),
            }
        }, status=201)

    return JsonResponse({"success": False, "error": f"Method {request.method} not allowed"}, status=405)


@csrf_exempt
def place_detail(request, place_id):
    """
    Endpoint: /api/places/<place_id>/
    - GET: Retrieve full details of a specific place including reviews and gallery
    """
    if request.method != "GET":
        return JsonResponse({"success": False, "error": "GET method required"}, status=405)

    try:
        place = Place.objects.select_related("author").prefetch_related("images", "reviews__user").get(id=place_id)
    except Place.DoesNotExist:
        return JsonResponse({"success": False, "error": "ไม่พบสถานที่นี้ในระบบ"}, status=404)

    images = [{"id": img.id, "image_url": img.image_url, "caption": img.caption} for img in place.images.all()]
    reviews = [
        {
            "id": r.id,
            "user": r.user.username,
            "rating": r.rating,
            "comment": r.comment,
            "created_at": r.created_at.isoformat(),
        }
        for r in place.reviews.all()
    ]

    return JsonResponse({
        "success": True,
        "id": place.id,
        "name": place.name,
        "average_rating": place.average_rating,
        "reviews_count": place.reviews_count,
        "place": {
            "id": place.id,
            "name": place.name,
            "slug": place.slug,
            "category": place.category,
            "category_display": place.get_category_display(),
            "description": place.description,
            "address": place.address,
            "latitude": float(place.latitude) if place.latitude else None,
            "longitude": float(place.longitude) if place.longitude else None,
            "cover_image_url": place.cover_image_url,
            "author": {
                "id": place.author.id if place.author else None,
                "username": place.author.username if place.author else "ZoneIn",
                "name": (place.author.first_name or place.author.username) if place.author else "ZoneIn",
            },
            "average_rating": place.average_rating,
            "review_count": place.review_count,
            "likes_count": place.likes_count,
            "images": images,
            "reviews": reviews,
            "created_at": place.created_at.isoformat(),
        }
    })
