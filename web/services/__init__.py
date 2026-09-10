"""
Services package for web application.
"""

from .cloudinary_service import (
    upload_image,
    delete_image,
    get_optimized_url,
    upload_multiple_images,
    is_cloudinary_configured,
)
from .social_auth_service import (
    is_provider_configured,
    get_social_provider_config,
    generate_oauth_state,
    get_authorization_url,
    exchange_code_for_user_info,
    sync_social_user,
    get_consent_disclosures,
)

__all__ = [
    "upload_image",
    "delete_image",
    "get_optimized_url",
    "upload_multiple_images",
    "is_cloudinary_configured",
    "is_provider_configured",
    "get_social_provider_config",
    "generate_oauth_state",
    "get_authorization_url",
    "exchange_code_for_user_info",
    "sync_social_user",
    "get_consent_disclosures",
]

