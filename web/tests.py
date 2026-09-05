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


class PostLikeAPITests(TestCase):
    def setUp(self):
        self.client = Client()
        self.author = User.objects.create_user(username="author_traveler", password="password123")
        self.user1 = User.objects.create_user(username="user1_liker", password="password123")
        self.user2 = User.objects.create_user(username="user2_liker", password="password123")
        self.post = TravelPost.objects.create(
            author=self.author,
            place_name="ดอยอินทนนท์",
            location="เชียงใหม่",
            rating=5,
            content="ยอดดอยหนาวมาก",
        )

    def test_default_user_like_flow(self):
        """Unauthenticated user in demo uses default traveler user to like seamlessly."""
        res = self.client.post(reverse("web:api_post_like", args=[self.post.id]))
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()["liked"])
        self.assertEqual(res.json()["likes_count"], 1)


    def test_toggle_like_and_unlike(self):
        """Authenticated user can toggle like and unlike on a post."""
        self.client.force_login(self.user1)

        # 1. First click: Like
        res_like = self.client.post(reverse("web:api_post_like", args=[self.post.id]))
        self.assertEqual(res_like.status_code, 200)
        data_like = res_like.json()
        self.assertTrue(data_like["liked"])
        self.assertEqual(data_like["likes_count"], 1)

        self.post.refresh_from_db()
        self.assertEqual(self.post.likes_count, 1)

        # 2. Second click: Unlike (Toggle)
        res_unlike = self.client.post(reverse("web:api_post_like", args=[self.post.id]))
        self.assertEqual(res_unlike.status_code, 200)
        data_unlike = res_unlike.json()
        self.assertFalse(data_unlike["liked"])
        self.assertEqual(data_unlike["likes_count"], 0)

        self.post.refresh_from_db()
        self.assertEqual(self.post.likes_count, 0)

    def test_explicit_delete_unlike(self):
        """DELETE /api/posts/<id>/like/ explicitly unlikes a post."""
        self.client.force_login(self.user1)
        # Like first
        self.client.post(reverse("web:api_post_like", args=[self.post.id]))

        # Explicit DELETE
        res_del = self.client.delete(reverse("web:api_post_like", args=[self.post.id]))
        self.assertEqual(res_del.status_code, 200)
        self.assertFalse(res_del.json()["liked"])
        self.assertEqual(res_del.json()["likes_count"], 0)

    def test_multiple_users_like_same_post(self):
        """Multiple distinct users liking a post increases likes_count accurately."""
        # User 1 likes
        self.client.force_login(self.user1)
        res1 = self.client.post(reverse("web:api_post_like", args=[self.post.id]))
        self.assertEqual(res1.json()["likes_count"], 1)

        # User 2 likes
        self.client.force_login(self.user2)
        res2 = self.client.post(reverse("web:api_post_like", args=[self.post.id]))
        self.assertEqual(res2.json()["likes_count"], 2)

        self.post.refresh_from_db()
        self.assertEqual(self.post.likes_count, 2)

    def test_get_post_likes_list(self):
        """GET /api/posts/<id>/likes/ returns the list of likers and count."""
        self.client.force_login(self.user1)
        self.client.post(reverse("web:api_post_like", args=[self.post.id]))

        self.client.force_login(self.user2)
        self.client.post(reverse("web:api_post_like", args=[self.post.id]))

        res = self.client.get(reverse("web:api_post_likes", args=[self.post.id]))
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["likes_count"], 2)
        self.assertEqual(len(data["users"]), 2)
        usernames = [u["username"] for u in data["users"]]
        self.assertIn("user1_liker", usernames)
        self.assertIn("user2_liker", usernames)
        self.assertTrue(data["is_liked"])  # user2 is logged in

    def test_post_feed_serialization_includes_like_state(self):
        """GET /api/posts/ includes likes_count and is_liked status."""
        self.client.force_login(self.user1)
        self.client.post(reverse("web:api_post_like", args=[self.post.id]))

        # Check feed as user1 (liked = True)
        res_user1 = self.client.get(reverse("web:api_posts"))
        self.assertEqual(res_user1.status_code, 200)
        post_item = res_user1.json()["results"][0]
        self.assertEqual(post_item["likes_count"], 1)
        self.assertTrue(post_item["is_liked"])

        # Check feed as user2 (liked = False)
        self.client.force_login(self.user2)
        res_user2 = self.client.get(reverse("web:api_posts"))
        post_item2 = res_user2.json()["results"][0]
        self.assertEqual(post_item2["likes_count"], 1)
        self.assertFalse(post_item2["is_liked"])


class PostCommentAPITests(TestCase):
    def setUp(self):
        self.client = Client()
        self.author = User.objects.create_user(username="author_user", password="password123")
        self.commenter1 = User.objects.create_user(username="commenter_one", password="password123")
        self.commenter2 = User.objects.create_user(username="commenter_two", password="password123")
        self.post = TravelPost.objects.create(
            author=self.author,
            place_name="ดอยม่อนแจ่ม",
            rating=5,
            content="บรรยากาศดีมาก อากาศเย็นสบาย",
        )

    def test_add_comment_to_post(self):
        """POST /api/posts/<id>/comments/ creates a comment and increments comments_count."""
        self.client.force_login(self.commenter1)
        res = self.client.post(
            reverse("web:api_post_comments", args=[self.post.id]),
            data={"content": "น่าไปมากเลยครับ ขอบคุณที่รีวิวครับ"},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertEqual(data["comment"]["author_name"], "commenter_one")
        self.assertEqual(data["comment"]["content"], "น่าไปมากเลยครับ ขอบคุณที่รีวิวครับ")
        self.assertEqual(data["comments_count"], 1)

        self.post.refresh_from_db()
        self.assertEqual(self.post.comments_count, 1)

    def test_get_post_comments_list(self):
        """GET /api/posts/<id>/comments/ returns all comments in chronological order."""
        self.client.force_login(self.commenter1)
        self.client.post(
            reverse("web:api_post_comments", args=[self.post.id]),
            data={"content": "คอมเมนต์ที่ 1"},
            content_type="application/json",
        )

        self.client.force_login(self.commenter2)
        self.client.post(
            reverse("web:api_post_comments", args=[self.post.id]),
            data={"content": "คอมเมนต์ที่ 2"},
            content_type="application/json",
        )

        res = self.client.get(reverse("web:api_post_comments", args=[self.post.id]))
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["comments_count"], 2)
        self.assertEqual(len(data["comments"]), 2)
        self.assertEqual(data["comments"][0]["content"], "คอมเมนต์ที่ 1")
        self.assertEqual(data["comments"][1]["content"], "คอมเมนต์ที่ 2")

    def test_delete_comment(self):
        """DELETE /api/posts/<id>/comments/<comment_id>/ deletes comment and decrements count."""
        self.client.force_login(self.commenter1)
        res_create = self.client.post(
            reverse("web:api_post_comments", args=[self.post.id]),
            data={"content": "ความคิดเห็นชั่วคราว"},
            content_type="application/json",
        )
        comment_id = res_create.json()["comment"]["id"]
        self.post.refresh_from_db()
        self.assertEqual(self.post.comments_count, 1)

        # Delete comment
        res_del = self.client.delete(reverse("web:api_post_comment_delete", args=[self.post.id, comment_id]))
        self.assertEqual(res_del.status_code, 200)
        self.assertEqual(res_del.json()["comments_count"], 0)

        self.post.refresh_from_db()
        self.assertEqual(self.post.comments_count, 0)

    def test_unauthorized_user_cannot_delete_others_comment(self):
        """User cannot delete another user's comment."""
        self.client.force_login(self.commenter1)
        res_create = self.client.post(
            reverse("web:api_post_comments", args=[self.post.id]),
            data={"content": "ความคิดเห็นของคนแรก"},
            content_type="application/json",
        )
        comment_id = res_create.json()["comment"]["id"]

        # Attempt delete as commenter2
        self.client.force_login(self.commenter2)
        res_del = self.client.delete(reverse("web:api_post_comment_delete", args=[self.post.id, comment_id]))
        self.assertEqual(res_del.status_code, 403)

    def test_empty_comment_rejected(self):
        """Empty or whitespace comment should return 400 error."""
        self.client.force_login(self.commenter1)
        res = self.client.post(
            reverse("web:api_post_comments", args=[self.post.id]),
            data={"content": "   "},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 400)

    def test_comment_xss_sanitized(self):
        """Script tags in comment content should be escaped."""
        self.client.force_login(self.commenter1)
        res = self.client.post(
            reverse("web:api_post_comments", args=[self.post.id]),
            data={"content": "<script>alert('xss')</script> สวยมาก"},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 201)
        self.assertNotIn("<script>", res.json()["comment"]["content"])
        self.assertIn("&lt;script&gt;", res.json()["comment"]["content"])


class FollowModelAndAPITests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username="alice", password="password123")
        self.user2 = User.objects.create_user(username="bob", password="password123")

    def test_follow_toggle_flow(self):
        """User can follow and unfollow another user via API."""
        self.client.force_login(self.user1)

        # 1. Follow bob
        res_follow = self.client.post(
            reverse("web:api_user_follow", args=[self.user2.id]),
            data={"action": "follow"},
            content_type="application/json",
        )
        self.assertEqual(res_follow.status_code, 200)
        self.assertTrue(res_follow.json()["is_following"])
        self.assertEqual(res_follow.json()["followers_count"], 1)

        # 2. Check follow status
        res_status = self.client.get(reverse("web:api_user_follow_status", args=[self.user2.id]))
        self.assertEqual(res_status.status_code, 200)
        self.assertTrue(res_status.json()["is_following"])
        self.assertEqual(res_status.json()["followers_count"], 1)

        # 3. Unfollow bob via DELETE
        res_unfollow = self.client.delete(reverse("web:api_user_follow", args=[self.user2.id]))
        self.assertEqual(res_unfollow.status_code, 200)
        self.assertFalse(res_unfollow.json()["is_following"])
        self.assertEqual(res_unfollow.json()["followers_count"], 0)

    def test_cannot_self_follow(self):
        """User cannot follow themselves."""
        self.client.force_login(self.user1)
        res = self.client.post(reverse("web:api_user_follow", args=[self.user1.id]))
        self.assertEqual(res.status_code, 400)


