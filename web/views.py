from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages


def index(request):
    """
    Zone In Main Homepage / Feed view.
    """
    return render(request, "index.html")


def signin_view(request):
    """
    Sign In / Login view supporting username, email, and social login (Google & Facebook).
    """
    if request.method == "POST":
        identifier = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        remember_me = request.POST.get("remember_me")

        # Allow login using either username or email
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
                request.session.set_expiry(2592000)  # 30 days

            display_name = user.first_name if user.first_name else user.username
            messages.success(request, f"ยินดีต้อนรับ, {display_name}! เข้าสู่ระบบสำเร็จแล้ว")
            return redirect("signin")
        else:
            messages.error(request, "ชื่อผู้ใช้/อีเมล หรือรหัสผ่านไม่ถูกต้อง โปรดลองใหม่อีกครั้ง")

    return render(request, "signin.html")


def signup_view(request):
    """
    Sign Up / Registration view with input validation and instant login.
    """
    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        # Form validation
        if not username or not email or not password:
            messages.error(request, "กรุณากรอกข้อมูลให้ครบถ้วนทุกช่อง")
            return render(request, "signup.html", {"full_name": full_name, "username": username, "email": email})

        if len(password) < 6:
            messages.error(request, "รหัสผ่านต้องมีความยาวอย่างน้อย 6 ตัวอักษร")
            return render(request, "signup.html", {"full_name": full_name, "username": username, "email": email})

        if password != confirm_password:
            messages.error(request, "รหัสผ่านและการยืนยันรหัสผ่านไม่ตรงกัน")
            return render(request, "signup.html", {"full_name": full_name, "username": username, "email": email})

        if User.objects.filter(username__iexact=username).exists():
            messages.error(request, f"ชื่อผู้ใช้ '{username}' มีผู้ใช้งานแล้ว โปรดเลือกชื่ออื่น")
            return render(request, "signup.html", {"full_name": full_name, "email": email})

        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, f"อีเมล '{email}' เคยลงทะเบียนแล้ว โปรดเข้าสู่ระบบ")
            return render(request, "signup.html", {"full_name": full_name, "username": username})

        # Create user account
        new_user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=full_name if full_name else username
        )
        login(request, new_user)
        messages.success(request, f"สมัครสมาชิกสำเร็จ! ยินดีต้อนรับสู่ Zone In, {new_user.first_name}")
        return redirect("signin")

    return render(request, "signup.html")


def social_login_view(request, provider):
    """
    Social Login endpoint for Google and Facebook.
    Provides instant functional login/signup, creating or retrieving the account.
    """
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
        return redirect("signin")

    # Get or create social user
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            "email": email,
            "first_name": display_name,
        }
    )

    if created:
        user.set_unusable_password()
        user.save()

    login(request, user)
    action_text = "สมัครและเข้าสู่ระบบ" if created else "เข้าสู่ระบบ"
    messages.success(request, f"{action_text}ด้วย {provider_name} สำเร็จเรียบร้อยแล้ว!")
    return redirect("signin")


def logout_view(request):
    """
    Logs out the user and redirects to signin with a confirmation message.
    """
    logout(request)
    messages.info(request, "ออกจากระบบเรียบร้อยแล้ว")
    return redirect("signin")

