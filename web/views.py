from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from .models import TravelPost


def _ensure_sample_data():
    """Ensure sample traveler place recommendation posts exist."""
    if TravelPost.objects.count() == 0:
        u1, _ = User.objects.get_or_create(username="alex_traveler", defaults={"email": "alex@example.com"})
        u2, _ = User.objects.get_or_create(username="sarah_backpacker", defaults={"email": "sarah@example.com"})
        u3, _ = User.objects.get_or_create(username="john_camper", defaults={"email": "john@example.com"})

        # Post 1 by Alex
        p1 = TravelPost.objects.create(
            author=u1,
            place_name="สวนป่าเบญจกิติ (Benchakitti Forest Park)",
            category="ธรรมชาติ & สวนสาธารณะ",
            location="คลองเตย กรุงเทพมหานคร",
            rating=5,
            content="สวนสาธารณะเปิดใหม่ใจกลางกรุง สวยอลังการมาก! มี Skywalk ลอยฟ้ายาวกว่า 1.6 กม. ให้เดินรับลมชมวิวบึงน้ำและตึกสูง พระอาทิตย์ตกดินแสงสวยสุดๆ @sarah_backpacker @john_camper วันหยุดนี้ต้องมาถ่ายรูปด้วยกันนะ!",
            image_url="https://images.unsplash.com/photo-1596422846543-75c6fc197f07?w=1000&auto=format&fit=crop&q=80",
        )
        p1.tagged_users.add(u2, u3)

        # Post 2 by Sarah
        p2 = TravelPost.objects.create(
            author=u2,
            place_name="Riva Floating Cafe คาเฟ่แพริมน้ำ",
            category="คาเฟ่ริมน้ำ & ของกิน",
            location="อ.สามพราน จ.นครปฐม",
            rating=4,
            content="แวะมาพักผ่อนจิบกาแฟริมแม่น้ำท่าจีน นั่งห้อยขาชิลล์ๆ ลมพัดเย็นสบาย ขนมเค้กมะพร้าวอ่อนอร่อยมาก กาแฟหอม แนะนำให้มาช่วงบ่ายแก่ๆ แดดไม่ร้อนเลย @alex_traveler ลองแวะมาดู!",
            image_url="https://images.unsplash.com/photo-1554118811-1e0d58224f24?w=1000&auto=format&fit=crop&q=80",
        )
        p2.tagged_users.add(u1)

        # Post 3 by John
        p3 = TravelPost.objects.create(
            author=u3,
            place_name="จุดชมวิวผาเดียวดาย & ลานกางเต็นท์ลำตะคอง",
            category="แคมป์ปิ้ง & ภูเขา",
            location="อุทยานแห่งชาติเขาใหญ่ จ.นครราชสีมา",
            rating=5,
            content="ทริปหนีฝุ่นมากอดทะเลหมอกบนเขาใหญ่ อากาศตอนเช้า 18 องศา ฟินมาก! ลานกางเต็นท์ติดริมน้ำ นั่งจิบคราฟต์ช็อกโกแลตอุ่นๆ ส่องสัตว์ป่าและดูดาวเต็มท้องฟ้า ประทับใจ 5 ดาวเต็ม!",
            image_url="https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=1000&auto=format&fit=crop&q=80",
        )
        p3.tagged_users.add(u1, u2)


def home_view(request):
    """Render the traveler place recommendations feed UI."""
    _ensure_sample_data()
    posts = TravelPost.objects.select_related("author").prefetch_related("tagged_users").order_by("-created_at")
    users = User.objects.all().order_by("id")[:6]

    return render(
        request,
        "web/index.html",
        {
            "posts": posts,
            "demo_users": users,
            "user": request.user,
        },
    )


@require_http_methods(["POST", "GET"])
def demo_switch_user_view(request):
    """Utility endpoint to quickly switch demo traveler users for testing in browser."""
    username = request.POST.get("username") or request.GET.get("username")
    action = request.POST.get("action") or request.GET.get("action")

    if action == "logout":
        logout(request)
        return redirect("web:home")

    if username:
        user, _ = User.objects.get_or_create(username=username, defaults={"email": f"{username}@example.com"})
        login(request, user)
        return redirect("web:home")

    return redirect("web:home")
