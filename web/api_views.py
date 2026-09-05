import json
import re
from django.contrib.auth.models import User
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import transaction
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.html import escape
from django.views.decorators.http import require_http_methods

from .models import Place, Review


def _parse_json_body(request):
    """Safely parse JSON request body or POST dict."""
    if request.content_type == "application/json" and request.body:
        try:
            return json.loads(request.body.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return None
    return request.POST


def _extract_tagged_users(comment_text, explicit_user_ids=None, explicit_usernames=None):
    """
    Extract User queryset based on @mentions in comment and explicit lists.
    """
    users_to_tag = set()

    # 1. Parse @username mentions from comment text
    if comment_text:
        mentions = re.findall(r"@([a-zA-Z0-9_]+)", comment_text)
        if mentions:
            mentioned_users = User.objects.filter(username__in=mentions)
            users_to_tag.update(mentioned_users)

    # 2. Add explicit IDs if provided
    if explicit_user_ids and isinstance(explicit_user_ids, list):
        valid_ids = [uid for uid in explicit_user_ids if str(uid).isdigit()]
        if valid_ids:
            users_to_tag.update(User.objects.filter(id__in=valid_ids))

    # 3. Add explicit usernames if provided
    if explicit_usernames and isinstance(explicit_usernames, list):
        valid_names = [str(name).strip().lstrip("@") for name in explicit_usernames if str(name).strip()]
        if valid_names:
            users_to_tag.update(User.objects.filter(username__in=valid_names))

    return list(users_to_tag)


def _serialize_review(review, current_user=None):
    """Helper to serialize a Review instance to dict including tagged friends."""
    is_owner = False
    is_admin = False
    is_tagged = False

    tagged_list = [
        {"id": u.id, "username": u.username}
        for u in review.tagged_users.all()
    ]

    if current_user and current_user.is_authenticated:
        is_owner = review.user_id == current_user.id
        is_admin = current_user.is_staff or current_user.is_superuser
        is_tagged = any(u["id"] == current_user.id for u in tagged_list)

    return {
        "id": review.id,
        "target_id": review.target_id,
        "target_name": review.target.name,
        "user_id": review.user_id,
        "username": review.user.username,
        "rating": review.rating,
        "comment": review.comment,
        "tagged_users": tagged_list,
        "is_tagged": is_tagged,
        "created_at": review.created_at.isoformat(),
        "updated_at": review.updated_at.isoformat(),
        "is_owner": is_owner,
        "can_delete": is_owner or is_admin,
    }


def _serialize_place(place):
    """Helper to serialize Place instance."""
    return {
        "id": place.id,
        "name": place.name,
        "category": place.category,
        "location": place.location,
        "description": place.description,
        "image_url": place.image_url,
        "average_rating": place.average_rating,
        "review_count": place.review_count,
        "created_at": place.created_at.isoformat(),
    }


@require_http_methods(["GET", "POST"])
def places_list_create_view(request):
    """
    GET /api/places/ -> List all place recommendation posts
    POST /api/places/ -> Create a new place recommendation post
    """
    if request.method == "GET":
        places = Place.objects.all().order_by("-created_at")
        data = [_serialize_place(p) for p in places]
        return JsonResponse({"places": data, "products": data}, status=200)

    # POST - Create a new Place recommendation post
    data = _parse_json_body(request)
    if data is None:
        return JsonResponse({"error": "Invalid JSON body format."}, status=400)

    name = str(data.get("name", "")).strip()
    category = str(data.get("category", "")).strip() or "สถานที่ท่องเที่ยว"
    location = str(data.get("location", "")).strip()
    description = str(data.get("description", "")).strip()
    image_url = str(data.get("image_url", "")).strip()

    if not name:
        return JsonResponse({"error": "กรุณาระบุชื่อสถานที่ (name is required)"}, status=400)

    # Default image if empty
    if not image_url:
        image_url = "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&auto=format&fit=crop&q=60"

    place = Place.objects.create(
        name=escape(name),
        category=escape(category),
        location=escape(location),
        description=escape(description),
        image_url=image_url,
    )

    return JsonResponse(
        {
            "message": "สร้างโพสต์แนะนำสถานที่สำเร็จเรียบร้อย!",
            "place": _serialize_place(place),
        },
        status=201,
    )


@require_http_methods(["GET", "POST"])
def reviews_list_create_view(request):
    """
    GET /api/reviews/?target_id=xxx&page=1&page_size=10
    POST /api/reviews/ (Body: {target_id, rating, comment, tagged_user_ids?})
    """
    if request.method == "GET":
        target_id = request.GET.get("target_id")
        if not target_id:
            return JsonResponse({"error": "target_id query parameter is required."}, status=400)

        try:
            target_id = int(target_id)
        except (ValueError, TypeError):
            return JsonResponse({"error": "target_id must be a valid integer."}, status=400)

        place = get_object_or_404(Place, pk=target_id)

        reviews_qs = (
            Review.objects.filter(target=place)
            .select_related("user", "target")
            .prefetch_related("tagged_users")
            .order_by("-created_at")
        )

        page_number = request.GET.get("page", 1)
        page_size = request.GET.get("page_size", 10)
        try:
            page_size = min(max(int(page_size), 1), 50)
        except (ValueError, TypeError):
            page_size = 10

        paginator = Paginator(reviews_qs, page_size)
        try:
            reviews_page = paginator.page(page_number)
        except (PageNotAnInteger, EmptyPage):
            reviews_page = paginator.page(1) if int(page_number or 1) <= 1 else []

        serialized_reviews = [
            _serialize_review(r, request.user)
            for r in (reviews_page.object_list if hasattr(reviews_page, "object_list") else reviews_page)
        ]

        return JsonResponse({
            "count": paginator.count,
            "num_pages": paginator.num_pages,
            "current_page": reviews_page.number if hasattr(reviews_page, "number") else 1,
            "has_next": reviews_page.has_next() if hasattr(reviews_page, "has_next") else False,
            "has_previous": reviews_page.has_previous() if hasattr(reviews_page, "has_previous") else False,
            "results": serialized_reviews,
        }, status=200)

    # POST - Create Review
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required to submit a review."}, status=401)

    data = _parse_json_body(request)
    if data is None:
        return JsonResponse({"error": "Invalid JSON body format."}, status=400)

    target_id = data.get("target_id")
    rating_raw = data.get("rating")
    comment_raw = data.get("comment", "")
    explicit_tagged_ids = data.get("tagged_user_ids", [])
    explicit_tagged_names = data.get("tagged_usernames", [])

    if not target_id:
        return JsonResponse({"error": "target_id is required."}, status=400)

    try:
        place = Place.objects.get(pk=int(target_id))
    except (ValueError, TypeError, Place.DoesNotExist):
        return JsonResponse({"error": "Target place does not exist."}, status=404)

    # Validate rating
    try:
        rating = int(rating_raw)
        if rating < 1 or rating > 5:
            return JsonResponse({"error": "Rating must be an integer between 1 and 5."}, status=400)
    except (ValueError, TypeError):
        return JsonResponse({"error": "Rating must be a valid integer between 1 and 5."}, status=400)

    # Check for duplicate review
    if Review.objects.filter(user=request.user, target=place).exists():
        return JsonResponse(
            {"error": "You have already reviewed this place. Please update your existing review instead."},
            status=400,
        )

    # Sanitize comment for XSS protection
    sanitized_comment = escape(str(comment_raw).strip()) if comment_raw else ""

    # Resolve tagged users
    users_to_tag = _extract_tagged_users(
        comment_raw,
        explicit_user_ids=explicit_tagged_ids,
        explicit_usernames=explicit_tagged_names,
    )

    with transaction.atomic():
        review = Review.objects.create(
            user=request.user,
            target=place,
            rating=rating,
            comment=sanitized_comment,
        )
        if users_to_tag:
            review.tagged_users.set(users_to_tag)
        place.update_rating_stats()

    return JsonResponse(
        {
            "message": "Review submitted successfully.",
            "review": _serialize_review(review, request.user),
            "summary": {
                "average_rating": place.average_rating,
                "review_count": place.review_count,
            },
        },
        status=201,
    )


@require_http_methods(["PUT", "DELETE", "GET"])
def review_detail_view(request, review_id):
    """
    GET /api/reviews/<id>/
    PUT /api/reviews/<id>/ (Body: {rating?, comment?, tagged_user_ids?})
    DELETE /api/reviews/<id>/
    """
    try:
        review = Review.objects.select_related("user", "target").prefetch_related("tagged_users").get(pk=review_id)
    except Review.DoesNotExist:
        return JsonResponse({"error": "Review not found."}, status=404)

    if request.method == "GET":
        return JsonResponse(_serialize_review(review, request.user), status=200)

    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required."}, status=401)

    is_owner = review.user_id == request.user.id
    is_admin = request.user.is_staff or request.user.is_superuser

    if request.method == "PUT":
        if not is_owner:
            return JsonResponse(
                {"error": "Permission denied. You can only edit your own review."},
                status=403,
            )

        data = _parse_json_body(request)
        if data is None:
            return JsonResponse({"error": "Invalid JSON body format."}, status=400)

        updated_fields = []
        if "rating" in data:
            try:
                new_rating = int(data["rating"])
                if new_rating < 1 or new_rating > 5:
                    return JsonResponse({"error": "Rating must be an integer between 1 and 5."}, status=400)
                review.rating = new_rating
                updated_fields.append("rating")
            except (ValueError, TypeError):
                return JsonResponse({"error": "Rating must be a valid integer between 1 and 5."}, status=400)

        comment_changed = False
        if "comment" in data:
            review.comment = escape(str(data["comment"]).strip())
            updated_fields.append("comment")
            comment_changed = True

        with transaction.atomic():
            if updated_fields:
                review.save()
                review.target.update_rating_stats()

            if comment_changed or "tagged_user_ids" in data or "tagged_usernames" in data:
                users_to_tag = _extract_tagged_users(
                    data.get("comment", review.comment),
                    explicit_user_ids=data.get("tagged_user_ids"),
                    explicit_usernames=data.get("tagged_usernames"),
                )
                review.tagged_users.set(users_to_tag)

        # Refresh to get updated tagged users
        review.refresh_from_db()

        return JsonResponse(
            {
                "message": "Review updated successfully.",
                "review": _serialize_review(review, request.user),
                "summary": {
                    "average_rating": review.target.average_rating,
                    "review_count": review.target.review_count,
                },
            },
            status=200,
        )

    if request.method == "DELETE":
        if not (is_owner or is_admin):
            return JsonResponse(
                {"error": "Permission denied. Only review author or administrator can delete this review."},
                status=403,
            )

        place = review.target
        with transaction.atomic():
            review.delete()
            place.update_rating_stats()

        return JsonResponse(
            {
                "message": "Review deleted successfully.",
                "summary": {
                    "average_rating": place.average_rating,
                    "review_count": place.review_count,
                },
            },
            status=200,
        )


@require_http_methods(["GET"])
def reviews_summary_view(request):
    """
    GET /api/reviews/summary/?target_id=xxx
    """
    target_id = request.GET.get("target_id")
    if not target_id:
        return JsonResponse({"error": "target_id query parameter is required."}, status=400)

    try:
        target_id = int(target_id)
    except (ValueError, TypeError):
        return JsonResponse({"error": "target_id must be a valid integer."}, status=400)

    place = get_object_or_404(Place, pk=target_id)

    distribution = (
        Review.objects.filter(target=place)
        .values("rating")
        .annotate(count=Count("rating"))
    )
    breakdown = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for item in distribution:
        breakdown[item["rating"]] = item["count"]

    user_review = None
    if request.user.is_authenticated:
        existing = Review.objects.filter(target=place, user=request.user).prefetch_related("tagged_users").first()
        if existing:
            user_review = _serialize_review(existing, request.user)

    return JsonResponse({
        "target_id": place.id,
        "target_name": place.name,
        "average_rating": place.average_rating,
        "review_count": place.review_count,
        "breakdown": breakdown,
        "user_reviewed": user_review is not None,
        "user_review": user_review,
    }, status=200)


@require_http_methods(["GET"])
def users_list_api_view(request):
    """
    GET /api/users/?q=xxx
    Returns list of users that can be tagged/mentioned.
    """
    query = request.GET.get("q", "").strip()
    users_qs = User.objects.all().order_by("username")
    if query:
        users_qs = users_qs.filter(Q(username__icontains=query) | Q(first_name__icontains=query))

    users = [{"id": u.id, "username": u.username} for u in users_qs[:20]]
    return JsonResponse({"users": users})
