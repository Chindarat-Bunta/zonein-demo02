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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "travel_posts"
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.rating}★] {self.place_name} ({self.location})"


# Backward compatibility aliases
Review = TravelPost
Place = TravelPost
Product = TravelPost
