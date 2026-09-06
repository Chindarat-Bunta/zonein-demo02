import json
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import Client, TestCase
from django.urls import reverse

from web.models import (
    Comment,
    Place,
    PlaceImage,
    PlaceLike,
    Review,
    UserProfile,
    Wishlist,
)
from web.services.cloudinary_service import (
    delete_image,
    get_optimized_url,
    upload_image,
    upload_multiple_images,
)


class PlaceModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="password123"
        )
        self.place = Place.objects.create(
            author=self.user, name="สวนเบญจกิติ", address="กรุงเทพฯ"
        )

    def test_average_rating_and_reviews_count(self):
        """Average rating should compute correctly and reviews count match."""
        self.assertEqual(self.place.average_rating, 0.0)
        self.assertEqual(self.place.reviews_count, 0)

        Review.objects.create(
            place=self.place, user=self.user, rating=5, comment="ยอดเยี่ยม"
        )
        Review.objects.create(
            place=self.place, user=self.user, rating=3, comment="พอใช้"
        )

        self.assertEqual(self.place.reviews_count, 2)
        self.assertEqual(self.place.average_rating, 4.0)


class HomePageAPITests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(
            username="somchai", password="password123"
        )
        self.user2 = User.objects.create_user(username="ploy", password="password123")

        # Create 2 places
        self.place1 = Place.objects.create(
            author=self.user1, name="ดอยอินทนนท์", address="เชียงใหม่"
        )
        self.place2 = Place.objects.create(
            author=self.user2, name="หาดป่าตอง", address="ภูเก็ต"
        )

        # Create reviews with distinct ratings
        Review.objects.create(
            place=self.place1, user=self.user1, rating=5, comment="หนาวจับใจ"
        )
        Review.objects.create(
            place=self.place1, user=self.user2, rating=5, comment="วิวอลังการ"
        )
        Review.objects.create(
            place=self.place2, user=self.user1, rating=4, comment="หาดทรายสวย"
        )

    def test_home_page_renders_successfully(self):
        """Home page should return status code 200."""
        response = self.client.get(reverse("web:home"))
        self.assertEqual(response.status_code, 200)

    def test_api_popular_places_ordered_by_rating(self):
        """Popular places API should return places sorted by rating and review count."""
        response = self.client.get(reverse("web:api_popular_places") + "?limit=10")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("places", data)
        self.assertTrue(len(data["places"]) >= 2)

        # Place 1 (rating 5.0) should come before Place 2 (rating 4.0)
        first_place = data["places"][0]
        self.assertEqual(first_place["name"], "ดอยอินทนนท์")
        self.assertEqual(first_place["average_rating"], 5.0)
        self.assertEqual(first_place["reviews_count"], 2)

    def test_api_recent_reviews_ordered_by_date(self):
        """Recent reviews API should return reviews in reverse chronological order."""
        response = self.client.get(reverse("web:api_recent_reviews") + "?limit=10")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("reviews", data)
        self.assertTrue(len(data["reviews"]) >= 3)

        first_review = data["reviews"][0]
        self.assertIn("author", first_review)
        self.assertIn("place", first_review)
        self.assertIn("rating", first_review)
        self.assertIn("content", first_review)

    def test_api_place_detail(self):
        """Place detail API should return full info for a specific place."""
        response = self.client.get(
            reverse("web:api_place_detail", args=[self.place1.id])
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["name"], "ดอยอินทนนท์")
        self.assertEqual(data["average_rating"], 5.0)

    def test_api_add_comment(self):
        """Adding a comment to a review should succeed."""
        review = Review.objects.first()
        response = self.client.post(
            reverse("web:api_add_comment", args=[review.id]),
            data=json.dumps({"content": "สวยมากครับ!", "username": "somchai"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["comment"]["content"], "สวยมากครับ!")

    def test_api_edit_review(self):
        """Editing review content and rating should succeed."""
        review = Review.objects.first()
        response = self.client.post(
            reverse("web:api_edit_review", args=[review.id]),
            data=json.dumps({"content": "แก้ไขข้อความรีวิวใหม่", "rating": 4}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        review.refresh_from_db()
        self.assertEqual(review.content, "แก้ไขข้อความรีวิวใหม่")
        self.assertEqual(review.rating, 4)

    def test_api_delete_review(self):
        """Deleting a review should remove it from the database."""
        review = Review.objects.first()
        review_id = review.id
        response = self.client.post(reverse("web:api_delete_review", args=[review_id]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Review.objects.filter(id=review_id).exists())


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
        self.assertEqual(
            result["url"],
            "https://res.cloudinary.com/zonein/image/upload/v12345/sample.jpg",
        )
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
        mock_destroy.assert_called_once_with(
            "zonein/sample_image", resource_type="image"
        )

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


class ModelsSchemaTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="testuser1",
            email="testuser1@zonein.app",
            password="password123",
            first_name="สมชาย",
        )
        self.user2 = User.objects.create_user(
            username="testuser2",
            email="testuser2@zonein.app",
            password="password123",
            first_name="วิภาดา",
        )

    def test_user_profile_created_via_signal(self):
        """Test that UserProfile is automatically created when User is saved."""
        self.assertTrue(hasattr(self.user1, "profile"))
        profile = self.user1.profile
        profile.nickname = "พี่สมชาย"
        profile.bio = "ชอบเดินทางและดื่มกาแฟคั่วเข้ม"
        profile.avatar_url = (
            "https://res.cloudinary.com/aomzjdia/image/upload/v1/avatars/somchai.jpg"
        )
        profile.save()

        self.assertEqual(profile.get_display_name(), "พี่สมชาย")
        self.assertIn("avatars/somchai.jpg", profile.avatar_url)
        self.assertEqual(profile.bio, "ชอบเดินทางและดื่มกาแฟคั่วเข้ม")

    def test_place_creation_with_maps_coordinates(self):
        """Test Place creation with Google Maps coordinates, category and cover image."""
        place = Place.objects.create(
            author=self.user1,
            name="The Glasshouse Cafe & Co",
            category="cafe",
            description="คาเฟ่บรรยากาศอบอุ่นกลางสวน มีกาแฟ Specialty",
            address="123 ถนนสุขุมวิท กรุงเทพฯ",
            latitude=Decimal("13.7563310"),
            longitude=Decimal("100.5017650"),
            cover_image_url="https://res.cloudinary.com/aomzjdia/image/upload/v1/places/glasshouse.jpg",
        )

        self.assertEqual(place.slug, "the-glasshouse-cafe-co")
        self.assertEqual(place.average_rating, 0.0)
        self.assertEqual(place.review_count, 0)
        self.assertEqual(place.likes_count, 0)
        self.assertEqual(place.wishlist_count, 0)
        self.assertEqual(str(place), "The Glasshouse Cafe & Co (คาเฟ่ (Cafe))")

    def test_place_images_gallery(self):
        """Test adding multiple gallery images to a Place."""
        place = Place.objects.create(
            author=self.user1, name="Camping Hilltop", category="nature"
        )
        img1 = PlaceImage.objects.create(
            place=place,
            image_url="https://res.cloudinary.com/aomzjdia/image/upload/v1/places/camp1.jpg",
            caption="วิวหมอกยามเช้า",
        )
        img2 = PlaceImage.objects.create(
            place=place,
            image_url="https://res.cloudinary.com/aomzjdia/image/upload/v1/places/camp2.jpg",
            caption="ลานกางเต็นท์ริมน้ำ",
        )

        self.assertEqual(place.images.count(), 2)
        self.assertEqual(img1.caption, "วิวหมอกยามเช้า")

    def test_review_and_average_rating(self):
        """Test rating and review calculations on a Place."""
        place = Place.objects.create(
            author=self.user1, name="Artisan Bakery", category="cafe"
        )

        Review.objects.create(
            place=place, user=self.user1, rating=5, comment="ขนมอบสดใหม่ อร่อยมาก!"
        )

        Review.objects.create(
            place=place, user=self.user2, rating=4, comment="กาแฟรสชาติดี บรรยากาศเงียบสงบ"
        )

        self.assertEqual(place.review_count, 2)
        self.assertEqual(place.average_rating, 4.5)

    def test_review_rating_validation(self):
        """Test that review rating must be between 1 and 5 stars."""
        place = Place.objects.create(
            author=self.user1, name="Test Place", category="cafe"
        )
        invalid_review = Review(
            place=place, user=self.user1, rating=6, comment="Invalid rating test"
        )
        with self.assertRaises(ValidationError):
            invalid_review.full_clean()

    def test_wishlist_unique_constraint(self):
        """Test that a user cannot add the same place to wishlist twice."""
        place = Place.objects.create(
            author=self.user1, name="Secret Beach Villa", category="hotel"
        )

        Wishlist.objects.create(user=self.user1, place=place)
        self.assertEqual(place.wishlist_count, 1)

        with self.assertRaises(IntegrityError):
            Wishlist.objects.create(user=self.user1, place=place)

    def test_placelike_unique_constraint(self):
        """Test that a user cannot like the same place twice."""
        place = Place.objects.create(
            author=self.user1, name="Sunset Viewpoint", category="travel"
        )

        PlaceLike.objects.create(user=self.user2, place=place)
        self.assertEqual(place.likes_count, 1)

        with self.assertRaises(IntegrityError):
            PlaceLike.objects.create(user=self.user2, place=place)


class WishlistTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.place = Place.objects.create(
            name="Nana Coffee Roasters",
            slug="nana-coffee-roasters",
            category="cafe",
            address="อารีย์ ซอย 4",
            description="คาเฟ่สวย กาแฟดี",
        )

    def test_wishlist_page_renders_empty_state(self):
        response = self.client.get(reverse("web:wishlist"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "รายการสถานที่โปรด (My Wishlist)")
        self.assertContains(response, "ยังไม่มีสถานที่ในรายการโปรด")

    def test_api_wishlist_toggle_add_and_remove(self):
        response = self.client.post(
            reverse("web:api_wishlist_toggle"),
            data=json.dumps({"place_id": self.place.id}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["action"], "added")
        self.assertTrue(data["is_wishlisted"])
        self.assertEqual(data["total_count"], 1)

        # 2. Remove from wishlist
        response2 = self.client.post(
            reverse("web:api_wishlist_toggle"),
            data=json.dumps({"place_id": self.place.id}),
            content_type="application/json",
        )
        self.assertEqual(response2.status_code, 200)
        data2 = response2.json()
        self.assertEqual(data2["status"], "success")
        self.assertEqual(data2["action"], "removed")
        self.assertFalse(data2["is_wishlisted"])
        self.assertEqual(data2["total_count"], 0)
