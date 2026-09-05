from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import Client, TestCase
from django.urls import reverse

from .models import TravelPost


class TravelPostModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="traveler", password="password123")

    def test_rating_validators_on_model(self):
        """TravelPost model validation should reject rating < 1 or > 5."""
        invalid_low = TravelPost(author=self.user, place_name="ดอยอินทนนท์", rating=0)
        with self.assertRaises(ValidationError):
            invalid_low.full_clean()

        invalid_high = TravelPost(author=self.user, place_name="ดอยอินทนนท์", rating=6)
        with self.assertRaises(ValidationError):
            invalid_high.full_clean()

        valid_post = TravelPost(author=self.user, place_name="ดอยอินทนนท์", rating=5)
        valid_post.full_clean()  # should not raise


class TravelPostAPITests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="traveler", password="password123")

    def test_create_travel_post_with_place_tag_and_rating(self):
        """Create a travel post with place tag, location, 1-5 star rating, and review text."""
        response = self.client.post(
            reverse("web:api_posts"),
            data={
                "place_name": "สวนป่าเบญจกิติ",
                "category": "ธรรมชาติ & สวนสาธารณะ",
                "location": "กรุงเทพฯ",
                "rating": 5,
                "content": "วิวพระอาทิตย์ตกสวยมาก Skywalk เดินเพลิน",
                "image_url": "https://images.unsplash.com/photo-1596422846543-75c6fc197f07",
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["post"]["place_name"], "สวนป่าเบญจกิติ")
        self.assertEqual(data["post"]["location"], "กรุงเทพฯ")
        self.assertEqual(data["post"]["rating"], 5)

        # Verify post is saved in DB
        post = TravelPost.objects.get(pk=data["post"]["id"])
        self.assertEqual(post.place_name, "สวนป่าเบญจกิติ")
        self.assertEqual(post.rating, 5)

    def test_rating_out_of_range_rejected(self):
        """Rating outside 1-5 should return 400."""
        for invalid_rating in [0, 6, -1, 10, "invalid"]:
            res = self.client.post(
                reverse("web:api_posts"),
                data={"place_name": "ผาเดียวดาย", "rating": invalid_rating, "content": "Test"},
                content_type="application/json",
            )
            self.assertEqual(res.status_code, 400)

    def test_edit_travel_post(self):
        """Can edit travel post place name, location, rating, and review text."""
        post = TravelPost.objects.create(
            author=self.user,
            place_name="หาดไร่เลย์",
            category="ทะเล",
            location="กระบี่",
            rating=4,
            content="หาดสวย",
        )

        res_ok = self.client.put(
            reverse("web:api_post_detail", args=[post.id]),
            data={
                "place_name": "หาดไร่เลย์วิวพระอาทิตย์ตก",
                "location": "อ.เมือง จ.กระบี่",
                "rating": 5,
                "content": "อัปเดตดาวเป็น 5 ดาว วิวสุดยอดมาก",
            },
            content_type="application/json",
        )
        self.assertEqual(res_ok.status_code, 200)
        post.refresh_from_db()
        self.assertEqual(post.place_name, "หาดไร่เลย์วิวพระอาทิตย์ตก")
        self.assertEqual(post.location, "อ.เมือง จ.กระบี่")
        self.assertEqual(post.rating, 5)

    def test_delete_travel_post(self):
        """Can delete travel post."""
        post = TravelPost.objects.create(
            author=self.user,
            place_name="คาเฟ่ริมน้ำ",
            rating=5,
            content="ชิลล์มาก",
        )

        res_del = self.client.delete(reverse("web:api_post_detail", args=[post.id]))
        self.assertEqual(res_del.status_code, 200)
        self.assertFalse(TravelPost.objects.filter(pk=post.id).exists())

    def test_xss_sanitization_in_post_content(self):
        """Script tags in place name and content must be escaped."""
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

    def test_get_posts_list_and_category_filter(self):
        """GET /api/posts/ should list posts and support category filtering."""
        TravelPost.objects.create(
            author=self.user,
            place_name="ดอยหลวงเชียงดาว",
            category="แคมป์ปิ้ง & ภูเขา",
            location="เชียงใหม่",
            rating=5,
        )
        TravelPost.objects.create(
            author=self.user,
            place_name="เกาะพีพี",
            category="ทะเล & ชายหาด",
            location="กระบี่",
            rating=5,
        )

        # All posts
        res_all = self.client.get(reverse("web:api_posts"))
        self.assertEqual(res_all.status_code, 200)
        self.assertEqual(len(res_all.json()["results"]), 2)

        # Filter by category
        res_filtered = self.client.get(reverse("web:api_posts"), {"category": "แคมป์ปิ้ง & ภูเขา"})
        self.assertEqual(res_filtered.status_code, 200)
        self.assertEqual(len(res_filtered.json()["results"]), 1)
        self.assertEqual(res_filtered.json()["results"][0]["place_name"], "ดอยหลวงเชียงดาว")
