import json
import re
from django.contrib.auth.models import User
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.html import escape
from django.views.decorators.http import require_http_methods

from .models import TravelPost


def _parse_json_body(request):
    """Safely parse JSON request body or POST dict."""
    if request.content_type == "application/json" and request.body:
        try:
            return json.loads(request.body.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return None
    return request.POST


def _extract_tagged_users(text_content, explicit_user_ids=None, explicit_usernames=None):
    """Extract User queryset based on @mentions in text and explicit arrays."""
    users_to_tag = set()

    if text_content:
        mentions = re.findall(r"@([a-zA-Z0-9_]+)", text_content)
        if mentions:
            mentioned_users = User.objects.filter(username__in=mentions)
            users_to_tag.update(mentioned_users)

    if explicit_user_ids and isinstance(explicit_user_ids, list):
        valid_ids = [uid for uid in explicit_user_ids if str(uid).isdigit()]
        if valid_ids:
            users_to_tag.update(User.objects.filter(id__in=valid_ids))

    if explicit_usernames and isinstance(explicit_usernames, list):
        valid_names = [str(name).strip().lstrip("@") for name in explicit_usernames if str(name).strip()]
        if valid_names:
            users_to_tag.update(User.objects.filter(username__in=valid_names))

    return list(users_to_tag)


def _serialize_post(post, current_user=None):
    """Serialize a TravelPost instance to dictionary."""
    is_owner = False
    is_admin = False
    is_tagged = False

    tagged_list = [
        {"id": u.id, "username": u.username}
        for u in post.tagged_users.all()
    ]

    if current_user and current_user.is_authenticated:
        is_owner = post.author_id == current_user.id
        is_admin = current_user.is_staff or current_user.is_superuser
        is_tagged = any(u["id"] == current_user.id for u in tagged_list)

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
        "tagged_users": tagged_list,
        "is_tagged": is_tagged,
        "is_owner": is_owner,
        "can_delete": is_owner or is_admin,
        "created_at": post.created_at.isoformat(),
        "updated_at": post.updated_at.isoformat(),
    }


@require_http_methods(["GET", "POST"])
def travel_posts_list_create_view(request):
    """
    GET /api/posts/ -> List all travel recommendation posts (with search & pagination)
    POST /api/posts/ -> Create new travel recommendation & review post
    """
    if request.method == "GET":
        category_filter = request.GET.get("category", "").strip()
        search_query = request.GET.get("q", "").strip()

        posts_qs = TravelPost.objects.select_related("author").prefetch_related("tagged_users").order_by("-created_at")

        if category_filter:
            posts_qs = posts_qs.filter(category=category_filter)
        if search_query:
            posts_qs = posts_qs.filter(
                Q(place_name__icontains=search_query)
                | Q(location__icontains=search_query)
                | Q(content__icontains=search_query)
                | Q(author__username__icontains=search_query)
            )

        page_number = request.GET.get("page", 1)
        page_size = request.GET.get("page_size", 10)
        try:
            page_size = min(max(int(page_size), 1), 50)
        except (ValueError, TypeError):
            page_size = 10

        paginator = Paginator(posts_qs, page_size)
        try:
            posts_page = paginator.page(page_number)
        except (PageNotAnInteger, EmptyPage):
            posts_page = paginator.page(1) if int(page_number or 1) <= 1 else []

        serialized_posts = [
            _serialize_post(p, request.user)
            for r in [posts_page]
            for p in (posts_page.object_list if hasattr(posts_page, "object_list") else posts_page)
        ]

        return JsonResponse({
            "count": paginator.count,
            "num_pages": paginator.num_pages,
            "current_page": posts_page.number if hasattr(posts_page, "number") else 1,
            "has_next": posts_page.has_next() if hasattr(posts_page, "has_next") else False,
            "has_previous": posts_page.has_previous() if hasattr(posts_page, "has_previous") else False,
            "results": serialized_posts,
            "posts": serialized_posts,
        }, status=200)

    # POST - Create Travel Review Post
    if not request.user.is_authenticated:
        return JsonResponse({"error": "กรุณาเข้าสู่ระบบก่อนสร้างโพสต์รีวิวสถานที่"}, status=401)

    data = _parse_json_body(request)
    if data is None:
        return JsonResponse({"error": "รูปแบบ JSON ไม่ถูกต้อง"}, status=400)

    place_name = str(data.get("place_name", "") or data.get("name", "")).strip()
    category = str(data.get("category", "")).strip() or "สถานที่ท่องเที่ยว"
    location = str(data.get("location", "")).strip()
    content = str(data.get("content", "") or data.get("comment", "")).strip()
    image_url = str(data.get("image_url", "")).strip()
    rating_raw = data.get("rating")
    explicit_tagged_ids = data.get("tagged_user_ids", [])
    explicit_tagged_names = data.get("tagged_usernames", [])

    if not place_name:
        return JsonResponse({"error": "กรุณาระบุชื่อสถานที่ท่องเที่ยว"}, status=400)

    # Validate rating
    try:
        rating = int(rating_raw)
        if rating < 1 or rating > 5:
            return JsonResponse({"error": "คะแนนดาวต้องเป็นจำนวนเต็มระหว่าง 1 ถึง 5"}, status=400)
    except (ValueError, TypeError):
        return JsonResponse({"error": "กรุณาเลือกระดับคะแนนดาว 1-5 ดาว"}, status=400)

    if not image_url:
        image_url = "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&auto=format&fit=crop&q=60"

    sanitized_content = escape(content)
    users_to_tag = _extract_tagged_users(content, explicit_tagged_ids, explicit_tagged_names)

    with transaction.atomic():
        post = TravelPost.objects.create(
            author=request.user,
            place_name=escape(place_name),
            category=escape(category),
            location=escape(location),
            rating=rating,
            content=sanitized_content,
            image_url=image_url,
        )
        if users_to_tag:
            post.tagged_users.set(users_to_tag)

    return JsonResponse(
        {
            "message": "สร้างโพสต์รีวิวสถานที่และแท็กเพื่อนเรียบร้อยแล้ว!",
            "post": _serialize_post(post, request.user),
            "review": _serialize_post(post, request.user),
        },
        status=201,
    )


@require_http_methods(["GET", "PUT", "DELETE"])
def travel_post_detail_view(request, post_id):
    """
    GET /api/posts/<id>/ -> View post
    PUT /api/posts/<id>/ -> Edit post (owner only)
    DELETE /api/posts/<id>/ -> Delete post (owner or admin only)
    """
    try:
        post = TravelPost.objects.select_related("author").prefetch_related("tagged_users").get(pk=post_id)
    except TravelPost.DoesNotExist:
        return JsonResponse({"error": "ไม่พบโพสต์สถานที่นี้"}, status=404)

    if request.method == "GET":
        return JsonResponse(_serialize_post(post, request.user), status=200)

    if not request.user.is_authenticated:
        return JsonResponse({"error": "กรุณาเข้าสู่ระบบก่อนทำรายการ"}, status=401)

    is_owner = post.author_id == request.user.id
    is_admin = request.user.is_staff or request.user.is_superuser

    if request.method == "PUT":
        if not is_owner:
            return JsonResponse({"error": "คุณสามารถแก้ไขได้เฉพาะโพสต์ของตัวเองเท่านั้น"}, status=403)

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

        content_changed = False
        if "content" in data or "comment" in data:
            raw_content = str(data.get("content", data.get("comment", ""))).strip()
            post.content = escape(raw_content)
            content_changed = True

        with transaction.atomic():
            post.save()
            if content_changed or "tagged_user_ids" in data or "tagged_usernames" in data:
                users_to_tag = _extract_tagged_users(
                    data.get("content", post.content),
                    explicit_user_ids=data.get("tagged_user_ids"),
                    explicit_usernames=data.get("tagged_usernames"),
                )
                post.tagged_users.set(users_to_tag)

        post.refresh_from_db()
        return JsonResponse(
            {
                "message": "แก้ไขโพสต์รีวิวเรียบร้อยแล้ว",
                "post": _serialize_post(post, request.user),
                "review": _serialize_post(post, request.user),
            },
            status=200,
        )

    if request.method == "DELETE":
        if not (is_owner or is_admin):
            return JsonResponse({"error": "คุณสามารถลบได้เฉพาะโพสต์ของตัวเองเท่านั้น (หรือผู้ดูแลระบบ)"}, status=403)

        post.delete()
        return JsonResponse({"message": "ลบโพสต์รีวิวสถานที่เรียบร้อยแล้ว"}, status=200)


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
