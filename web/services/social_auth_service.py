"""
Social Authentication & OAuth 2.0 Integration Service (Google)
Compliant with Thailand Personal Data Protection Act (PDPA) consent guidelines.
"""

import logging
import secrets
import urllib.parse
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.text import slugify
import requests
from web.models import UserProfile

logger = logging.getLogger(__name__)

# Provider Configurations
PROVIDERS = {
    "google": {
        "name": "Google",
        "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "userinfo_url": "https://www.googleapis.com/oauth2/v3/userinfo",
        "scopes": "openid email profile",
        "client_id_setting": "GOOGLE_CLIENT_ID",
        "client_secret_setting": "GOOGLE_CLIENT_SECRET",
        "color": "#4285F4",
        "icon": "google",
    },
}


def is_provider_configured(provider: str) -> bool:
    """Check if the given social provider has valid client credentials configured."""
    prov = PROVIDERS.get(provider.lower())
    if not prov:
        return False
    client_id = getattr(settings, prov["client_id_setting"], "")
    client_secret = getattr(settings, prov["client_secret_setting"], "")
    return bool(
        client_id
        and client_secret
        and client_id not in ("your_google_client_id", "")
    )


def get_social_provider_config(provider: str) -> dict:
    """Return dictionary of provider settings and active status."""
    prov = PROVIDERS.get(provider.lower(), {})
    is_ready = is_provider_configured(provider)
    return {
        "provider": provider.lower(),
        "name": prov.get("name", provider.capitalize()),
        "color": prov.get("color", "#FF9D9D"),
        "is_configured": is_ready,
        "client_id": getattr(settings, prov.get("client_id_setting", ""), ""),
    }


def generate_oauth_state() -> str:
    """Generate a cryptographically secure state token to prevent CSRF in OAuth."""
    return secrets.token_urlsafe(32)


def get_authorization_url(provider: str, redirect_uri: str, state: str) -> str:
    """
    Construct the OAuth 2.0 authorization URL for Google.
    """
    prov = PROVIDERS.get(provider.lower())
    if not prov:
        raise ValueError(f"Unsupported social provider: {provider}")

    client_id = getattr(settings, prov["client_id_setting"], "")

    if provider.lower() == "google":
        params = {
            "client_id": client_id,
            "response_type": "code",
            "scope": prov["scopes"],
            "redirect_uri": redirect_uri,
            "state": state,
            "access_type": "online",
            "prompt": "select_account consent",
        }
        return f"{prov['auth_url']}?{urllib.parse.urlencode(params)}"

    return ""


def exchange_code_for_user_info(provider: str, code: str, redirect_uri: str) -> dict:
    """
    Exchange authorization code for access token and fetch user identity information.
    """
    prov = PROVIDERS.get(provider.lower())
    if not prov:
        return {"success": False, "error": f"ผู้ให้บริการ '{provider}' ไม่ถูกต้อง"}

    client_id = getattr(settings, prov["client_id_setting"], "")
    client_secret = getattr(settings, prov["client_secret_setting"], "")

    try:
        # 1. Exchange authorization code for access token
        if provider.lower() == "google":
            token_resp = requests.post(
                prov["token_url"],
                data={
                    "code": code,
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                },
                timeout=12,
            )
            token_data = token_resp.json()
            if "error" in token_data:
                logger.error("Google Token Exchange Error: %s", token_data)
                return {
                    "success": False,
                    "error": token_data.get("error_description", "การยืนยันรหัสเข้าสู่ระบบกับ Google ล้มเหลว"),
                }

            access_token = token_data.get("access_token")

            # 2. Fetch User Profile from Google UserInfo endpoint
            userinfo_resp = requests.get(
                prov["userinfo_url"],
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=12,
            )
            user_data = userinfo_resp.json()
            if "error" in user_data:
                return {"success": False, "error": "ไม่สามารถดึงข้อมูลโปรไฟล์จาก Google ได้"}

            return {
                "success": True,
                "provider": "google",
                "id": user_data.get("sub"),
                "email": user_data.get("email"),
                "name": user_data.get("name") or user_data.get("given_name", "Google User"),
                "picture": user_data.get("picture", ""),
                "raw": user_data,
            }

    except Exception as e:
        logger.error("OAuth Exchange Exception for %s: %s", provider, str(e), exc_info=True)
        return {"success": False, "error": f"เกิดข้อผิดพลาดในการเชื่อมต่อ: {str(e)}"}


def sync_social_user(provider: str, user_info: dict) -> tuple:
    """
    Find or create User and UserProfile in Neon PostgreSQL database.
    Updates avatar and display name accordingly.
    Returns (user, user_profile, created_boolean).
    """
    email = user_info.get("email", "").strip().lower()
    full_name = user_info.get("name", "").strip()
    picture_url = user_info.get("picture", "").strip()
    social_id = str(user_info.get("id", ""))

    # 1. Try to find user by email
    user = None
    created = False
    if email:
        user = User.objects.filter(email__iexact=email).first()

    # 2. If not found, create new user with username matching full_name (ชื่อ)
    if not user:
        clean_name = full_name.strip() if full_name else ""
        base_username = clean_name if clean_name else f"user_{social_id[:6]}"
        base_username = base_username[:30]
        username = base_username

        # Guarantee unique username in Neon DB
        counter = 1
        while User.objects.filter(username__iexact=username).exists():
            username = f"{base_username}_{counter}"
            counter += 1

        user = User.objects.create_user(
            username=username,
            email=email or f"{username}@{provider}.zonein.app",
            first_name=full_name or username,
        )
        user.set_unusable_password()
        user.save()
        created = True
    else:
        # Existing user: update name if blank
        if not user.first_name and full_name:
            user.first_name = full_name
            user.save(update_fields=["first_name"])

    # 3. Synchronize UserProfile (Neon DB)
    profile, _ = UserProfile.objects.get_or_create(user=user)

    if full_name:
        profile.nickname = full_name
    elif not profile.nickname:
        profile.nickname = user.first_name or user.username

    # Set avatar from social picture if provided
    if picture_url:
        profile.avatar_url = picture_url

    profile.save()

    return user, profile, created


def get_consent_disclosures(provider: str = "google") -> dict:
    """
    Returns standardized PDPA data collection notice & consent terms.
    """
    prov_name = PROVIDERS.get(provider.lower(), {}).get("name", provider.capitalize())
    return {
        "provider": provider.lower(),
        "provider_name": prov_name,
        "title": f"การขอความยินยอมและแจ้งการจัดเก็บข้อมูลส่วนบุคคล ({prov_name})",
        "intro": f"Zone In มีนโยบายเคารพความเป็นส่วนตัวของคุณ เพื่อความโปร่งใสตามพระราชบัญญัติคุ้มครองข้อมูลส่วนบุคคล (PDPA) ระบบจะขอเข้าถึงและจัดเก็บข้อมูลจากบัญชี {prov_name} ของคุณดังต่อไปนี้:",
        "collected_data": [
            {
                "label": "ชื่อและนามสกุล (Public Name)",
                "detail": f"ดึงจากชื่อบัญชี {prov_name} เพื่อใช้แสดงเป็นชื่อในโปรไฟล์, โพสต์ และรีวิวสถานที่",
                "icon": "👤",
                "required": True,
            },
            {
                "label": "ที่อยู่อีเมล (Email Address)",
                "detail": f"ดึงจากอีเมลหลักของ {prov_name} เพื่อใช้ระบุตัวตนบัญชี, ป้องกันการสวมสิทธิ์ และรับการแจ้งเตือนสำคัญ",
                "icon": "📧",
                "required": True,
            },
            {
                "label": "รูปภาพโปรไฟล์ (Profile Picture)",
                "detail": f"ดึงรูปภาพประจำตัวสาธารณะจาก {prov_name} มาใช้เป็น Avatar เริ่มต้นในระบบ Zone In (สามารถเปลี่ยนได้ภายหลัง)",
                "icon": "🖼️",
                "required": False,
            },
            {
                "label": "รหัสระบุตัวตนผู้ใช้ (Social Account Identifier)",
                "detail": f"รหัสเฉพาะ (ID) ของ {prov_name} เพื่อใช้เชื่อมต่อการเข้าสู่ระบบครั้งถัดไปได้อย่างรวดเร็วและปลอดภัย",
                "icon": "🆔",
                "required": True,
            },
        ],
        "excluded_data": [
            "รหัสผ่านบัญชี Google ของคุณ (ระบบไม่สามารถและจะไม่เข้าถึงรหัสผ่านใดๆ)",
            "รายชื่อเพื่อน, ข้อความแชทส่วนตัว, ประวัติการค้นหา หรือโพสต์ส่วนตัวบนบัญชี Google",
            "ระบบจะไม่มีการโพสต์สิ่งใดลงบนหน้าฟีดหรือบัญชีของคุณโดยเด็ดขาด",
        ],
        "purposes": [
            "เพื่อสร้างและยืนยันตัวตนบัญชีสมาชิก Zone In ผ่านระบบ Single Sign-On (SSO)",
            "เพื่อบันทึกสถานที่โปรด, แนะนำสถานที่ท่องเที่ยว, และเผยแพร่รีวิวของคุณ",
            "เพื่อส่งการแจ้งเตือนเมื่อมีผู้มากดไลก์ หรือแสดงความคิดเห็นบนรีวิวของคุณ",
        ],
        "retention_period": "ตลอดระยะเวลาที่คุณยังคงเป็นสมาชิก โดยคุณสามารถแก้ไขหรือขอลบบัญชีและข้อมูลทั้งหมดได้ตลอดเวลา",
        "user_rights": "คุณมีสิทธิ์ขอเข้าถึง, ขอรับสำเนา, ขอแก้ไข, หรือขอลบข้อมูลส่วนบุคคลของคุณได้ตามกฎหมาย PDPA ผ่านเมนูตั้งค่าโปรไฟล์",
    }
