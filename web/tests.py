from unittest.mock import patch, MagicMock
from django.test import TestCase
from web.services.cloudinary_service import (
    upload_image,
    delete_image,
    get_optimized_url,
    upload_multiple_images,
    is_cloudinary_configured,
)


class CloudinaryServiceTests(TestCase):
    """
    Test suite for central Cloudinary upload service.
    """

    @patch("cloudinary.uploader.upload")
    def test_upload_image_success(self, mock_upload):
        mock_upload.return_value = {
            "secure_url": "https://res.cloudinary.com/zonein/image/upload/v12345/sample.jpg",
            "public_id": "zonein/sample",
            "format": "jpg",
            "width": 800,
            "height": 600,
            "bytes": 102400,
            "created_at": "2026-09-05T12:00:00Z",
        }

        fake_file = b"mock image content"
        result = upload_image(fake_file, folder="zonein/reviews")

        self.assertTrue(result["success"])
        self.assertEqual(result["url"], "https://res.cloudinary.com/zonein/image/upload/v12345/sample.jpg")
        self.assertEqual(result["public_id"], "zonein/sample")
        self.assertEqual(result["format"], "jpg")
        mock_upload.assert_called_once()

    @patch("cloudinary.uploader.upload")
    def test_upload_image_failure_handled(self, mock_upload):
        mock_upload.side_effect = Exception("Cloudinary connection failed")

        result = upload_image("invalid_path.jpg")

        self.assertFalse(result["success"])
        self.assertIn("Cloudinary connection failed", result["error"])
        self.assertIsNone(result["url"])

    @patch("cloudinary.uploader.destroy")
    def test_delete_image_success(self, mock_destroy):
        mock_destroy.return_value = {"result": "ok"}

        result = delete_image("zonein/sample_image")

        self.assertTrue(result["success"])
        self.assertEqual(result["result"], "ok")
        mock_destroy.assert_called_once_with("zonein/sample_image", resource_type="image")

    def test_delete_image_empty_id(self):
        result = delete_image("")
        self.assertFalse(result["success"])
        self.assertIn("public_id is required", result["error"])

    def test_get_optimized_url(self):
        url = get_optimized_url("zonein/cafe_1", width=600, height=400, crop="fill")
        self.assertIn("zonein/cafe_1", url)
        self.assertIn("w_600", url)
        self.assertIn("h_400", url)
        self.assertIn("c_fill", url)

    def test_get_optimized_url_empty_id(self):
        url = get_optimized_url("")
        self.assertEqual(url, "")

    @patch("web.services.cloudinary_service.upload_image")
    def test_upload_multiple_images(self, mock_upload):
        mock_upload.side_effect = [
            {"success": True, "url": "https://res.cloudinary.com/zonein/img1.jpg"},
            {"success": True, "url": "https://res.cloudinary.com/zonein/img2.jpg"},
        ]

        files = [b"file1", b"file2"]
        results = upload_multiple_images(files, folder="zonein/gallery")

        self.assertEqual(len(results), 2)
        self.assertTrue(results[0]["success"])
        self.assertTrue(results[1]["success"])
        self.assertEqual(mock_upload.call_count, 2)
