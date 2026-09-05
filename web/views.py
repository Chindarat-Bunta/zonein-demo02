import json
from django.contrib.auth.models import User
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Avg, Count, Value
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import Comment, Place, Review


def _ensure_sample_data():
    """Seed initial popular places, recent reviews, and comments if empty."""
    if Place.objects.count() == 0:
        # Users
        u1, _ = User.objects.get_or_create(username="somchai_explorer", defaults={"email": "somchai@example.com"})
        u2, _ = User.objects.get_or_create(username="ploy_wanderer", defaults={"email": "ploy@example.com"})
        u3, _ = User.objects.get_or_create(username="ton_backpacker", defaults={"email": "ton@example.com"})
        u4, _ = User.objects.get_or_create(username="traveler", defaults={"email": "traveler@example.com"})

        # Places
        p1 = Place.objects.create(
            name="สวนป่าเบญจกิติ (Benchakitti Forest Park)",
            location="คลองเตย กรุงเทพมหานคร",
            category="ธรรมชาติ & สวนสาธารณะ",
            description="สวนสาธารณะขนาดใหญ่ใจกลางเมือง พร้อม Skywalk ยาวกว่า 1.6 กิโลเมตร ชมวิวบึงน้ำและตึกระฟ้า",
            image_url="https://images.unsplash.com/photo-1596422846543-75c6fc197f07?w=1000&auto=format&fit=crop&q=80",
        )
        p2 = Place.objects.create(
            name="Riva Floating Cafe คาเฟ่แพริมน้ำ",
            location="อ.สามพราน จ.นครปฐม",
            category="คาเฟ่ริมน้ำ & ของกิน",
            description="คาเฟ่สไตล์แพลอยน้ำริมแม่น้ำท่าจีน บรรยากาศสุดชิลล์ นั่งห้อยขาจิบกาแฟและเค้กมะพร้าวอ่อน",
            image_url="https://images.unsplash.com/photo-1554118811-1e0d58224f24?w=1000&auto=format&fit=crop&q=80",
        )
        p3 = Place.objects.create(
            name="จุดชมวิวผาเดียวดาย & ลานกางเต็นท์ลำตะคอง",
            location="อุทยานแห่งชาติเขาใหญ่ จ.นครราชสีมา",
            category="แคมป์ปิ้ง & ภูเขา",
            description="สัมผัสอากาศหนาวและทะเลหมอกยามเช้า จุดกางเต็นท์ริมน้ำ ชมดาวเต็มท้องฟ้า",
            image_url="https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=1000&auto=format&fit=crop&q=80",
        )
        p4 = Place.objects.create(
            name="หาดไร่เลย์ (Railay Beach)",
            location="อ.เมือง จ.กระบี่",
            category="ทะเล & เกาะ",
            description="หาดทรายขาวละเอียดล้อมรอบด้วยหน้าผาหินปูนสูงตระหง่าน แหล่งปีนผาระดับโลกและจุดชมพระอาทิตย์ตก",
            image_url="https://images.unsplash.com/photo-1552465011-b4e21bf6e79a?w=1000&auto=format&fit=crop&q=80",
        )
        p5 = Place.objects.create(
            name="วัดร่องขุ่น (White Temple)",
            location="อ.เมือง จ.เชียงราย",
            category="วัด & ศิลปวัฒนธรรม",
            description="พุทธศิลป์สีขาวบริสุทธิ์อันวิจิตรอลังการ ผลงานชิ้นเอกโดยอาจารย์เฉลิมชัย โฆษิตพิพัฒน์",
            image_url="https://images.unsplash.com/photo-1528181304800-259b08848526?w=1000&auto=format&fit=crop&q=80",
        )

        # Reviews
        r1 = Review.objects.create(
            place=p1,
            author=u1,
            rating=5,
            content="สวนสวยอลังการมาก! ทางเดินลอยฟ้าถ่ายรูปสวยทุกมุม แนะนำให้มาช่วง 17.00 น. แสงกำลังละมุนลมเย็นสบาย",
            image_url="https://images.unsplash.com/photo-1596422846543-75c6fc197f07?w=1000&auto=format&fit=crop&q=80",
        )
        r2 = Review.objects.create(
            place=p1,
            author=u2,
            rating=5,
            content="พื้นที่กว้างขวาง เหมาะมากกับการมาวิ่งออกกำลังกายและปั่นจักรยาน มีที่จอดรถสะดวกสบาย",
            image_url="",
        )
        r3 = Review.objects.create(
            place=p2,
            author=u2,
            rating=4,
            content="กาแฟหอม ขนมอร่อย นั่งชิลล์ห้อยขาริมแม่น้ำบรรยากาศดีมาก คนเยอะช่วงวันหยุดแนะนำให้มาช่วงเช้า",
            image_url="https://images.unsplash.com/photo-1554118811-1e0d58224f24?w=1000&auto=format&fit=crop&q=80",
        )
        r4 = Review.objects.create(
            place=p3,
            author=u3,
            rating=5,
            content="กางเต็นท์นอนดูดาว ตื่นเช้ามาเจอทะเลหมอกที่ผาเดียวดาย อากาศ 16 องศา สดชื่นประทับใจสุดๆ",
            image_url="https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=1000&auto=format&fit=crop&q=80",
        )
        r5 = Review.objects.create(
            place=p4,
            author=u4,
            rating=5,
            content="น้ำทะเลใสมาก หน้าผาสวยงามตระการตา ได้ลองพายคายัครอบหาด ประทับใจ 5 ดาวเต็ม!",
            image_url="https://images.unsplash.com/photo-1552465011-b4e21bf6e79a?w=1000&auto=format&fit=crop&q=80",
        )
        r6 = Review.objects.create(
            place=p5,
            author=u1,
            rating=5,
            content="งดงามประณีตสมคำร่ำลือ ศิลปะสีขาวสะท้อนแสงแดดระยิบระยับ ต้องมาเห็นด้วยตาตัวเองสักครั้ง",
            image_url="https://images.unsplash.com/photo-1528181304800-259b08848526?w=1000&auto=format&fit=crop&q=80",
        )

        # Seed comments
        Comment.objects.create(review=r1, author=u2, content="เห็นรูปแล้วอยากไปตามรอยเลยครับ มุมสวยมาก!")
        Comment.objects.create(review=r1, author=u3, content="ช่วงเย็นคนเยอะไหมครับ กำลังวางแผนไปเสาร์นี้")
        Comment.objects.create(review=r6, author=u4, content="วัดสวยจริงครับ แดดสะท้อนกระจกวิบวับมาก")
    elif Comment.objects.count() == 0:
        u_sample, _ = User.objects.get_or_create(username="ploy_wanderer", defaults={"email": "ploy@example.com"})
        u_backpacker, _ = User.objects.get_or_create(username="ton_backpacker", defaults={"email": "ton@example.com"})
        first_review = Review.objects.first()
        if first_review:
            Comment.objects.create(review=first_review, author=u_sample, content="เห็นรูปแล้วอยากไปตามรอยเลยครับ มุมสวยมาก!")
            Comment.objects.create(review=first_review, author=u_backpacker, content="ช่วงเย็นคนเยอะไหมครับ กำลังวางแผนไปเสาร์นี้")


def home_view(request):
    """Render the Home Page Feed view."""
    _ensure_sample_data()
    return render(request, "web/home.html")


@require_http_methods(["GET"])
def api_popular_places(request):
    """
    GET /api/places/popular?page=1&limit=6
    ดึงรายการสถานที่ฮิต เรียงตามคะแนนดาวเฉลี่ยและจำนวนรีวิว
    """
    _ensure_sample_data()
    page = request.GET.get("page", 1)
    limit = min(int(request.GET.get("limit", 6)), 50)

    places_qs = (
        Place.objects.annotate(
            avg_rating=Coalesce(Avg("reviews__rating"), Value(0.0)),
            review_count=Count("reviews"),
        )
        .order_by("-avg_rating", "-review_count", "-created_at")
    )

    paginator = Paginator(places_qs, limit)
    try:
        page_obj = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.page(1)

    results = []
    for place in page_obj:
        results.append({
            "id": place.id,
            "name": place.name,
            "location": place.location,
            "category": place.category,
            "description": place.description,
            "image_url": place.image_url,
            "average_rating": round(place.avg_rating, 1) if place.avg_rating else 0.0,
            "reviews_count": place.review_count,
            "created_at": place.created_at.isoformat(),
        })

    return JsonResponse({
        "places": results,
        "total": paginator.count,
        "page": page_obj.number,
        "num_pages": paginator.num_pages,
        "has_next": page_obj.has_next(),
    })


@require_http_methods(["GET"])
def api_recent_reviews(request):
    """
    GET /api/reviews/recent?page=1&limit=6
    ดึงรีวิวล่าสุด เรียงตาม created_at DESC พร้อมข้อมูลผู้ใช้ สถานที่ และคอมเมนต์
    """
    _ensure_sample_data()
    page = request.GET.get("page", 1)
    limit = min(int(request.GET.get("limit", 6)), 50)

    reviews_qs = (
        Review.objects.select_related("author", "place")
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
                },
            }
            for c in review.comments.all()
        ]
        results.append({
            "id": review.id,
            "rating": review.rating,
            "content": review.content,
            "image_url": review.image_url,
            "created_at": review.created_at.isoformat(),
            "author": {
                "id": review.author.id,
                "username": review.author.username,
            },
            "place": {
                "id": review.place.id,
                "name": review.place.name,
                "location": review.place.location,
                "category": review.place.category,
            },
            "comments": comments_data,
            "comments_count": len(comments_data),
        })

    return JsonResponse({
        "reviews": results,
        "total": paginator.count,
        "page": page_obj.number,
        "num_pages": paginator.num_pages,
        "has_next": page_obj.has_next(),
    })


@csrf_exempt
@require_http_methods(["POST"])
def api_add_comment(request, review_id):
    """
    POST /api/reviews/<review_id>/comments/
    เพิ่มคอมเมนต์ในรีวิว
    """
    review = get_object_or_404(Review, pk=review_id)
    try:
        data = json.loads(request.body.decode("utf-8")) if request.body else {}
    except json.JSONDecodeError:
        data = request.POST

    content = data.get("content", "").strip()
    if not content:
        return JsonResponse({"error": "Content cannot be empty"}, status=400)

    username = data.get("username", "").strip() or "traveler"
    author, _ = User.objects.get_or_create(username=username, defaults={"email": f"{username}@example.com"})

    comment = Comment.objects.create(review=review, author=author, content=content)
    return JsonResponse({
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
    }, status=201)


@csrf_exempt
@require_http_methods(["POST", "PUT"])
def api_edit_review(request, review_id):
    """
    POST /api/reviews/<review_id>/edit/
    แก้ไขข้อความและคะแนนรีวิว
    """
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
    return JsonResponse({
        "success": True,
        "review": {
            "id": review.id,
            "rating": review.rating,
            "content": review.content,
            "created_at": review.created_at.isoformat(),
        },
    })


@csrf_exempt
@require_http_methods(["POST", "DELETE"])
def api_delete_review(request, review_id):
    """
    POST /api/reviews/<review_id>/delete/
    ลบรีวิว
    """
    review = get_object_or_404(Review, pk=review_id)
    review.delete()
    return JsonResponse({"success": True, "message": "Review deleted successfully"})


@require_http_methods(["GET"])
def api_place_detail(request, place_id):
    """GET /api/places/<place_id>/ -> Place detail."""
    place = get_object_or_404(Place, pk=place_id)
    return JsonResponse({
        "id": place.id,
        "name": place.name,
        "location": place.location,
        "category": place.category,
        "description": place.description,
        "image_url": place.image_url,
        "average_rating": place.average_rating,
        "reviews_count": place.reviews_count,
        "created_at": place.created_at.isoformat(),
    })


@require_http_methods(["GET"])
def api_review_detail(request, review_id):
    """GET /api/reviews/<review_id>/ -> Review detail."""
    review = get_object_or_404(Review.objects.select_related("author", "place"), pk=review_id)
    return JsonResponse({
        "id": review.id,
        "rating": review.rating,
        "content": review.content,
        "image_url": review.image_url,
        "created_at": review.created_at.isoformat(),
        "author": {
            "id": review.author.id,
            "username": review.author.username,
        },
        "place": {
            "id": review.place.id,
            "name": review.place.name,
            "location": review.place.location,
            "category": review.place.category,
        },
    })


def _ensure_sample_data():
    """Seed initial popular places and recent reviews if empty."""
    if Place.objects.count() == 0:
        # Users
        u1, _ = User.objects.get_or_create(username="somchai_explorer", defaults={"email": "somchai@example.com"})
        u2, _ = User.objects.get_or_create(username="ploy_wanderer", defaults={"email": "ploy@example.com"})
        u3, _ = User.objects.get_or_create(username="ton_backpacker", defaults={"email": "ton@example.com"})
        u4, _ = User.objects.get_or_create(username="traveler", defaults={"email": "traveler@example.com"})

        # Places
        p1 = Place.objects.create(
            name="สวนป่าเบญจกิติ (Benchakitti Forest Park)",
            location="คลองเตย กรุงเทพมหานคร",
            category="ธรรมชาติ & สวนสาธารณะ",
            description="สวนสาธารณะขนาดใหญ่ใจกลางเมือง พร้อม Skywalk ยาวกว่า 1.6 กิโลเมตร ชมวิวบึงน้ำและตึกระฟ้า",
            image_url="https://images.unsplash.com/photo-1596422846543-75c6fc197f07?w=1000&auto=format&fit=crop&q=80",
        )
        p2 = Place.objects.create(
            name="Riva Floating Cafe คาเฟ่แพริมน้ำ",
            location="อ.สามพราน จ.นครปฐม",
            category="คาเฟ่ริมน้ำ & ของกิน",
            description="คาเฟ่สไตล์แพลอยน้ำริมแม่น้ำท่าจีน บรรยากาศสุดชิลล์ นั่งห้อยขาจิบกาแฟและเค้กมะพร้าวอ่อน",
            image_url="https://images.unsplash.com/photo-1554118811-1e0d58224f24?w=1000&auto=format&fit=crop&q=80",
        )
        p3 = Place.objects.create(
            name="จุดชมวิวผาเดียวดาย & ลานกางเต็นท์ลำตะคอง",
            location="อุทยานแห่งชาติเขาใหญ่ จ.นครราชสีมา",
            category="แคมป์ปิ้ง & ภูเขา",
            description="สัมผัสอากาศหนาวและทะเลหมอกยามเช้า จุดกางเต็นท์ริมน้ำ ชมดาวเต็มท้องฟ้า",
            image_url="https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=1000&auto=format&fit=crop&q=80",
        )
        p4 = Place.objects.create(
            name="หาดไร่เลย์ (Railay Beach)",
            location="อ.เมือง จ.กระบี่",
            category="ทะเล & เกาะ",
            description="หาดทรายขาวละเอียดล้อมรอบด้วยหน้าผาหินปูนสูงตระหง่าน แหล่งปีนผาระดับโลกและจุดชมพระอาทิตย์ตก",
            image_url="https://images.unsplash.com/photo-1552465011-b4e21bf6e79a?w=1000&auto=format&fit=crop&q=80",
        )
        p5 = Place.objects.create(
            name="วัดร่องขุ่น (White Temple)",
            location="อ.เมือง จ.เชียงราย",
            category="วัด & ศิลปวัฒนธรรม",
            description="พุทธศิลป์สีขาวบริสุทธิ์อันวิจิตรอลังการ ผลงานชิ้นเอกโดยอาจารย์เฉลิมชัย โฆษิตพิพัฒน์",
            image_url="https://images.unsplash.com/photo-1528181304800-259b08848526?w=1000&auto=format&fit=crop&q=80",
        )

        # Reviews
        Review.objects.create(
            place=p1,
            author=u1,
            rating=5,
            content="สวนสวยอลังการมาก! ทางเดินลอยฟ้าถ่ายรูปสวยทุกมุม แนะนำให้มาช่วง 17.00 น. แสงกำลังละมุนลมเย็นสบาย",
            image_url="https://images.unsplash.com/photo-1596422846543-75c6fc197f07?w=1000&auto=format&fit=crop&q=80",
        )
        Review.objects.create(
            place=p1,
            author=u2,
            rating=5,
            content="พื้นที่กว้างขวาง เหมาะมากกับการมาวิ่งออกกำลังกายและปั่นจักรยาน มีที่จอดรถสะดวกสบาย",
            image_url="",
        )
        Review.objects.create(
            place=p2,
            author=u2,
            rating=4,
            content="กาแฟหอม ขนมอร่อย นั่งชิลล์ห้อยขาริมแม่น้ำบรรยากาศดีมาก คนเยอะช่วงวันหยุดแนะนำให้มาช่วงเช้า",
            image_url="https://images.unsplash.com/photo-1554118811-1e0d58224f24?w=1000&auto=format&fit=crop&q=80",
        )
        Review.objects.create(
            place=p3,
            author=u3,
            rating=5,
            content="กางเต็นท์นอนดูดาว ตื่นเช้ามาเจอทะเลหมอกที่ผาเดียวดาย อากาศ 16 องศา สดชื่นประทับใจสุดๆ",
            image_url="https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=1000&auto=format&fit=crop&q=80",
        )
        Review.objects.create(
            place=p4,
            author=u4,
            rating=5,
            content="น้ำทะเลใสมาก หน้าผาสวยงามตระการตา ได้ลองพายคายัครอบหาด ประทับใจ 5 ดาวเต็ม!",
            image_url="https://images.unsplash.com/photo-1552465011-b4e21bf6e79a?w=1000&auto=format&fit=crop&q=80",
        )
        Review.objects.create(
            place=p5,
            author=u1,
            rating=5,
            content="งดงามประณีตสมคำร่ำลือ ศิลปะสีขาวสะท้อนแสงแดดระยิบระยับ ต้องมาเห็นด้วยตาตัวเองสักครั้ง",
            image_url="https://images.unsplash.com/photo-1528181304800-259b08848526?w=1000&auto=format&fit=crop&q=80",
        )


def home_view(request):
    """Render the Home Page Feed view."""
    _ensure_sample_data()
    return render(request, "web/home.html")


@require_http_methods(["GET"])
def api_popular_places(request):
    """
    GET /api/places/popular?page=1&limit=6
    ดึงรายการสถานที่ฮิต เรียงตามคะแนนดาวเฉลี่ยและจำนวนรีวิว
    """
    _ensure_sample_data()
    page = request.GET.get("page", 1)
    limit = min(int(request.GET.get("limit", 6)), 50)

    places_qs = (
        Place.objects.annotate(
            avg_rating=Coalesce(Avg("reviews__rating"), Value(0.0)),
            review_count=Count("reviews"),
        )
        .order_by("-avg_rating", "-review_count", "-created_at")
    )

    paginator = Paginator(places_qs, limit)
    try:
        page_obj = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.page(1)

    results = []
    for place in page_obj:
        results.append({
            "id": place.id,
            "name": place.name,
            "location": place.location,
            "category": place.category,
            "description": place.description,
            "image_url": place.image_url,
            "average_rating": round(place.avg_rating, 1) if place.avg_rating else 0.0,
            "reviews_count": place.review_count,
            "created_at": place.created_at.isoformat(),
        })

    return JsonResponse({
        "places": results,
        "total": paginator.count,
        "page": page_obj.number,
        "num_pages": paginator.num_pages,
        "has_next": page_obj.has_next(),
    })


@require_http_methods(["GET"])
def api_recent_reviews(request):
    """
    GET /api/reviews/recent?page=1&limit=6
    ดึงรีวิวล่าสุด เรียงตาม created_at DESC พร้อมข้อมูลผู้ใช้และสถานที่
    """
    _ensure_sample_data()
    page = request.GET.get("page", 1)
    limit = min(int(request.GET.get("limit", 6)), 50)

    reviews_qs = (
        Review.objects.select_related("author", "place")
        .order_by("-created_at")
    )

    paginator = Paginator(reviews_qs, limit)
    try:
        page_obj = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.page(1)

    results = []
    for review in page_obj:
        results.append({
            "id": review.id,
            "rating": review.rating,
            "content": review.content,
            "image_url": review.image_url,
            "created_at": review.created_at.isoformat(),
            "author": {
                "id": review.author.id,
                "username": review.author.username,
            },
            "place": {
                "id": review.place.id,
                "name": review.place.name,
                "location": review.place.location,
                "category": review.place.category,
            },
        })

    return JsonResponse({
        "reviews": results,
        "total": paginator.count,
        "page": page_obj.number,
        "num_pages": paginator.num_pages,
        "has_next": page_obj.has_next(),
    })


@require_http_methods(["GET"])
def api_place_detail(request, place_id):
    """GET /api/places/<place_id>/ -> Place detail."""
    place = get_object_or_404(Place, pk=place_id)
    return JsonResponse({
        "id": place.id,
        "name": place.name,
        "location": place.location,
        "category": place.category,
        "description": place.description,
        "image_url": place.image_url,
        "average_rating": place.average_rating,
        "reviews_count": place.reviews_count,
        "created_at": place.created_at.isoformat(),
    })


@require_http_methods(["GET"])
def api_review_detail(request, review_id):
    """GET /api/reviews/<review_id>/ -> Review detail."""
    review = get_object_or_404(Review.objects.select_related("author", "place"), pk=review_id)
    return JsonResponse({
        "id": review.id,
        "rating": review.rating,
        "content": review.content,
        "image_url": review.image_url,
        "created_at": review.created_at.isoformat(),
        "author": {
            "id": review.author.id,
            "username": review.author.username,
        },
        "place": {
            "id": review.place.id,
            "name": review.place.name,
            "location": review.place.location,
            "category": review.place.category,
        },
    })
