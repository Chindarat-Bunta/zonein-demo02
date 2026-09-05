from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import Client, TestCase
from django.urls import reverse

from .models import TravelPost


class TravelPostModelTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="traveler1", password="password123")
        self.user2 = User.objects.create_user(username="traveler2", password="password123")

    def test_rating_validators_on_model(self):
        """TravelPost model validation should reject rating < 1 or > 5."""
        invalid_low = TravelPost(author=self.user1, place_name="ดอยอินทนนท์", rating=0)
        with self.assertRaises(ValidationError):
            invalid_low.full_clean()

        invalid_high = TravelPost(author=self.user1, place_name="ดอยอินทนนท์", rating=6)
        with self.assertRaises(ValidationError):
            invalid_high.full_clean()

        valid_post = TravelPost(author=self.user1, place_name="ดอยอินทนนท์", rating=5)
        valid_post.full_clean()  # should not raise


class TravelPostAPITests(TestCase):
    def setUp(self):
        self.client = Client()
        self.author = User.objects.create_user(username="author1", password="password123")
        self.other_user = User.objects.create_user(username="other_user", password="password123")
        self.friend = User.objects.create_user(username="sarah_friend", password="password123")
        self.admin_user = User.objects.create_superuser(username="admin", password="password123", email="admin@example.com")

    def test_unauthenticated_user_cannot_create_post(self):
        """POST /api/posts/ should return 401 for unauthenticated users."""
        response = self.client.post(
            reverse("web:api_posts"),
            data={"place_name": "สวนป่าเบญจกิติ", "rating": 5, "content": "สวยมาก!"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)

    def test_create_travel_post_with_rating_and_tagging(self):
        """Authenticated traveler can create post with rating 1-5, photo, and @mention friends."""
        self.client.force_login(self.author)
        response = self.client.post(
            reverse("web:api_posts"),
            data={
                "place_name": "สวนป่าเบญจกิติ",
                "category": "ธรรมชาติ & สวนสาธารณะ",
                "location": "กรุงเทพฯ",
                "rating": 5,
                "content": "วิวพระอาทิตย์ตกสวยมาก @sarah_friend ต้องมาถ่ายรูปนะ!",
                "image_url": "https://images.unsplash.com/photo-1596422846543-75c6fc197f07",
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["post"]["place_name"], "สวนป่าเบญจกิติ")
        self.assertEqual(data["post"]["rating"], 5)
        tagged_names = [u["username"] for u in data["post"]["tagged_users"]]
        self.assertIn("sarah_friend", tagged_names)

        # Verify post is saved in DB
        post = TravelPost.objects.get(pk=data["post"]["id"])
        self.assertEqual(post.author, self.author)
        self.assertEqual(post.rating, 5)

        # Log in as tagged friend and verify is_tagged is True
        self.client.force_login(self.friend)
        feed_res = self.client.get(reverse("web:api_posts"))
        feed_data = feed_res.json()
        self.assertTrue(feed_data["results"][0]["is_tagged"])

    def test_rating_out_of_range_rejected(self):
        """Rating outside 1-5 should return 400."""
        self.client.force_login(self.author)
        for invalid_rating in [0, 6, -1, 10, "invalid"]:
            res = self.client.post(
                reverse("web:api_posts"),
                data={"place_name": "ผาเดียวดาย", "rating": invalid_rating, "content": "Test"},
                content_type="application/json",
            )
            self.assertEqual(res.status_code, 400)

    def test_edit_travel_post_owner_only(self):
        """Author can edit their post, others cannot."""
        post = TravelPost.objects.create(
            author=self.author,
            place_name="หาดไร่เลย์",
            category="ทะเล",
            location="กระบี่",
            rating=4,
            content="หาดสวย",
        )

        # Other user cannot edit -> 403
        self.client.force_login(self.other_user)
        res_forbidden = self.client.put(
            reverse("web:api_post_detail", args=[post.id]),
            data={"place_name": "Hacked", "rating": 1},
            content_type="application/json",
        )
        self.assertEqual(res_forbidden.status_code, 403)

        # Author can edit -> 200
        self.client.force_login(self.author)
        res_ok = self.client.put(
            reverse("web:api_post_detail", args=[post.id]),
            data={"place_name": "หาดไร่เลย์วิวสวย", "rating": 5, "content": "อัปเดตดาวเป็น 5 ดาว"},
            content_type="application/json",
        )
        self.assertEqual(res_ok.status_code, 200)
        post.refresh_from_db()
        self.assertEqual(post.place_name, "หาดไร่เลย์วิวสวย")
        self.assertEqual(post.rating, 5)

    def test_delete_travel_post_permission(self):
        """Author or Admin can delete post, other users cannot."""
        post = TravelPost.objects.create(
            author=self.author,
            place_name="คาเฟ่ริมน้ำ",
            rating=5,
            content="ชิลล์มาก",
        )

        # Other user cannot delete -> 403
        self.client.force_login(self.other_user)
        res_user2 = self.client.delete(reverse("web:api_post_detail", args=[post.id]))
        self.assertEqual(res_user2.status_code, 403)

        # Author can delete -> 200
        self.client.force_login(self.author)
        res_del = self.client.delete(reverse("web:api_post_detail", args=[post.id]))
        self.assertEqual(res_del.status_code, 200)
        self.assertFalse(TravelPost.objects.filter(pk=post.id).exists())

    def test_admin_can_delete_any_post(self):
        """Admin can delete any travel post."""
        post = TravelPost.objects.create(
            author=self.author,
            place_name="จุดกางเต็นท์",
            rating=5,
        )
        self.client.force_login(self.admin_user)
        res_admin = self.client.delete(reverse("web:api_post_detail", args=[post.id]))
        self.assertEqual(res_admin.status_code, 200)
        self.assertFalse(TravelPost.objects.filter(pk=post.id).exists())

    def test_xss_sanitization_in_post_content(self):
        """Script tags in place name and content must be escaped."""
        self.client.force_login(self.author)
        res = self.client.post(
            reverse("web:api_posts"),
            data={
                "place_name": "<script>alert('place')</script>สวนสาธารณะ",
                "rating": 5,
                "content": "<script>alert('XSS')</script><b>Bold</b>",
            },
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 201)
        post_data = res.json()["post"]
        self.assertNotIn("<script>", post_data["place_name"])
        self.assertIn("&lt;script&gt;", post_data["place_name"])
        self.assertNotIn("<script>", post_data["content"])

    def test_users_list_for_tagging(self):
        """GET /api/users/?q=xxx returns searchable user list."""
        res = self.client.get(f"{reverse('web:api_users')}?q=sarah")
        self.assertEqual(res.status_code, 200)
        users = res.json()["users"]
        usernames = [u["username"] for u in users]
        self.assertIn("sarah_friend", usernames)
