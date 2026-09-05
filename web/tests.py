from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import Client, TestCase
from django.urls import reverse

from .models import Place, Review


class RatingReviewModelTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", password="password123")
        self.user2 = User.objects.create_user(username="user2", password="password123")
        self.place = Place.objects.create(
            name="สวนป่าเบญจกิติ",
            category="สวนสาธารณะ",
            location="กรุงเทพฯ",
            description="สวนสาธารณะใจกลางเมือง",
        )

    def test_rating_validators_on_model(self):
        """Review model validation should reject rating < 1 or > 5."""
        invalid_low = Review(user=self.user1, target=self.place, rating=0)
        with self.assertRaises(ValidationError):
            invalid_low.full_clean()

        invalid_high = Review(user=self.user1, target=self.place, rating=6)
        with self.assertRaises(ValidationError):
            invalid_high.full_clean()

        valid_review = Review(user=self.user1, target=self.place, rating=5)
        valid_review.full_clean()  # should not raise

    def test_unique_user_target_constraint(self):
        """One user can only create one review per target place."""
        Review.objects.create(user=self.user1, target=self.place, rating=5, comment="First review")
        with self.assertRaises(IntegrityError):
            Review.objects.create(user=self.user1, target=self.place, rating=4, comment="Duplicate review")

    def test_recalculate_average_rating_and_count(self):
        """Average rating and review count must update accurately on create, update, and delete."""
        self.assertEqual(self.place.average_rating, 0.0)
        self.assertEqual(self.place.review_count, 0)

        # 1. First review: 5 stars
        r1 = Review.objects.create(user=self.user1, target=self.place, rating=5)
        self.place.update_rating_stats()
        self.place.refresh_from_db()
        self.assertEqual(self.place.review_count, 1)
        self.assertEqual(self.place.average_rating, 5.0)

        # 2. Second review: 4 stars -> (5 + 4) / 2 = 4.5
        r2 = Review.objects.create(user=self.user2, target=self.place, rating=4)
        self.place.update_rating_stats()
        self.place.refresh_from_db()
        self.assertEqual(self.place.review_count, 2)
        self.assertEqual(self.place.average_rating, 4.5)

        # 3. Update review: r2 from 4 stars to 2 stars -> (5 + 2) / 2 = 3.5
        r2.rating = 2
        r2.save()
        self.place.update_rating_stats()
        self.place.refresh_from_db()
        self.assertEqual(self.place.review_count, 2)
        self.assertEqual(self.place.average_rating, 3.5)

        # 4. Delete review: delete r1 -> remaining: r2 (2 stars) -> avg 2.0, count 1
        r1.delete()
        self.place.update_rating_stats()
        self.place.refresh_from_db()
        self.assertEqual(self.place.review_count, 1)
        self.assertEqual(self.place.average_rating, 2.0)


class RatingReviewAPITests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username="author1", password="password123")
        self.user2 = User.objects.create_user(username="author2", password="password123")
        self.admin_user = User.objects.create_superuser(username="admin", password="password123", email="admin@example.com")
        self.place = Place.objects.create(
            name="Riva Floating Cafe",
            category="คาเฟ่ริมน้ำ",
            location="นครปฐม",
            description="คาเฟ่แพริมน้ำ",
        )

    def test_unauthenticated_user_cannot_create_review(self):
        """POST /api/reviews/ should return 401 for unauthenticated users."""
        response = self.client.post(
            reverse("web:api_reviews_list_create"),
            data={"target_id": self.place.id, "rating": 5, "comment": "Great!"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)

    def test_create_review_success(self):
        """Authenticated user can submit valid review and target stats are updated."""
        self.client.force_login(self.user1)
        response = self.client.post(
            reverse("web:api_reviews_list_create"),
            data={"target_id": self.place.id, "rating": 5, "comment": "Awesome place!"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["review"]["rating"], 5)
        self.assertEqual(data["review"]["comment"], "Awesome place!")

        self.place.refresh_from_db()
        self.assertEqual(self.place.review_count, 1)
        self.assertEqual(self.place.average_rating, 5.0)

    def test_validation_rating_out_of_range(self):
        """Rating outside 1-5 should return 400 Bad Request."""
        self.client.force_login(self.user1)
        for invalid_rating in [0, 6, -1, 10, "invalid"]:
            response = self.client.post(
                reverse("web:api_reviews_list_create"),
                data={"target_id": self.place.id, "rating": invalid_rating, "comment": "Bad"},
                content_type="application/json",
            )
            self.assertEqual(response.status_code, 400)

    def test_prevent_duplicate_review(self):
        """Submitting a duplicate review for the same target should return 400."""
        self.client.force_login(self.user1)
        # First submission
        res1 = self.client.post(
            reverse("web:api_reviews_list_create"),
            data={"target_id": self.place.id, "rating": 4, "comment": "Good"},
            content_type="application/json",
        )
        self.assertEqual(res1.status_code, 201)

        # Second submission
        res2 = self.client.post(
            reverse("web:api_reviews_list_create"),
            data={"target_id": self.place.id, "rating": 5, "comment": "Trying again"},
            content_type="application/json",
        )
        self.assertEqual(res2.status_code, 400)
        self.assertIn("already reviewed", res2.json()["error"])

    def test_xss_sanitization_in_comment(self):
        """HTML/Script tags in comments must be sanitized."""
        self.client.force_login(self.user1)
        malicious_input = "<script>alert('XSS')</script><b>Bold</b>"
        response = self.client.post(
            reverse("web:api_reviews_list_create"),
            data={"target_id": self.place.id, "rating": 5, "comment": malicious_input},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        created_comment = response.json()["review"]["comment"]
        self.assertNotIn("<script>", created_comment)
        self.assertIn("&lt;script&gt;", created_comment)

    def test_update_review_ownership_and_stats(self):
        """Owner can edit their review and average rating updates accordingly."""
        review = Review.objects.create(user=self.user1, target=self.place, rating=3, comment="Average")
        self.place.update_rating_stats()

        # User 2 tries to edit User 1's review -> 403 Forbidden
        self.client.force_login(self.user2)
        res_forbidden = self.client.put(
            reverse("web:api_review_detail", args=[review.id]),
            data={"rating": 5, "comment": "Hacked"},
            content_type="application/json",
        )
        self.assertEqual(res_forbidden.status_code, 403)

        # User 1 edits own review -> 200 OK
        self.client.force_login(self.user1)
        res_ok = self.client.put(
            reverse("web:api_review_detail", args=[review.id]),
            data={"rating": 5, "comment": "Changed mind, it is great!"},
            content_type="application/json",
        )
        self.assertEqual(res_ok.status_code, 200)

        self.place.refresh_from_db()
        self.assertEqual(self.place.average_rating, 5.0)

    def test_delete_review_permission(self):
        """Review author or Admin can delete review, others cannot."""
        review = Review.objects.create(user=self.user1, target=self.place, rating=5, comment="Top")
        self.place.update_rating_stats()
        self.assertEqual(self.place.review_count, 1)

        # User 2 cannot delete
        self.client.force_login(self.user2)
        res_user2 = self.client.delete(reverse("web:api_review_detail", args=[review.id]))
        self.assertEqual(res_user2.status_code, 403)

        # Admin can delete
        self.client.force_login(self.admin_user)
        res_admin = self.client.delete(reverse("web:api_review_detail", args=[review.id]))
        self.assertEqual(res_admin.status_code, 200)

        self.place.refresh_from_db()
        self.assertEqual(self.place.review_count, 0)
        self.assertEqual(self.place.average_rating, 0.0)

    def test_reviews_summary_and_breakdown(self):
        """Summary endpoint returns correct average, total, star breakdown, and user status."""
        Review.objects.create(user=self.user1, target=self.place, rating=5)
        Review.objects.create(user=self.user2, target=self.place, rating=4)
        self.place.update_rating_stats()

        self.client.force_login(self.user1)
        response = self.client.get(f"{reverse('web:api_reviews_summary')}?target_id={self.place.id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["average_rating"], 4.5)
        self.assertEqual(data["review_count"], 2)
        self.assertEqual(data["breakdown"]["5"], 1)
        self.assertEqual(data["breakdown"]["4"], 1)
        self.assertEqual(data["breakdown"]["1"], 0)
        self.assertTrue(data["user_reviewed"])

    def test_reviews_pagination(self):
        """GET /api/reviews/?target_id=xxx returns paginated review results."""
        # Create 15 reviews
        for i in range(15):
            u = User.objects.create_user(username=f"user_{i}", password="password")
            Review.objects.create(user=u, target=self.place, rating=4, comment=f"Comment {i}")

        response = self.client.get(
            f"{reverse('web:api_reviews_list_create')}?target_id={self.place.id}&page=1&page_size=5"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["count"], 15)
        self.assertEqual(data["num_pages"], 3)
        self.assertEqual(len(data["results"]), 5)
        self.assertTrue(data["has_next"])

    def test_tagging_friends_in_review(self):
        """Review creation with @mentions and explicit tagged_user_ids should link tagged users."""
        friend = User.objects.create_user(username="sarah_friend", password="password123")
        self.client.force_login(self.user1)

        response = self.client.post(
            reverse("web:api_reviews_list_create"),
            data={
                "target_id": self.place.id,
                "rating": 5,
                "comment": "Check this out @sarah_friend it is amazing!",
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        tagged_names = [u["username"] for u in data["review"]["tagged_users"]]
        self.assertIn("sarah_friend", tagged_names)

        # Log in as friend and verify is_tagged is True
        self.client.force_login(friend)
        res_list = self.client.get(
            f"{reverse('web:api_reviews_list_create')}?target_id={self.place.id}"
        )
        review_data = res_list.json()["results"][0]
        self.assertTrue(review_data["is_tagged"])

    def test_users_list_api(self):
        """GET /api/users/ returns searchable user list for autocomplete tagging."""
        response = self.client.get(f"{reverse('web:api_users')}?q=author")
        self.assertEqual(response.status_code, 200)
        users = response.json()["users"]
        usernames = [u["username"] for u in users]
        self.assertIn("author1", usernames)
        self.assertIn("author2", usernames)
