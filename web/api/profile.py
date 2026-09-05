from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from web.models import UserProfile
from .views import parse_json_body


@csrf_exempt
def profile_detail_update(request):
    """
    Endpoint: /api/profile/
    - GET: Retrieve current user's profile information
    - POST: Update user profile (nickname, bio, avatar_url)
    """
    user = request.user if request.user.is_authenticated else None
    if not user:
        user, _ = User.objects.get_or_create(
            username="zonein_user",
            defaults={"first_name": "Zone In User", "email": "user@zonein.app"}
        )

    profile, _ = UserProfile.objects.get_or_create(user=user)

    if request.method == "GET":
        return JsonResponse({
            "success": True,
            "profile": {
                "id": profile.id,
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "nickname": profile.nickname,
                "display_name": profile.get_display_name(),
                "avatar_url": profile.avatar_url,
                "bio": profile.bio,
                "created_at": profile.created_at.isoformat(),
            }
        })

    elif request.method == "POST":
        payload = parse_json_body(request)
        if payload is None:
            payload = request.POST.dict()

        nickname = payload.get("nickname")
        bio = payload.get("bio")
        avatar_url = payload.get("avatar_url")
        avatar_public_id = payload.get("avatar_public_id")

        if nickname is not None:
            profile.nickname = nickname.strip()
        if bio is not None:
            profile.bio = bio.strip()
        if avatar_url is not None:
            profile.avatar_url = avatar_url.strip()
        if avatar_public_id is not None:
            profile.avatar_public_id = avatar_public_id.strip()

        profile.save()

        return JsonResponse({
            "success": True,
            "message": "อัปเดตข้อมูลโปรไฟล์เรียบร้อยแล้ว",
            "profile": {
                "id": profile.id,
                "username": user.username,
                "nickname": profile.nickname,
                "display_name": profile.get_display_name(),
                "avatar_url": profile.avatar_url,
                "bio": profile.bio,
                "updated_at": profile.updated_at.isoformat(),
            }
        })

    return JsonResponse({"success": False, "error": f"Method {request.method} not allowed"}, status=405)
