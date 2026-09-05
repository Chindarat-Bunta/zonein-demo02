import json
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import transaction
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.html import escape
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import Product, Review


def _parse_json_body(request):
    """Safely parse JSON request body or POST dict."""
    if request.content_type == "application/json" and request.body:
        try:
            return json.loads(request.body.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return None
    return request.POST


def _serialize_review(review, current_user=None):
    """Helper to serialize a Review instance to dict."""
    is_owner = False
    is_admin = False
    if current_user and current_user.is_authenticated:
        is_owner = review.user_id == current_user.id
        is_admin = current_user.is_staff or current_user.is_superuser

    return {
        "id": review.id,
        "target_id": review.target_id,
        "target_name": review.target.name,
        "user_id": review.user_id,
        "username": review.user.username,
        "rating": review.rating,
        "comment": review.comment,
        "created_at": review.created_at.isoformat(),
        "updated_at": review.updated_at.isoformat(),
        "is_owner": is_owner,
        "can_delete": is_owner or is_admin,
    }


@require_http_methods(["GET", "POST"])
def reviews_list_create_view(request):
    """
    GET /api/reviews/?target_id=xxx&page=1&page_size=10
    POST /api/reviews/ (Body: {target_id, rating, comment})
    """
    if request.method == "GET":
        target_id = request.GET.get("target_id")
        if not target_id:
            return JsonResponse({"error": "target_id query parameter is required."}, status=400)

        try:
            target_id = int(target_id)
        except (ValueError, TypeError):
            return JsonResponse({"error": "target_id must be a valid integer."}, status=400)

        product = get_object_or_404(Product, pk=target_id)

        reviews_qs = (
            Review.objects.filter(target=product)
            .select_related("user", "target")
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
            _serialize_review(r, request.user) for r in (reviews_page.object_list if hasattr(reviews_page, "object_list") else reviews_page)
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

    if not target_id:
        return JsonResponse({"error": "target_id is required."}, status=400)

    try:
        product = Product.objects.get(pk=int(target_id))
    except (ValueError, TypeError, Product.DoesNotExist):
        return JsonResponse({"error": "Target product does not exist."}, status=404)

    # Validate rating
    try:
        rating = int(rating_raw)
        if rating < 1 or rating > 5:
            return JsonResponse({"error": "Rating must be an integer between 1 and 5."}, status=400)
    except (ValueError, TypeError):
        return JsonResponse({"error": "Rating must be a valid integer between 1 and 5."}, status=400)

    # Check for duplicate review
    if Review.objects.filter(user=request.user, target=product).exists():
        return JsonResponse(
            {"error": "You have already reviewed this product. Please update your existing review instead."},
            status=400,
        )

    # Sanitize comment for XSS protection
    sanitized_comment = escape(str(comment_raw).strip()) if comment_raw else ""

    with transaction.atomic():
        review = Review.objects.create(
            user=request.user,
            target=product,
            rating=rating,
            comment=sanitized_comment,
        )
        product.update_rating_stats()

    return JsonResponse(
        {
            "message": "Review submitted successfully.",
            "review": _serialize_review(review, request.user),
            "summary": {
                "average_rating": product.average_rating,
                "review_count": product.review_count,
            },
        },
        status=201,
    )


@require_http_methods(["PUT", "DELETE", "GET"])
def review_detail_view(request, review_id):
    """
    GET /api/reviews/<id>/
    PUT /api/reviews/<id>/ (Body: {rating?, comment?})
    DELETE /api/reviews/<id>/
    """
    try:
        review = Review.objects.select_related("user", "target").get(pk=review_id)
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

        if "comment" in data:
            review.comment = escape(str(data["comment"]).strip())
            updated_fields.append("comment")

        if updated_fields:
            with transaction.atomic():
                review.save()
                review.target.update_rating_stats()

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

        product = review.target
        with transaction.atomic():
            review.delete()
            product.update_rating_stats()

        return JsonResponse(
            {
                "message": "Review deleted successfully.",
                "summary": {
                    "average_rating": product.average_rating,
                    "review_count": product.review_count,
                },
            },
            status=200,
        )


@require_http_methods(["GET"])
def reviews_summary_view(request):
    """
    GET /api/reviews/summary/?target_id=xxx
    Returns rating summary, average, total count, star breakdown (1-5), and current user review status.
    """
    target_id = request.GET.get("target_id")
    if not target_id:
        return JsonResponse({"error": "target_id query parameter is required."}, status=400)

    try:
        target_id = int(target_id)
    except (ValueError, TypeError):
        return JsonResponse({"error": "target_id must be a valid integer."}, status=400)

    product = get_object_or_404(Product, pk=target_id)

    # Star breakdown distribution
    distribution = (
        Review.objects.filter(target=product)
        .values("rating")
        .annotate(count=Count("rating"))
    )
    breakdown = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for item in distribution:
        breakdown[item["rating"]] = item["count"]

    # Check if current logged in user has already reviewed
    user_review = None
    if request.user.is_authenticated:
        existing = Review.objects.filter(target=product, user=request.user).first()
        if existing:
            user_review = _serialize_review(existing, request.user)

    return JsonResponse({
        "target_id": product.id,
        "target_name": product.name,
        "average_rating": product.average_rating,
        "review_count": product.review_count,
        "breakdown": breakdown,
        "user_reviewed": user_review is not None,
        "user_review": user_review,
    }, status=200)
