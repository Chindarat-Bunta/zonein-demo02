from django.shortcuts import render


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
