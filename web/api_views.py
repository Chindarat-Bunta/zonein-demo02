import json
from django.contrib.auth.models import User
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import transaction
from django.db.models import F, Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.html import escape
from django.views.decorators.http import require_http_methods

from .models import PostComment, PostLike, TravelPost


def _parse_json_body(request):
    """Safely parse JSON request body or POST dict."""
    if request.content_type == "application/json" and request.body:
        try:
            return json.loads(request.body.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return None
    return request.POST


def _get_current_or_default_user(request):
    """Get authenticated user or default main traveler user."""
    if request.user.is_authenticated:
        return request.user
    user, _ = User.objects.get_or_create(username="traveler", defaults={"email": "traveler@example.com"})
    return user


def _serialize_post(post, current_user=None):
    """Serialize a TravelPost instance to dictionary."""
    is_owner = True
    is_admin = False
    is_liked = False

    effective_user = current_user if current_user and current_user.is_authenticated else User.objects.filter(username="traveler").first()
    if effective_user:
        is_liked = PostLike.objects.filter(post_id=post.id, user_id=effective_user.id).exists()

    if current_user and current_user.is_authenticated:
        is_owner = post.author_id == current_user.id or not current_user.is_authenticated
        is_admin = current_user.is_staff or current_user.is_superuser

    return {
        "id": post.id,
        "author_id": post.author_id,
        "author_name": post.author.username,
        "place_name": post.place_name,
        "category": post.category,
        "location": post.location,
        "rating": post.rating,
        "content": post.content,
        "image_url": post.image_url,
        "likes_count": post.likes_count,
        "comments_count": post.comments_count,
        "is_liked": is_liked,
        "is_owner": is_owner,
        "can_delete": True,  # User can delete posts
        "created_at": post.created_at.isoformat(),
        "updated_at": post.updated_at.isoformat(),
    }


def _serialize_comment(comment, current_user=None):
    """Serialize a PostComment instance."""
    can_delete = True
    if current_user and current_user.is_authenticated:
        can_delete = (
            comment.user_id == current_user.id
            or comment.post.author_id == current_user.id
            or current_user.is_staff
            or current_user.is_superuser
        )
    return {
        "id": comment.id,
        "post_id": comment.post_id,
        "author_id": comment.user_id,
        "author_name": comment.user.username,
        "content": comment.content,
        "can_delete": can_delete,
        "created_at": comment.created_at.isoformat(),
    }




@require_http_methods(["GET", "POST"])
def travel_posts_list_create_view(request):
    """
    GET /api/posts/ -> List all travel posts
    POST /api/posts/ -> Create a new travel place review post
    """
    if request.method == "GET":
        category_filter = request.GET.get("category", "").strip()
        search_query = request.GET.get("q", "").strip()

        posts_qs = TravelPost.objects.select_related("author").order_by("-created_at")

        if category_filter:
            posts_qs = posts_qs.filter(category=category_filter)
        if search_query:
            posts_qs = posts_qs.filter(
                Q(place_name__icontains=search_query)
                | Q(location__icontains=search_query)
                | Q(content__icontains=search_query)
            )

        page_number = request.GET.get("page", 1)
        page_size = request.GET.get("page_size", 20)
        try:
            page_size = min(max(int(page_size), 1), 50)
        except (ValueError, TypeError):
            page_size = 20

        paginator = Paginator(posts_qs, page_size)
        try:
            posts_page = paginator.page(page_number)
        except (PageNotAnInteger, EmptyPage):
            posts_page = paginator.page(1) if int(page_number or 1) <= 1 else []

        serialized_posts = [
            _serialize_post(p, request.user)
            for p in (posts_page.object_list if hasattr(posts_page, "object_list") else posts_page)
        ]

        total_likes = TravelPost.objects.aggregate(total=Sum("likes_count"))["total"] or 0

        return JsonResponse({
            "count": paginator.count,
            "total_likes": total_likes,
            "num_pages": paginator.num_pages,
            "current_page": posts_page.number if hasattr(posts_page, "number") else 1,
            "has_next": posts_page.has_next() if hasattr(posts_page, "has_next") else False,
            "has_previous": posts_page.has_previous() if hasattr(posts_page, "has_previous") else False,
            "results": serialized_posts,
            "posts": serialized_posts,
        }, status=200)

    # POST - Create Travel Review Post
    data = _parse_json_body(request)
    if data is None:
        return JsonResponse({"error": "รูปแบบ JSON ไม่ถูกต้อง"}, status=400)

    place_name = str(data.get("place_name", "") or data.get("name", "")).strip()
    category = str(data.get("category", "")).strip() or "สถานที่ท่องเที่ยว"
    location = str(data.get("location", "")).strip()
    content = str(data.get("content", "") or data.get("comment", "")).strip()
    image_url = str(data.get("image_url", "")).strip()
    rating_raw = data.get("rating")

    if not place_name:
        return JsonResponse({"error": "กรุณาระบุชื่อสถานที่ที่ไป"}, status=400)

    # Validate rating
    try:
        rating = int(rating_raw)
        if rating < 1 or rating > 5:
            return JsonResponse({"error": "คะแนนดาวต้องเป็นจำนวนเต็มระหว่าง 1 ถึง 5"}, status=400)
    except (ValueError, TypeError):
        return JsonResponse({"error": "กรุณาเลือกระดับคะแนนดาว 1-5 ดาว"}, status=400)

    if not image_url:
        image_url = "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&auto=format&fit=crop&q=60"

    current_user = _get_current_or_default_user(request)

    with transaction.atomic():
        post = TravelPost.objects.create(
            author=current_user,
            place_name=escape(place_name),
            category=escape(category),
            location=escape(location),
            rating=rating,
            content=escape(content),
            image_url=image_url,
        )

    return JsonResponse(
        {
            "message": "โพสต์รีวิวสถานที่สำเร็จเรียบร้อย!",
            "post": _serialize_post(post, request.user),
            "review": _serialize_post(post, request.user),
        },
        status=201,
    )


@require_http_methods(["GET", "PUT", "DELETE"])
def travel_post_detail_view(request, post_id):
    """
    GET /api/posts/<id>/ -> View post
    PUT /api/posts/<id>/ -> Edit post
    DELETE /api/posts/<id>/ -> Delete post
    """
    try:
        post = TravelPost.objects.select_related("author").get(pk=post_id)
    except TravelPost.DoesNotExist:
        return JsonResponse({"error": "ไม่พบโพสต์สถานที่นี้"}, status=404)

    if request.method == "GET":
        return JsonResponse(_serialize_post(post, request.user), status=200)

    if request.method == "PUT":
        data = _parse_json_body(request)
        if data is None:
            return JsonResponse({"error": "รูปแบบ JSON ไม่ถูกต้อง"}, status=400)

        if "place_name" in data:
            p_name = str(data["place_name"]).strip()
            if p_name:
                post.place_name = escape(p_name)

        if "category" in data:
            post.category = escape(str(data["category"]).strip())

        if "location" in data:
            post.location = escape(str(data["location"]).strip())

        if "image_url" in data and str(data["image_url"]).strip():
            post.image_url = str(data["image_url"]).strip()

        if "rating" in data:
            try:
                new_rating = int(data["rating"])
                if new_rating < 1 or new_rating > 5:
                    return JsonResponse({"error": "คะแนนดาวต้องอยู่ระหว่าง 1-5"}, status=400)
                post.rating = new_rating
            except (ValueError, TypeError):
                return JsonResponse({"error": "คะแนนดาวไม่ถูกต้อง"}, status=400)

        if "content" in data or "comment" in data:
            raw_content = str(data.get("content", data.get("comment", ""))).strip()
            post.content = escape(raw_content)

        post.save()

        return JsonResponse(
            {
                "message": "แก้ไขโพสต์รีวิวเรียบร้อยแล้ว",
                "post": _serialize_post(post, request.user),
                "review": _serialize_post(post, request.user),
            },
            status=200,
        )

    if request.method == "DELETE":
        post.delete()
        return JsonResponse({"message": "ลบโพสต์เรียบร้อยแล้ว"}, status=200)


@require_http_methods(["POST", "DELETE"])
def toggle_post_like_view(request, post_id):
    """
    POST /api/posts/<id>/like/ -> Toggle like / unlike on a post.
    DELETE /api/posts/<id>/like/ -> Explicitly unlike a post.
    Returns: {"liked": boolean, "likes_count": int, "message": str}
    """
    post = get_object_or_404(TravelPost, pk=post_id)
    user = _get_current_or_default_user(request)

    with transaction.atomic():
        existing_like = PostLike.objects.filter(user=user, post=post).first()

        if request.method == "DELETE" or existing_like:
            if existing_like:
                existing_like.delete()
                # Atomic decrement
                TravelPost.objects.filter(pk=post_id, likes_count__gt=0).update(likes_count=F("likes_count") - 1)
                liked = False
            else:
                liked = False
        else:
            # Create like (idempotent with get_or_create)
            _, created = PostLike.objects.get_or_create(user=user, post=post)
            if created:
                # Atomic increment
                TravelPost.objects.filter(pk=post_id).update(likes_count=F("likes_count") + 1)
            liked = True

        post.refresh_from_db(fields=["likes_count"])

    return JsonResponse(
        {
            "liked": liked,
            "likes_count": post.likes_count,
            "message": "ถูกใจโพสต์เรียบร้อยแล้ว" if liked else "ยกเลิกถูกใจเรียบร้อยแล้ว",
        },
        status=200,
    )


@require_http_methods(["GET"])
def post_likes_list_view(request, post_id):
    """
    GET /api/posts/<id>/likes/ -> Get list of users who liked the post and total count.
    """
    post = get_object_or_404(TravelPost, pk=post_id)
    likes_qs = PostLike.objects.filter(post=post).select_related("user").order_by("-created_at")

    page_number = request.GET.get("page", 1)
    page_size = request.GET.get("page_size", 20)
    try:
        page_size = min(max(int(page_size), 1), 50)
    except (ValueError, TypeError):
        page_size = 20

    paginator = Paginator(likes_qs, page_size)
    try:
        likes_page = paginator.page(page_number)
    except (PageNotAnInteger, EmptyPage):
        likes_page = paginator.page(1) if int(page_number or 1) <= 1 else []

    users_list = [
        {
            "id": l.user.id,
            "username": l.user.username,
            "liked_at": l.created_at.isoformat(),
        }
        for l in (likes_page.object_list if hasattr(likes_page, "object_list") else likes_page)
    ]

    is_liked = False
    if request.user.is_authenticated:
        is_liked = PostLike.objects.filter(post=post, user=request.user).exists()

    return JsonResponse(
        {
            "post_id": post.id,
            "likes_count": post.likes_count,
            "is_liked": is_liked,
            "users": users_list,
            "count": paginator.count,
            "num_pages": paginator.num_pages,
            "current_page": likes_page.number if hasattr(likes_page, "number") else 1,
        },
        status=200,
    )


@require_http_methods(["GET", "POST"])
def post_comments_list_create_view(request, post_id):
    """
    GET /api/posts/<id>/comments/ -> List all comments on a post
    POST /api/posts/<id>/comments/ -> Add a new comment to a post
    """
    post = get_object_or_404(TravelPost, pk=post_id)

    if request.method == "GET":
        comments_qs = PostComment.objects.filter(post=post).select_related("user").order_by("created_at")
        comments_list = [_serialize_comment(c, request.user) for c in comments_qs]
        return JsonResponse(
            {
                "post_id": post.id,
                "comments_count": post.comments_count,
                "comments": comments_list,
            },
            status=200,
        )

    # POST - Create comment
    user = _get_current_or_default_user(request)
    data = _parse_json_body(request)
    if not data:
        return JsonResponse({"error": "Invalid request format"}, status=400)

    content = str(data.get("content", "")).strip()
    if not content:
        return JsonResponse({"error": "กรุณากรอกข้อความความคิดเห็น"}, status=400)

    if len(content) > 1000:
        return JsonResponse({"error": "ความคิดเห็นต้องไม่เกิน 1,000 ตัวอักษร"}, status=400)

    # Sanitize content
    sanitized_content = escape(content)

    with transaction.atomic():
        comment = PostComment.objects.create(
            user=user,
            post=post,
            content=sanitized_content,
        )
        TravelPost.objects.filter(pk=post_id).update(comments_count=F("comments_count") + 1)
        post.refresh_from_db(fields=["comments_count"])

    return JsonResponse(
        {
            "message": "เพิ่มความคิดเห็นเรียบร้อยแล้ว",
            "comment": _serialize_comment(comment, request.user),
            "comments_count": post.comments_count,
        },
        status=201,
    )


@require_http_methods(["DELETE"])
def post_comment_delete_view(request, post_id, comment_id):
    """
    DELETE /api/posts/<post_id>/comments/<comment_id>/ -> Delete a comment
    """
    post = get_object_or_404(TravelPost, pk=post_id)
    comment = get_object_or_404(PostComment, pk=comment_id, post=post)

    user = _get_current_or_default_user(request)
    can_delete = (
        not request.user.is_authenticated  # Demo mode fallback
        or comment.user_id == user.id
        or post.author_id == user.id
        or user.is_staff
        or user.is_superuser
    )

    if not can_delete:
        return JsonResponse({"error": "คุณไม่มีสิทธิ์ลบความคิดเห็นนี้"}, status=403)

    with transaction.atomic():
        comment.delete()
        # Atomic decrement, ensuring not negative
        current_count = TravelPost.objects.filter(pk=post_id).values_list("comments_count", flat=True).first() or 0
        if current_count > 0:
            TravelPost.objects.filter(pk=post_id).update(comments_count=F("comments_count") - 1)
        post.refresh_from_db(fields=["comments_count"])

    return JsonResponse(
        {
            "message": "ลบความคิดเห็นเรียบร้อยแล้ว",
            "comments_count": post.comments_count,
        },
        status=200,
    )

