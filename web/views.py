from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from .models import Place, Review


def _ensure_sample_data():
    """Ensure sample place recommendation posts exist."""
    if Place.objects.count() == 0:
        p1 = Place.objects.create(
            name="สวนป่าเบญจกิติ (Benchakitti Forest Park)",
            category="สวนสาธารณะ & พื้นที่สีเขียว",
            location="เขตคลองเตย กรุงเทพมหานคร",
            description="สวนสาธารณะใจกลางกรุงขนาดใหญ่ มี Skywalk ทอดยาวรอบบึงน้ำและพื้นที่ป่าชุ่มน้ำ เหมาะสำหรับเดินเล่น วิ่งออกกำลังกาย ปั่นจักรยาน ชมนก และถ่ายรูปวิวเมืองยามเย็น",
            image_url="https://images.unsplash.com/photo-1596422846543-75c6fc197f07?w=800&auto=format&fit=crop&q=60",
        )
        p2 = Place.objects.create(
            name="Riva Floating Cafe (คาเฟ่แพริมน้ำ)",
            category="คาเฟ่ & จุดเช็คอินถ่ายรูป",
            location="อ.สามพราน จ.นครปฐม",
            description="คาเฟ่แพริมแม่น้ำท่าจีนบรรยากาศสุดชิลล์ นั่งห้อยขาริมน้ำ จิบกาแฟสด ทานเบเกอรี่โฮมเมด ลมพัดเย็นสบาย เหมาะกับการพักผ่อนช่วงวันหยุดสุดสัปดาห์",
            image_url="https://images.unsplash.com/photo-1554118811-1e0d58224f24?w=800&auto=format&fit=crop&q=60",
        )
        p3 = Place.objects.create(
            name="จุดชมวิวผาเดียวดาย & ลานกางเต็นท์ลำตะคอง",
            category="ธรรมชาติ & แคมป์ปิ้ง",
            location="อุทยานแห่งชาติเขาใหญ่ จ.นครราชสีมา",
            description="จุดชมวิวหน้าผาสูงชมทะเลหมอกและทิวเขาเขียวขจี อากาศเย็นสบายตลอดปี พร้อมลานกางเต็นท์ริมธารน้ำใส ดูดาวตอนกลางคืนและส่องสัตว์ป่า",
            image_url="https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=800&auto=format&fit=crop&q=60",
        )

        u1, _ = User.objects.get_or_create(username="alex_dev", defaults={"email": "alex@example.com"})
        u2, _ = User.objects.get_or_create(username="sarah_ux", defaults={"email": "sarah@example.com"})
        u3, _ = User.objects.get_or_create(username="john_doe", defaults={"email": "john@example.com"})

        r1, _ = Review.objects.get_or_create(
            user=u1,
            target=p1,
            defaults={"rating": 5, "comment": "บรรยากาศดีมาก ลมพัดสบายช่วงเย็น แนะนำให้มาถ่ายรูปบนสกายวอล์ก @sarah_ux วันหยุดนี้ไปกัน!"},
        )
        r1.tagged_users.add(u2)

        Review.objects.get_or_create(
            user=u2,
            target=p1,
            defaults={"rating": 4, "comment": "ต้นไม้ร่มรื่น วิวตึกตัดกับธรรมชาติสวยมาก แนะนำให้พกน้ำดื่มมาด้วย"},
        )
        p1.update_rating_stats()

        Review.objects.get_or_create(
            user=u3,
            target=p2,
            defaults={"rating": 5, "comment": "ขนมเค้กอร่อย กาแฟหอม นั่งห้อยขาริมน้ำฟินสุดๆ"},
        )
        p2.update_rating_stats()


def home_view(request):
    """Render the main place recommendation showcase UI page."""
    _ensure_sample_data()
    places = Place.objects.all().order_by("id")
    current_place = places.first()
    users = User.objects.all().order_by("id")[:5]

    return render(
        request,
        "web/index.html",
        {
            "places": places,
            "current_place": current_place,
            "demo_users": users,
            "user": request.user,
        },
    )


@require_http_methods(["GET"])
def places_api_view(request):
    """Return list of places."""
    places = Place.objects.all().order_by("id")
    data = [
        {
            "id": p.id,
            "name": p.name,
            "category": p.category,
            "location": p.location,
            "description": p.description,
            "image_url": p.image_url,
            "average_rating": p.average_rating,
            "review_count": p.review_count,
        }
        for p in places
    ]
    return JsonResponse({"places": data, "products": data})


@require_http_methods(["POST", "GET"])
def demo_switch_user_view(request):
    """Utility endpoint to quickly switch demo users for testing in browser."""
    username = request.POST.get("username") or request.GET.get("username")
    action = request.POST.get("action") or request.GET.get("action")

    if action == "logout":
        logout(request)
        if request.headers.get("Accept") == "application/json" or request.GET.get("format") == "json":
            return JsonResponse({"success": True, "logged_in": False})
        return redirect("web:home")

    if username:
        user, _ = User.objects.get_or_create(username=username, defaults={"email": f"{username}@example.com"})
        login(request, user)
        if request.headers.get("Accept") == "application/json" or request.GET.get("format") == "json":
            return JsonResponse({"success": True, "username": user.username, "id": user.id})
        return redirect("web:home")

    return redirect("web:home")
