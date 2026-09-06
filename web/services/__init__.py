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

__all__ = [
    "upload_image",
    "delete_image",
    "get_optimized_url",
    "upload_multiple_images",
    "is_cloudinary_configured",
]
