import json
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Avg, Count, Value
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Comment, Place, Review, Wishlist


def profile_view(request):
    """
    Personal profile page (My Profile) showing user avatar, name,
    clean zero-state review history, and personal wishlist.
    """
    user = request.user

    if user.is_authenticated:
        display_name = user.first_name if user.first_name else user.username
        username = user.username
        email = user.email if user.email else f"{username}@zonein.app"
        join_date = user.date_joined.strftime("%b %Y") if hasattr(user, "date_joined") and user.date_joined else "ก.ย. 2026"
    else:
        display_name = "User Profile"
        username = "user"
        email = "user@zonein.app"
        join_date = "ก.ย. 2026"

    # Clean placeholder: no mock data, stats default to 0
    reviews = []
    wishlist = []

    context = {
        "display_name": display_name,
        "username": username,
        "email": email,
        "join_date": join_date,
        "reviews": reviews,
        "wishlist": wishlist,
        "reviews_count": 0,
        "wishlist_count": 0,
        "likes_count": 0,
    }

    return render(request, "profile.html", context)


def _ensure_sample_data():
    """Seed initial popular places, recent reviews, and comments if empty."""
    if Place.objects.count() == 0:
        # Users
        u1, _ = User.objects.get_or_create(
            username="somchai_explorer",
            defaults={"email": "somchai@example.com", "first_name": "สมชาย"},
        )
        u2, _ = User.objects.get_or_create(
            username="ploy_wanderer",
            defaults={"email": "ploy@example.com", "first_name": "พลอย"},
        )
        u3, _ = User.objects.get_or_create(
            username="ton_backpacker",
            defaults={"email": "ton@example.com", "first_name": "ต้น"},
        )
        u4, _ = User.objects.get_or_create(
            username="traveler",
            defaults={"email": "traveler@example.com", "first_name": "นักเดินทาง"},
        )

        # Places
        p1 = Place.objects.create(
            author=u1,
            name="ผามออีแดง (อุทยานแห่งชาติเขาพระวิหาร)",
            address="อุทยานแห่งชาติเขาพระวิหาร ต.เสาธงชัย อ.กันทรลักษ์ จ.ศรีสะเกษ",
            category="travel",
            description="จุดชมวิวหน้าผาสูงตระหง่าน ชมทะเลหมอกและพระอาทิตย์ขึ้นสุดอลังการ มองเห็นผืนป่ากัมพูชาและภาพสลักนูนต่ำอายุกว่าพันปี",
            cover_image_url="https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=1000&auto=format&fit=crop&q=80",
            is_featured=True,
        )
        p2 = Place.objects.create(
            author=u2,
            name="ปราสาทหินสระกำแพงใหญ่",
            address="วัดสระกำแพงใหญ่ ต.สระกำแพงใหญ่ อ.อุทุมพรพิสัย จ.ศรีสะเกษ",
            category="culture",
            description="ปราสาทขอมโบราณที่สมบูรณ์และงดงามที่สุดแห่งหนึ่งในอีสานใต้ โดดเด่นด้วยทับหลังศิลาทรายแกะสลักอย่างประณีต",
            cover_image_url="https://images.unsplash.com/photo-1596422846543-75c6fc197f07?w=1000&auto=format&fit=crop&q=80",
            is_featured=True,
        )
        p3 = Place.objects.create(
            author=u3,
            name="วัดป่ามหาเจดีย์แก้ว (วัดล้านขวด)",
            address="บ้านดอน ต.สิ อ.ขุนหาญ จ.ศรีสะเกษ",
            category="culture",
            description="มหัศจรรย์สถาปัตยกรรมระดับโลกที่สร้างสรรค์จากขวดแก้วรีไซเคิลกว่า 1.5 ล้านขวด สะท้อนแสงอาทิตย์ระยิบระยับสวยงาม",
            cover_image_url="https://images.unsplash.com/photo-1548013146-72479768bada?w=1000&auto=format&fit=crop&q=80",
            is_featured=True,
        )
        p4 = Place.objects.create(
            author=u4,
            name="ไก่ย่างไม้มะดัน ห้วยทับทัน",
            address="ริมทางหลวง 226 ต.ห้วยทับทัน อ.ห้วยทับทัน จ.ศรีสะเกษ",
            category="restaurant",
            description="ของดีเมืองศรีสะเกษ ไก่บ้านหมักเครื่องเทศย่างด้วยไม้มะดันสด หอมกลิ่นควันไม้และสมุนไพรเฉพาะตัว",
            cover_image_url="https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=1000&auto=format&fit=crop&q=80",
            is_featured=True,
        )

        # Reviews
        r1 = Review.objects.create(
            place=p1,
            user=u1,
            rating=5,
            comment="ทะเลหมอกยามเช้าสวยงามอลังการมาก อากาศสดชื่น ประทับใจ 5 ดาวเต็ม",
            image_url="https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=1000&auto=format&fit=crop&q=80",
        )
        r2 = Review.objects.create(
            place=p2,
            user=u2,
            rating=5,
            comment="ปราสาทโบราณที่สมบูรณ์มาก สัมผัสประวัติศาสตร์พันปี ถ่ายรูปสวยทุกมุม",
            image_url="",
        )
        r3 = Review.objects.create(
            place=p3,
            user=u3,
            rating=4,
            comment="แปลกตาและงดงามมาก สร้างจากขวดแก้วจริงๆ น่าทึ่งมาก",
            image_url="",
        )
        r4 = Review.objects.create(
            place=p4,
            user=u4,
            rating=5,
            comment="ไก่ย่างหอมไม้มะดัน หนังกรอบเนื้อนุ่ม ส้มตำแซ่บมาก",
            image_url="",
        )

        # Seed comments
        Comment.objects.create(
            review=r1, author=u2, content="เห็นรูปแล้วอยากไปตามรอยเลยครับ มุมสวยมาก!"
        )
        Comment.objects.create(
            review=r1, author=u3, content="ช่วงเย็นคนเยอะไหมครับ กำลังวางแผนไปเสาร์นี้"
        )


def get_user_wishlist_place_ids(request):
    if request.user.is_authenticated:
        return set(
            Wishlist.objects.filter(user=request.user).values_list("place_id", flat=True)
        )
    return set(request.session.get("wishlist", []))


def home_view(request, active_tab="home"):
    """Render the Home Page Feed and Search/Explore integrated view."""
    _ensure_sample_data()
    places = Place.objects.all().order_by("-created_at")
    category_map = dict(Place.CATEGORY_CHOICES)
    wishlist_ids = get_user_wishlist_place_ids(request)

    explore_items = []
    for p in places:
        cat_name = category_map.get(p.category, p.category)
        explore_items.append(
            {
                "id": p.id,
                "title": p.name,
                "category": p.category,
                "category_name": cat_name,
                "location": p.location or p.address or "ศรีสะเกษ",
                "rating": p.average_rating if p.average_rating else 4.8,
                "image_url": p.image_url
                or p.cover_image_url
                or "https://images.unsplash.com/photo-1554118811-1e0d58224f24?w=1000&auto=format&fit=crop&q=80",
                "is_video": (p.id % 2 == 1),
                "detail_url": f"/places/{p.id}/",
                "is_wishlisted": p.id in wishlist_ids,
            }
        )

    categories = [
        {"name": "สถานที่ท่องเที่ยว & ธรรมชาติ", "slug": "travel", "icon": "fa-mountain-sun", "color": "#10b981"},
        {"name": "โบราณสถาน & วัดวาอาราม", "slug": "culture", "icon": "fa-landmark-dome", "color": "#8b5cf6"},
        {"name": "คาเฟ่ & กาแฟ", "slug": "cafe", "icon": "fa-mug-hot", "color": "#f97316"},
        {"name": "ร้านอาหาร & สตรีทฟู้ด", "slug": "restaurant", "icon": "fa-utensils", "color": "#ef4444"},
        {"name": "ที่พัก & โรงแรม", "slug": "hotel", "icon": "fa-bed", "color": "#3b82f6"},
    ]

    locations = [
        {"city": "ศรีสะเกษ", "zone": "อ.เมืองศรีสะเกษ", "slug": "ssk-muang"},
        {"city": "ศรีสะเกษ", "zone": "อ.กันทรลักษ์ (ผามออีแดง - เขาพระวิหาร)", "slug": "ssk-kantharalak"},
        {"city": "ศรีสะเกษ", "zone": "อ.ขุนหาญ (วัดล้านขวด - น้ำตก)", "slug": "ssk-khunhan"},
        {"city": "ศรีสะเกษ", "zone": "อ.อุทุมพรพิสัย (ปราสาทสระกำแพงใหญ่)", "slug": "ssk-uthumphon"},
        {"city": "ศรีสะเกษ", "zone": "อ.ห้วยทับทัน (ไก่ย่างไม้มะดัน)", "slug": "ssk-huai-thap-than"},
        {"city": "ศรีสะเกษ", "zone": "อ.ปรางค์กู่ (ปราสาทปรางค์กู่)", "slug": "ssk-prang-ku"},
        {"city": "ศรีสะเกษ", "zone": "อ.ราษีไศล (เขื่อนราษีไศล)", "slug": "ssk-rasi-salai"},
    ]

    context = {
        "places": places,
        "explore_items": explore_items,
        "active_tab": active_tab,
        "categories": categories,
        "locations": locations,
        "total_count": places.count(),
        "all_places_count": places.count(),
        "wishlist_ids": wishlist_ids,
        "filters": {
            "q": request.GET.get("q", ""),
            "category": request.GET.get("category", "all"),
            "location": request.GET.get("location", "all"),
            "min_rating": request.GET.get("min_rating", ""),
            "sort": request.GET.get("sort", "rating"),
        },
    }

    # Render index.html for main page
    return render(request, "index.html", context)


def search_view(request):
    """Render the Search / Explore page view directly."""
    return home_view(request, active_tab="search")


def index(request):
    """Alias for main view."""
    return home_view(request)


def index_view(request):
    """Alias for main index view."""
    return home_view(request)


def signin_view(request):
    """Sign In / Login view supporting username, email, and social login."""
    if request.method == "POST":
        identifier = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        remember_me = request.POST.get("remember_me")

        username_to_try = identifier
        if "@" in identifier:
            matched_user = User.objects.filter(email__iexact=identifier).first()
            if matched_user:
                username_to_try = matched_user.username

        user = authenticate(request, username=username_to_try, password=password)
        if user is not None:
            login(request, user)
            if not remember_me:
                request.session.set_expiry(0)
            else:
                request.session.set_expiry(2592000)

            display_name = user.first_name if user.first_name else user.username
            messages.success(request, f"ยินดีต้อนรับ, {display_name}! เข้าสู่ระบบสำเร็จแล้ว")
            return redirect("web:index")
        else:
            messages.error(request, "ชื่อผู้ใช้/อีเมล หรือรหัสผ่านไม่ถูกต้อง โปรดลองใหม่อีกครั้ง")

    return render(request, "signin.html")


def signup_view(request):
    """Sign Up / Registration view with input validation and instant login."""
    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if not username or not email or not password:
            messages.error(request, "กรุณากรอกข้อมูลให้ครบถ้วนทุกช่อง")
            return render(
                request,
                "signup.html",
                {"full_name": full_name, "username": username, "email": email},
            )

        if len(password) < 6:
            messages.error(request, "รหัสผ่านต้องมีความยาวอย่างน้อย 6 ตัวอักษร")
            return render(
                request,
                "signup.html",
                {"full_name": full_name, "username": username, "email": email},
            )

        if password != confirm_password:
            messages.error(request, "รหัสผ่านและการยืนยันรหัสผ่านไม่ตรงกัน")
            return render(
                request,
                "signup.html",
                {"full_name": full_name, "username": username, "email": email},
            )

        if User.objects.filter(username__iexact=username).exists():
            messages.error(request, f"ชื่อผู้ใช้ '{username}' มีผู้ใช้งานแล้ว โปรดเลือกชื่ออื่น")
            return render(
                request, "signup.html", {"full_name": full_name, "email": email}
            )

        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, f"อีเมล '{email}' เคยลงทะเบียนแล้ว โปรดเข้าสู่ระบบ")
            return render(
                request, "signup.html", {"full_name": full_name, "username": username}
            )

        new_user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=full_name if full_name else username,
        )
        login(request, new_user)
        messages.success(
            request, f"สมัครสมาชิกสำเร็จ! ยินดีต้อนรับสู่ Zone In, {new_user.first_name}"
        )
        return redirect("web:index")

    return render(request, "signup.html")


def social_login_view(request, provider):
    """Social Login endpoint for Google and Facebook."""
    provider = provider.lower()

    if provider == "google":
        username = "google_user"
        email = "user.google@zonein.app"
        display_name = "Google User"
        provider_name = "Google"
    elif provider == "facebook":
        username = "facebook_user"
        email = "user.facebook@zonein.app"
        display_name = "Facebook User"
        provider_name = "Facebook"
    else:
        messages.error(request, "ผู้ให้บริการไม่ถูกต้อง")
        return redirect("web:signin")

    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            "email": email,
            "first_name": display_name,
        },
    )

    if created:
        user.set_unusable_password()
        user.save()

    login(request, user)
    action_text = "สมัครและเข้าสู่ระบบ" if created else "เข้าสู่ระบบ"
    messages.success(request, f"{action_text}ด้วย {provider_name} สำเร็จเรียบร้อยแล้ว!")
    return redirect("web:index")


def logout_view(request):
    """Logs out the user and redirects with a confirmation message."""
    logout(request)
    messages.info(request, "ออกจากระบบเรียบร้อยแล้ว")
    return redirect("web:signin")


# ==============================================================================
# Home Page Feed Backend APIs
# ==============================================================================
@require_http_methods(["GET"])
def api_popular_places(request):
    """GET /api/places/popular?page=1&limit=6"""
    _ensure_sample_data()
    page = request.GET.get("page", 1)
    limit = min(int(request.GET.get("limit", 6)), 50)

    places_qs = Place.objects.annotate(
        avg_rating=Coalesce(Avg("reviews__rating"), Value(0.0)),
        review_count_val=Count("reviews"),
    ).order_by("-avg_rating", "-review_count_val", "-created_at")

    paginator = Paginator(places_qs, limit)
    try:
        page_obj = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.page(1)

    results = []
    for place in page_obj:
        results.append(
            {
                "id": place.id,
                "name": place.name,
                "location": place.location,
                "category": place.category,
                "description": place.description,
                "image_url": place.image_url,
                "average_rating": (
                    round(place.avg_rating, 1) if place.avg_rating else 0.0
                ),
                "reviews_count": place.review_count_val,
                "created_at": place.created_at.isoformat(),
            }
        )

    return JsonResponse(
        {
            "places": results,
            "total": paginator.count,
            "page": page_obj.number,
            "num_pages": paginator.num_pages,
            "has_next": page_obj.has_next(),
        }
    )


@require_http_methods(["GET"])
def api_recent_reviews(request):
    """GET /api/reviews/recent?page=1&limit=6"""
    _ensure_sample_data()
    page = request.GET.get("page", 1)
    limit = min(int(request.GET.get("limit", 6)), 50)

    reviews_qs = (
        Review.objects.select_related("user", "place")
        .prefetch_related("comments__author")
        .order_by("-created_at")
    )

    paginator = Paginator(reviews_qs, limit)
    try:
        page_obj = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.page(1)

    results = []
    for review in page_obj:
        comments_data = [
            {
                "id": c.id,
                "content": c.content,
                "created_at": c.created_at.isoformat(),
                "author": {
                    "id": c.author.id,
                    "username": c.author.username,
                    "nickname": getattr(
                        getattr(c.author, "profile", None), "nickname", ""
                    )
                    or c.author.username,
                },
            }
            for c in review.comments.all()
        ]
        results.append(
            {
                "id": review.id,
                "rating": review.rating,
                "content": review.content,
                "image_url": review.image_url
                or (review.place.cover_image_url if review.place else ""),
                "created_at": review.created_at.isoformat(),
                "author": {
                    "id": review.user.id,
                    "username": review.user.username,
                    "nickname": getattr(
                        getattr(review.user, "profile", None), "nickname", ""
                    )
                    or review.user.username,
                },
                "place": {
                    "id": review.place.id,
                    "name": review.place.name,
                    "location": review.place.location,
                    "category": review.place.category,
                },
                "comments": comments_data,
                "comments_count": len(comments_data),
            }
        )

    return JsonResponse(
        {
            "reviews": results,
            "total": paginator.count,
            "page": page_obj.number,
            "num_pages": paginator.num_pages,
            "has_next": page_obj.has_next(),
        }
    )


@csrf_exempt
@require_http_methods(["POST"])
def api_add_comment(request, review_id):
    """POST /api/reviews/<review_id>/comments/"""
    review = get_object_or_404(Review, pk=review_id)
    try:
        data = json.loads(request.body.decode("utf-8")) if request.body else {}
    except json.JSONDecodeError:
        data = request.POST

    content = data.get("content", "").strip()
    if not content:
        return JsonResponse({"error": "Content cannot be empty"}, status=400)

    username = data.get("username", "").strip()
    if request.user.is_authenticated and not username:
        author = request.user
    else:
        username = username or "traveler"
        author, _ = User.objects.get_or_create(
            username=username, defaults={"email": f"{username}@example.com"}
        )

    comment = Comment.objects.create(review=review, author=author, content=content)
    return JsonResponse(
        {
            "success": True,
            "comment": {
                "id": comment.id,
                "content": comment.content,
                "created_at": comment.created_at.isoformat(),
                "author": {
                    "id": comment.author.id,
                    "username": comment.author.username,
                },
            },
        },
        status=201,
    )


@csrf_exempt
@require_http_methods(["POST", "PUT"])
def api_edit_review(request, review_id):
    """POST /api/reviews/<review_id>/edit/"""
    review = get_object_or_404(Review, pk=review_id)
    try:
        data = json.loads(request.body.decode("utf-8")) if request.body else {}
    except json.JSONDecodeError:
        data = request.POST

    content = data.get("content")
    if content is not None:
        review.content = content.strip()

    rating = data.get("rating")
    if rating is not None:
        try:
            rating_val = int(rating)
            if 1 <= rating_val <= 5:
                review.rating = rating_val
        except (ValueError, TypeError):
            pass

    review.save()
    return JsonResponse(
        {
            "success": True,
            "review": {
                "id": review.id,
                "rating": review.rating,
                "content": review.content,
                "created_at": review.created_at.isoformat(),
            },
        }
    )


@csrf_exempt
@require_http_methods(["POST", "DELETE"])
def api_delete_review(request, review_id):
    """POST /api/reviews/<review_id>/delete/"""
    review = get_object_or_404(Review, pk=review_id)
    review.delete()
    return JsonResponse({"success": True, "message": "Review deleted successfully"})


@require_http_methods(["GET"])
def api_place_detail(request, place_id):
    """GET /api/places/<place_id>/ -> Place detail."""
    place = get_object_or_404(Place, pk=place_id)
    return JsonResponse(
        {
            "id": place.id,
            "name": place.name,
            "location": place.location,
            "category": place.category,
            "description": place.description,
            "image_url": place.image_url,
            "average_rating": place.average_rating,
            "reviews_count": place.reviews_count,
            "created_at": place.created_at.isoformat(),
        }
    )


@require_http_methods(["GET"])
def api_review_detail(request, review_id):
    """GET /api/reviews/<review_id>/ -> Review detail."""
    review = get_object_or_404(
        Review.objects.select_related("user", "place"), pk=review_id
    )
    return JsonResponse(
        {
            "id": review.id,
            "rating": review.rating,
            "content": review.content,
            "image_url": review.image_url,
            "created_at": review.created_at.isoformat(),
            "author": {
                "id": review.user.id,
                "username": review.user.username,
            },
            "place": {
                "id": review.place.id,
                "name": review.place.name,
                "location": review.place.location,
                "category": review.place.category,
            },
        }
    )


def api_places_view(request):
    """Places search API for search filter."""
    wishlist_ids = get_user_wishlist_place_ids(request)
    q = request.GET.get("q", "").strip()
    category = request.GET.get("category", "").strip()
    location = request.GET.get("location", "").strip()
    min_rating = request.GET.get("min_rating", "").strip()
    sort = request.GET.get("sort", "rating").strip()

    qs = Place.objects.all()

    if q:
        from django.db.models import Q
        qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q) | Q(address__icontains=q) | Q(tags__icontains=q))
    if category and category != "all":
        qs = qs.filter(category=category)
    if location and location != "all":
        qs = qs.filter(address__icontains=location)

    category_map = dict(Place.CATEGORY_CHOICES)
    data = []
    for p in qs:
        cat_name = category_map.get(p.category, p.category)
        data.append(
            {
                "id": p.id,
                "name": p.name,
                "slug": p.slug,
                "description": p.description,
                "address": p.address,
                "location": {"zone": p.address},
                "category": {"name": cat_name, "slug": p.category, "color": "#10b981", "icon": "fa-location-dot"},
                "image_url": p.image_url or p.cover_image_url or "https://images.unsplash.com/photo-1554118811-1e0d58224f24?w=600&auto=format&fit=crop&q=80",
                "rating": float(p.rating),
                "review_count": p.review_count,
                "price_display": p.price_display,
                "tags": p.tag_list,
                "is_featured": p.is_featured,
                "is_wishlisted": p.id in wishlist_ids,
            }
        )

    # Sort
    if sort == "reviews":
        data.sort(key=lambda x: x["review_count"], reverse=True)
    elif sort == "newest":
        data.sort(key=lambda x: x["id"], reverse=True)
    elif sort == "name":
        data.sort(key=lambda x: x["name"])
    else:  # rating
        data.sort(key=lambda x: x["rating"], reverse=True)

    return JsonResponse({"status": "success", "count": len(data), "places": data})


def place_detail(request, place_id=None, slug=None):
    """หน้ารายละเอียดสถานที่ (Place Details View)"""
    place = None
    if place_id:
        place = Place.objects.filter(id=place_id).first()
    elif slug:
        place = Place.objects.filter(slug=slug).first()

    if not place:
        place = Place.objects.first()

    if not place:
        return redirect("web:index")

    wishlist_ids = get_user_wishlist_place_ids(request)
    related_places = Place.objects.filter(category=place.category).exclude(id=place.id)[:3]

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


def place_detail_view(request, slug):
    """Slug-based place detail view."""
    return place_detail(request, slug=slug)


# ==============================================================================
# Wishlist Views
# ==============================================================================
def wishlist_page_view(request):
    """Wishlist page view."""
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

    if request.user.is_authenticated:
        wishlist_item = Wishlist.objects.filter(user=request.user, place=place).first()
        if wishlist_item:
            wishlist_item.delete()
            action = "removed"
        else:
            Wishlist.objects.create(user=request.user, place=place)
            action = "added"
        total_count = Wishlist.objects.filter(user=request.user).count()
    else:
        wishlist = request.session.get("wishlist", [])
        pid = int(place_id)
        if pid in wishlist:
            wishlist.remove(pid)
            action = "removed"
        else:
            wishlist.append(pid)
            action = "added"
        request.session["wishlist"] = wishlist
        request.session.modified = True
        total_count = len(wishlist)

    return JsonResponse(
        {
            "status": "success",
            "success": True,
            "action": action,
            "place_id": place.id,
            "place_name": place.name,
            "total_count": total_count,
            "is_wishlisted": (action == "added"),
            "is_saved": (action == "added"),
        }
    )


def api_wishlist_list_view(request):
    if request.user.is_authenticated:
        wishlist_qs = Wishlist.objects.filter(user=request.user).select_related("place")
        places = [item.place for item in wishlist_qs]
    else:
        wishlist_ids = request.session.get("wishlist", [])
        places = list(Place.objects.filter(id__in=wishlist_ids))

    place_ids = [p.id for p in places]
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
            }
        )

    return JsonResponse(
        {
            "status": "success",
            "success": True,
            "count": len(data),
            "place_ids": place_ids,
            "places": data,
        }
    )
