from unittest.mock import patch
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from web.models import UserProfile
from web.services.cloudinary_service import (
    upload_image,
    delete_image,
    get_optimized_url,
    upload_multiple_images,
)


class ProfileSettingsTests(TestCase):
    """
    Tests for Profile Settings screen, Popup modal, and Cloudinary upload.
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@zonein.app",
            password="password123",
            first_name="สมชาย"
        )
        self.profile = UserProfile.objects.get(user=self.user)

    def test_profile_settings_view_get(self):
        response = self.client.get("/profile/settings/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profile_settings.html")
        self.assertContains(response, "แก้ไขข้อมูลส่วนตัว")
        self.assertContains(response, "ชื่อเล่น / ชื่อที่แสดง")
        self.assertContains(response, "ข้อความ Bio แนะนำตัว")

    @patch("web.services.cloudinary_service.cloudinary.uploader.upload")
    def test_profile_settings_post_with_avatar(self, mock_upload):
        mock_upload.return_value = {
            "secure_url": "https://res.cloudinary.com/zonein/image/upload/v123/avatar.jpg",
            "public_id": "zonein/avatars/avatar_123",
            "format": "jpg",
            "width": 400,
            "height": 400,
        }

        self.client.force_login(self.user)
        test_avatar = SimpleUploadedFile("avatar.jpg", b"mock image bytes", content_type="image/jpeg")

        response = self.client.post("/profile/settings/", {
            "nickname": "พี่สมชาย สายคาเฟ่",
            "username": "somchai_zonein",
            "bio": "ชอบเดินทางค้นหาคาเฟ่ลับ ถ่ายรูปวิวธรรมชาติ",
            "avatar": test_avatar,
        })

        self.assertEqual(response.status_code, 302)
        
        # Verify in database
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.nickname, "พี่สมชาย สายคาเฟ่")
        self.assertEqual(self.profile.bio, "ชอบเดินทางค้นหาคาเฟ่ลับ ถ่ายรูปวิวธรรมชาติ")
        self.assertEqual(self.profile.avatar_url, "https://res.cloudinary.com/zonein/image/upload/v123/avatar.jpg")
        self.assertEqual(self.profile.avatar_public_id, "zonein/avatars/avatar_123")
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "somchai_zonein")

    @patch("web.services.cloudinary_service.cloudinary.uploader.upload")
    def test_update_profile_api(self, mock_upload):
        mock_upload.return_value = {
            "secure_url": "https://res.cloudinary.com/zonein/image/upload/v123/api_avatar.jpg",
            "public_id": "zonein/avatars/api_avatar",
            "format": "png",
        }

        self.client.force_login(self.user)
        test_avatar = SimpleUploadedFile("avatar.png", b"mock bytes", content_type="image/png")

        response = self.client.post("/api/profile/update/", {
            "nickname": "นกน้อยพาเที่ยว",
            "username": "noknoi_trip",
            "bio": "แชร์พิกัดแคมป์ปิ้งวิวสวย",
            "avatar": test_avatar,
        })

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["nickname"], "นกน้อยพาเที่ยว")
        self.assertEqual(data["avatar_url"], "https://res.cloudinary.com/zonein/image/upload/v123/api_avatar.jpg")


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
        }

        fake_file = b"mock image content"
        result = upload_image(fake_file, folder="zonein/avatars")

        self.assertTrue(result["success"])
        self.assertEqual(result["url"], "https://res.cloudinary.com/zonein/image/upload/v12345/sample.jpg")
        self.assertEqual(result["public_id"], "zonein/sample")

    @patch("cloudinary.uploader.destroy")
    def test_delete_image_success(self, mock_destroy):
        mock_destroy.return_value = {"result": "ok"}
        result = delete_image("zonein/avatars/sample")
        self.assertTrue(result["success"])

    def test_get_optimized_url(self):
        url = get_optimized_url("zonein/avatars/user1", width=300, height=300, crop="auto", gravity="auto")
        self.assertIn("zonein/avatars/user1", url)
        self.assertIn("w_300", url)
        self.assertIn("c_auto", url)
