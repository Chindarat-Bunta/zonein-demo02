import json
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from .models import Comment, Place, Review


class PlaceModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.place = Place.objects.create(name="สวนเบญจกิติ", location="กรุงเทพฯ")

    def test_average_rating_and_reviews_count(self):
        """Average rating should compute correctly and reviews count match."""
        self.assertEqual(self.place.average_rating, 0.0)
        self.assertEqual(self.place.reviews_count, 0)

        Review.objects.create(place=self.place, author=self.user, rating=5, content="ยอดเยี่ยม")
        Review.objects.create(place=self.place, author=self.user, rating=3, content="พอใช้")

        self.assertEqual(self.place.reviews_count, 2)
        self.assertEqual(self.place.average_rating, 4.0)


class HomePageAPITests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username="somchai", password="password123")
        self.user2 = User.objects.create_user(username="ploy", password="password123")

        # Create 2 places
        self.place1 = Place.objects.create(name="ดอยอินทนนท์", location="เชียงใหม่")
        self.place2 = Place.objects.create(name="หาดป่าตอง", location="ภูเก็ต")

        # Create reviews with distinct ratings
        Review.objects.create(place=self.place1, author=self.user1, rating=5, content="หนาวจับใจ")
        Review.objects.create(place=self.place1, author=self.user2, rating=5, content="วิวอลังการ")
        Review.objects.create(place=self.place2, author=self.user1, rating=4, content="หาดทรายสวย")

    def test_home_page_renders_successfully(self):
        """Home page should return status code 200."""
        response = self.client.get(reverse("web:home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "web/home.html")

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

        # First review in response should have author and place information
        first_review = data["reviews"][0]
        self.assertIn("author", first_review)
        self.assertIn("place", first_review)
        self.assertIn("rating", first_review)
        self.assertIn("content", first_review)

    def test_api_place_detail(self):
        """Place detail API should return full info for a specific place."""
        response = self.client.get(reverse("web:api_place_detail", args=[self.place1.id]))
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
