from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class TravelPost(models.Model):
    """
    Traveler place recommendation and review post.
    โพสต์รีวิวสถานที่ท่องเที่ยว ให้คะแนนดาว แท็กสถานที่ และแนบรูป
    """
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="travel_posts")
    place_name = models.CharField(max_length=255, help_text="แท็กชื่อสถานที่ที่ไป")
    location = models.CharField(max_length=255, blank=True, default="", help_text="ที่ตั้ง / จังหวัด / พิกัด")
    category = models.CharField(max_length=100, blank=True, default="สถานที่ท่องเที่ยว", help_text="หมวดหมู่")
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="คะแนนดาวความประทับใจ 1-5 ดาว",
    )
    content = models.TextField(blank=True, default="", help_text="รีวิวบรรยากาศ ประสบการณ์ และสิ่งที่น่าสนใจ")
    image_url = models.TextField(blank=True, default="", help_text="รูปถ่ายสถานที่ (URL หรือ Base64 Data URL)")
    likes_count = models.PositiveIntegerField(default=0, help_text="จำนวนไลค์")
    comments_count = models.PositiveIntegerField(default=0, help_text="จำนวนความคิดเห็น")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "travel_posts"
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.rating}★] {self.place_name} ({self.location})"


class PostLike(models.Model):
    """
    Like / Heart on a travel post by a user.
    กดหัวใจ/ไลค์ให้กับโพสต์รีวิว
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="post_likes")
    post = models.ForeignKey(TravelPost, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "post_likes"
        unique_together = [("user", "post")]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} liked post {self.post_id}"


class PostComment(models.Model):
    """
    Comment on a travel post by a user.
    ความคิดเห็นต่อโพสต์รีวิวสถานที่
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="post_comments")
    post = models.ForeignKey(TravelPost, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField(help_text="ข้อความความคิดเห็น")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "post_comments"
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.place_name}"


# Backward compatibility aliases
Review = TravelPost
Place = TravelPost
Product = TravelPost
Like = PostLike
Comment = PostComment
