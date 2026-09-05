from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from .models import TravelPost


def _ensure_sample_data():
    """Ensure sample travel place recommendation posts and authors exist."""
    if TravelPost.objects.count() == 0:
        main_user, _ = User.objects.get_or_create(username="traveler", defaults={"email": "traveler@example.com"})
        user_somchai, _ = User.objects.get_or_create(username="somchai_explorer", defaults={"email": "somchai@example.com"})
        user_ploy, _ = User.objects.get_or_create(username="ploy_wanderer", defaults={"email": "ploy@example.com"})

        TravelPost.objects.create(
            author=user_somchai,
            place_name="สวนป่าเบญจกิติ (Benchakitti Forest Park)",
            category="ธรรมชาติ & สวนสาธารณะ",
            location="คลองเตย กรุงเทพมหานคร",
            rating=5,
            content="สวนสาธารณะเปิดใหม่ใจกลางกรุง สวยอลังการมาก! มี Skywalk ลอยฟ้ายาวกว่า 1.6 กม. ให้เดินรับลมชมวิวบึงน้ำและตึกสูง พระอาทิตย์ตกดินแสงสวยสุดๆ เหมาะแก่การมาวิ่งออกกำลังกายและถ่ายรูป",
            image_url="https://images.unsplash.com/photo-1596422846543-75c6fc197f07?w=1000&auto=format&fit=crop&q=80",
            likes_count=12,
            comments_count=2,
        )

        TravelPost.objects.create(
            author=user_ploy,
            place_name="Riva Floating Cafe คาเฟ่แพริมน้ำ",
            category="คาเฟ่ริมน้ำ & ของกิน",
            location="อ.สามพราน จ.นครปฐม",
            rating=4,
            content="แวะมาพักผ่อนจิบกาแฟริมแม่น้ำท่าจีน นั่งห้อยขาชิลล์ๆ ลมพัดเย็นสบาย ขนมเค้กมะพร้าวอ่อนอร่อยมาก กาแฟหอม แนะนำให้มาช่วงบ่ายแก่ๆ แดดไม่ร้อน บรรยากาศสงบ",
            image_url="https://images.unsplash.com/photo-1554118811-1e0d58224f24?w=1000&auto=format&fit=crop&q=80",
            likes_count=8,
            comments_count=1,
        )

        TravelPost.objects.create(
            author=main_user,
            place_name="จุดชมวิวผาเดียวดาย & ลานกางเต็นท์ลำตะคอง",
            category="แคมป์ปิ้ง & ภูเขา",
            location="อุทยานแห่งชาติเขาใหญ่ จ.นครราชสีมา",
            rating=5,
            content="ทริปหนีฝุ่นมากอดทะเลหมอกบนเขาใหญ่ อากาศตอนเช้า 18 องศา ฟินมาก! ลานกางเต็นท์ติดริมน้ำ นั่งจิบคราฟต์ช็อกโกแลตอุ่นๆ ส่องสัตว์ป่าและดูดาวเต็มท้องฟ้า ประทับใจ 5 ดาวเต็ม!",
            image_url="https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=1000&auto=format&fit=crop&q=80",
            likes_count=19,
            comments_count=3,
        )


def home_view(request):
    """Render the traveler place recommendations feed UI."""
    _ensure_sample_data()
    posts = TravelPost.objects.select_related("author").order_by("-created_at")

    return render(
        request,
        "web/index.html",
        {
            "posts": posts,
            "user": request.user,
        },
    )

