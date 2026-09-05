from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from decimal import Decimal
from web.models import UserProfile, Place, PlaceImage, Review, Wishlist, PlaceLike


class ModelsSchemaTests(TestCase):
    """
    Unit tests for Neon PostgreSQL schema:
    - UserProfile (User info, avatar, bio)
    - Place (Place/post, coordinates, category, Cloudinary cover)
    - PlaceImage (Place gallery image)
    - Review (1-5 star ratings, reviews)
    - Wishlist (Unique save/bookmark)
    - PlaceLike (Unique likes)
    """

    def setUp(self):
        self.user1 = User.objects.create_user(
            username="testuser1",
            email="testuser1@zonein.app",
            password="password123",
            first_name="สมชาย"
        )
        self.user2 = User.objects.create_user(
            username="testuser2",
            email="testuser2@zonein.app",
            password="password123",
            first_name="วิภาดา"
        )

    def test_user_profile_created_via_signal(self):
        """Test that UserProfile is automatically created when User is saved."""
        self.assertTrue(hasattr(self.user1, "profile"))
        profile = self.user1.profile
        profile.nickname = "พี่สมชาย"
        profile.bio = "ชอบเดินทางและดื่มกาแฟคั่วเข้ม"
        profile.avatar_url = "https://res.cloudinary.com/aomzjdia/image/upload/v1/avatars/somchai.jpg"
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
            cover_image_url="https://res.cloudinary.com/aomzjdia/image/upload/v1/places/glasshouse.jpg"
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
            author=self.user1,
            name="Camping Hilltop",
            category="nature"
        )
        img1 = PlaceImage.objects.create(
            place=place,
            image_url="https://res.cloudinary.com/aomzjdia/image/upload/v1/places/camp1.jpg",
            caption="วิวหมอกยามเช้า"
        )
        img2 = PlaceImage.objects.create(
            place=place,
            image_url="https://res.cloudinary.com/aomzjdia/image/upload/v1/places/camp2.jpg",
            caption="ลานกางเต็นท์ริมน้ำ"
        )

        self.assertEqual(place.images.count(), 2)
        self.assertEqual(img1.caption, "วิวหมอกยามเช้า")

    def test_review_and_average_rating(self):
        """Test rating and review calculations on a Place."""
        place = Place.objects.create(author=self.user1, name="Artisan Bakery", category="cafe")

        # User1 gives 5 stars
        Review.objects.create(
            place=place,
            user=self.user1,
            rating=5,
            comment="ขนมอบสดใหม่ อร่อยมาก!"
        )

        # User2 gives 4 stars
        Review.objects.create(
            place=place,
            user=self.user2,
            rating=4,
            comment="กาแฟรสชาติดี บรรยากาศเงียบสงบ"
        )

        self.assertEqual(place.review_count, 2)
        self.assertEqual(place.average_rating, 4.5)

    def test_review_rating_validation(self):
        """Test that review rating must be between 1 and 5 stars."""
        place = Place.objects.create(author=self.user1, name="Test Place", category="cafe")
        invalid_review = Review(
            place=place,
            user=self.user1,
            rating=6,  # Exceeds max rating of 5
            comment="Invalid rating test"
        )
        with self.assertRaises(ValidationError):
            invalid_review.full_clean()

    def test_wishlist_unique_constraint(self):
        """Test that a user cannot add the same place to wishlist twice."""
        place = Place.objects.create(author=self.user1, name="Secret Beach Villa", category="hotel")

        Wishlist.objects.create(user=self.user1, place=place)
        self.assertEqual(place.wishlist_count, 1)

        # Attempt duplicate wishlist
        with self.assertRaises(IntegrityError):
            Wishlist.objects.create(user=self.user1, place=place)

    def test_placelike_unique_constraint(self):
        """Test that a user cannot like the same place twice."""
        place = Place.objects.create(author=self.user1, name="Sunset Viewpoint", category="travel")

        PlaceLike.objects.create(user=self.user2, place=place)
        self.assertEqual(place.likes_count, 1)

        # Attempt duplicate like
        with self.assertRaises(IntegrityError):
            PlaceLike.objects.create(user=self.user2, place=place)


class ApiEndpointsTests(TestCase):
    """
    Tests for basic Zone In REST API routes (GET, POST).
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="api_tester",
            email="tester@zonein.app",
            password="testpassword"
        )
        self.place = Place.objects.create(
            author=self.user,
            name="Cafe De Botanica",
            category="cafe",
            description="คาเฟ่สไตล์ธรรมชาติ",
            address="เชียงใหม่",
            latitude=Decimal("18.7883"),
            longitude=Decimal("98.9853"),
            cover_image_url="https://res.cloudinary.com/aomzjdia/image/upload/v1/places/botanica.jpg"
        )

    def test_api_root(self):
        response = self.client.get("/api/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["name"], "Zone In API")
        self.assertIn("endpoints", data)

    def test_health_check(self):
        response = self.client.get("/api/health/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["database"], "connected")

    def test_places_list_and_create(self):
        # 1. GET places list
        response = self.client.get("/api/places/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertGreaterEqual(data["count"], 1)

        # 2. POST create place
        response = self.client.post(
            "/api/places/",
            data={
                "name": "Camp Viewpoint",
                "category": "nature",
                "description": "ลานกางเต็นท์ชมวิวทะเลหมอก",
                "address": "เพชรบูรณ์",
                "latitude": 16.7423,
                "longitude": 101.1234,
                "cover_image_url": "https://res.cloudinary.com/aomzjdia/image/upload/v1/places/camp.jpg"
            },
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        created_data = response.json()
        self.assertTrue(created_data["success"])
        self.assertEqual(created_data["place"]["name"], "Camp Viewpoint")

    def test_place_detail(self):
        response = self.client.get(f"/api/places/{self.place.id}/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["place"]["name"], "Cafe De Botanica")

    def test_reviews_list_and_create(self):
        # 1. POST add review
        response = self.client.post(
            f"/api/places/{self.place.id}/reviews/",
            data={"rating": 5, "comment": "เครื่องดื่มดี วิวสวยมาก"},
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertTrue(data["success"])

        # 2. GET reviews list
        response = self.client.get(f"/api/places/{self.place.id}/reviews/")
        self.assertEqual(response.status_code, 200)
        reviews_data = response.json()
        self.assertTrue(reviews_data["success"])
        self.assertEqual(reviews_data["review_count"], 1)

    def test_like_toggle(self):
        # 1. Like
        response = self.client.post(f"/api/places/{self.place.id}/like/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["is_liked"])

        # 2. Unlike
        response = self.client.post(f"/api/places/{self.place.id}/like/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data["is_liked"])

    def test_wishlist_list_and_toggle(self):
        # 1. Save to wishlist
        response = self.client.post(
            "/api/wishlist/toggle/",
            data={"place_id": self.place.id},
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["is_saved"])

        # 2. View wishlist
        response = self.client.get("/api/wishlist/")
        self.assertEqual(response.status_code, 200)
        wishlist_data = response.json()
        self.assertTrue(wishlist_data["success"])

    def test_profile_detail_and_update(self):
        # 1. GET profile
        response = self.client.get("/api/profile/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])

        # 2. POST update profile
        response = self.client.post(
            "/api/profile/",
            data={"nickname": "สายคาเฟ่ตัวจริง", "bio": "ตระเวนชิมกาแฟทั่วไทย"},
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        updated = response.json()
        self.assertTrue(updated["success"])
        self.assertEqual(updated["profile"]["nickname"], "สายคาเฟ่ตัวจริง")
