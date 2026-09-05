import logging
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from .models import UserProfile
from .services import upload_image

logger = logging.getLogger(__name__)


def profile_settings_view(request):
    """
    Profile settings screen and popup for editing user information:
    - Profile picture (Uploads to Cloudinary)
    - Username & Nickname / Display Name
    - Bio description
    """
    user = request.user

    # Get or create active user/profile for demo or authenticated user
    if user.is_authenticated:
        profile, _ = UserProfile.objects.get_or_create(user=user)
        username = user.username
        nickname = profile.nickname or user.first_name or user.username
        bio = profile.bio
        avatar_url = profile.avatar_url
    else:
        # Fallback / demo profile for previewing without requiring login
        demo_user, _ = User.objects.get_or_create(
            username="zonein_user",
            defaults={"first_name": "คุณภัทรพล วงศ์สว่าง", "email": "patraphon.w@zonein.app"}
        )
        profile, _ = UserProfile.objects.get_or_create(user=demo_user)
        username = demo_user.username
        nickname = profile.nickname or demo_user.first_name
        bio = profile.bio or "✨ ผู้หลงใหลในการเดินทางและค้นหาคาเฟ่ลับ | สมาชิก Zone In"
        avatar_url = profile.avatar_url

    if request.method == "POST":
        new_nickname = request.POST.get("nickname", "").strip()
        new_username = request.POST.get("username", "").strip()
        new_bio = request.POST.get("bio", "").strip()
        avatar_file = request.FILES.get("avatar")

        upload_success = True
        new_avatar_url = avatar_url

        # 1. Handle profile picture upload via Cloudinary service
        if avatar_file:
            upload_res = upload_image(avatar_file, folder="zonein/avatars")
            if upload_res.get("success"):
                new_avatar_url = upload_res.get("url")
                profile.avatar_url = new_avatar_url
                profile.avatar_public_id = upload_res.get("public_id", "")
            else:
                upload_success = False
                messages.error(request, f"อัปโหลดรูปภาพไม่สำเร็จ: {upload_res.get('error')}")

        # 2. Update nickname & bio
        profile.nickname = new_nickname
        profile.bio = new_bio
        profile.save()

        # 3. Update username if provided and changed
        target_user = user if user.is_authenticated else demo_user
        if new_username and new_username != target_user.username:
            if not User.objects.filter(username__iexact=new_username).exclude(id=target_user.id).exists():
                target_user.username = new_username
                target_user.save()
            else:
                messages.error(request, f"ชื่อผู้ใช้ '{new_username}' มีผู้อื่นใช้งานแล้ว")

        if upload_success:
            messages.success(request, "บันทึกและอัปเดตข้อมูลส่วนตัวเรียบร้อยแล้ว!")

        return redirect("profile_settings")

    context = {
        "username": username,
        "nickname": nickname,
        "bio": bio,
        "avatar_url": avatar_url,
    }
    return render(request, "profile_settings.html", context)


def update_profile_api(request):
    """
    AJAX endpoint for popup modal submission with real-time feedback.
    """
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "POST method required"}, status=405)

    user = request.user
    target_user = user if user.is_authenticated else User.objects.filter(username="zonein_user").first()
    if not target_user:
        target_user, _ = User.objects.get_or_create(username="zonein_user", defaults={"first_name": "User"})

    profile, _ = UserProfile.objects.get_or_create(user=target_user)

    new_nickname = request.POST.get("nickname", "").strip()
    new_username = request.POST.get("username", "").strip()
    new_bio = request.POST.get("bio", "").strip()
    avatar_file = request.FILES.get("avatar")

    avatar_url = profile.avatar_url

    if avatar_file:
        upload_res = upload_image(avatar_file, folder="zonein/avatars")
        if upload_res.get("success"):
            avatar_url = upload_res.get("url")
            profile.avatar_url = avatar_url
            profile.avatar_public_id = upload_res.get("public_id", "")
        else:
            return JsonResponse({"success": False, "error": f"อัปโหลดรูปภาพล้มเหลว: {upload_res.get('error')}"})

    profile.nickname = new_nickname
    profile.bio = new_bio
    profile.save()

    if new_username and new_username != target_user.username:
        if not User.objects.filter(username__iexact=new_username).exclude(id=target_user.id).exists():
            target_user.username = new_username
            target_user.save()
        else:
            return JsonResponse({"success": False, "error": f"ชื่อผู้ใช้ '{new_username}' ถูกใช้งานแล้ว"})

    return JsonResponse({
        "success": True,
        "message": "อัปเดตข้อมูลส่วนตัวสำเร็จ!",
        "nickname": profile.get_display_name(),
        "username": target_user.username,
        "bio": profile.bio,
        "avatar_url": profile.avatar_url,
    })
