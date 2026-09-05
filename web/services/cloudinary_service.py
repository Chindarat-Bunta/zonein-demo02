"""
Cloudinary Central Service for Zone In
Provides a unified interface for uploading, deleting, and optimizing images/media.
"""

import logging
import cloudinary
import cloudinary.uploader
import cloudinary.utils

logger = logging.getLogger(__name__)


def is_cloudinary_configured() -> bool:
    """
    Check if Cloudinary has been configured with valid credentials.
    """
    config = cloudinary.config()
    return bool(
        config.cloud_name
        and config.cloud_name != "zonein"
        and config.api_key
        and config.api_key != "demo_key"
        and config.api_secret
        and config.api_secret != "demo_secret"
    )


def upload_image(
    file,
    folder: str = "zonein/avatars",
    public_id: str = None,
    tags: list = None,
    transformation: list = None,
    resource_type: str = "image",
    **kwargs
) -> dict:
    """
    Upload an image or file to Cloudinary.

    :param file: File path, file-like object, bytes, or Django UploadedFile.
    :param folder: Target folder in Cloudinary (e.g. 'zonein/avatars', 'zonein/reviews').
    :param public_id: Optional custom public identifier for the asset.
    :param tags: Optional list of tags for categorization.
    :param transformation: Optional list of Cloudinary transformation dicts.
    :param resource_type: Resource type ('image', 'video', 'raw', 'auto').
    :return: dict containing upload results (success, url, public_id, etc.)
    """
    try:
        upload_options = {
            "folder": folder,
            "resource_type": resource_type,
            "overwrite": True,
            "unique_filename": True,
        }

        if public_id:
            upload_options["public_id"] = public_id

        if tags:
            upload_options["tags"] = tags

        if transformation:
            upload_options["transformation"] = transformation
        else:
            upload_options["transformation"] = [
                {"quality": "auto", "fetch_format": "auto"}
            ]

        upload_options.update(kwargs)

        response = cloudinary.uploader.upload(file, **upload_options)

        return {
            "success": True,
            "url": response.get("secure_url") or response.get("url"),
            "public_id": response.get("public_id"),
            "format": response.get("format"),
            "width": response.get("width"),
            "height": response.get("height"),
            "bytes": response.get("bytes"),
            "created_at": response.get("created_at"),
            "raw_response": response,
        }

    except Exception as e:
        logger.error(f"Failed to upload image to Cloudinary: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "url": None,
            "public_id": None,
        }


def delete_image(public_id: str, resource_type: str = "image", **kwargs) -> dict:
    """
    Delete an image or media asset from Cloudinary by its public_id.
    """
    if not public_id:
        return {"success": False, "error": "public_id is required"}

    try:
        response = cloudinary.uploader.destroy(
            public_id,
            resource_type=resource_type,
            **kwargs
        )
        result = response.get("result")
        is_ok = result in ("ok", "not found")

        return {
            "success": is_ok,
            "result": result,
            "raw_response": response,
        }

    except Exception as e:
        logger.error(f"Failed to delete image '{public_id}' from Cloudinary: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
        }


def get_optimized_url(
    public_id: str,
    width: int = None,
    height: int = None,
    crop: str = "fill",
    quality: str = "auto",
    fetch_format: str = "auto",
    secure: bool = True,
    **kwargs
) -> str:
    """
    Generate an optimized delivery URL for a Cloudinary asset with on-the-fly transformations.
    """
    if not public_id:
        return ""

    transformation = {
        "quality": quality,
        "fetch_format": fetch_format,
    }

    if width or height:
        transformation["crop"] = crop
        if width:
            transformation["width"] = width
        if height:
            transformation["height"] = height

    transformation.update(kwargs)

    url, _ = cloudinary.utils.cloudinary_url(
        public_id,
        transformation=transformation,
        secure=secure,
    )
    return url


def upload_multiple_images(
    files: list,
    folder: str = "zonein",
    **kwargs
) -> list:
    """
    Batch upload multiple image files to Cloudinary.
    """
    results = []
    for file in files:
        res = upload_image(file, folder=folder, **kwargs)
        results.append(res)
    return results
