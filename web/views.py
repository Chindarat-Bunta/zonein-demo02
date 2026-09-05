from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from .models import Product, Review


def _ensure_sample_data():
    """Ensure some initial demo products exist."""
    if Product.objects.count() == 0:
        p1 = Product.objects.create(
            name="ZoneIn Wireless Noise-Cancelling Headphones",
            description="Ultra-premium active noise-cancelling headphones with 40-hour battery life and spatial audio support.",
            price=299.00,
            image_url="https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&auto=format&fit=crop&q=60",
        )
        p2 = Product.objects.create(
            name="ZoneIn Ergonomic Mechanical Keyboard",
            description="Custom mechanical keyboard featuring hot-swappable tactile switches, gasket mount, and RGB lighting.",
            price=149.50,
            image_url="https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=800&auto=format&fit=crop&q=60",
        )
        p3 = Product.objects.create(
            name="ZoneIn Ultra-Wide Gaming Monitor 34\"",
            description="144Hz curved display with 1ms response time and HDR600 for immersive gaming and productivity.",
            price=499.99,
            image_url="https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=800&auto=format&fit=crop&q=60",
        )

        # Create demo users and initial reviews if none
        u1, _ = User.objects.get_or_create(username="alex_dev", defaults={"email": "alex@example.com"})
        u2, _ = User.objects.get_or_create(username="sarah_ux", defaults={"email": "sarah@example.com"})
        u3, _ = User.objects.get_or_create(username="john_doe", defaults={"email": "john@example.com"})

        Review.objects.get_or_create(
            user=u1,
            target=p1,
            defaults={"rating": 5, "comment": "Sound quality is phenomenal! The ANC completely blocks out train noises."},
        )
        Review.objects.get_or_create(
            user=u2,
            target=p1,
            defaults={"rating": 4, "comment": "Very comfortable for long working hours. Bass is slightly heavy but easily tuned."},
        )
        p1.update_rating_stats()

        Review.objects.get_or_create(
            user=u3,
            target=p2,
            defaults={"rating": 5, "comment": "Typing feel is buttery smooth. Best keyboard I have ever owned."},
        )
        p2.update_rating_stats()


def home_view(request):
    """Render the main interactive showcase page."""
    _ensure_sample_data()
    products = Product.objects.all().order_by("id")
    current_product = products.first()
    users = User.objects.all().order_by("id")[:5]

    return render(
        request,
        "web/index.html",
        {
            "products": products,
            "current_product": current_product,
            "demo_users": users,
            "user": request.user,
        },
    )


@require_http_methods(["GET"])
def products_api_view(request):
    """Return list of products."""
    products = Product.objects.all().order_by("id")
    data = [
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "price": float(p.price),
            "image_url": p.image_url,
            "average_rating": p.average_rating,
            "review_count": p.review_count,
        }
        for p in products
    ]
    return JsonResponse({"products": data})


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
