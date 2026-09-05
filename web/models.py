from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class TravelPost(models.Model):
    """
    Traveler place recommendation and review post.
    โพสต์แนะนำสถานที่ท่องเที่ยวพร้อมรีวิว ให้ดาว และแท็กเพื่อน
    """
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="travel_posts")
    place_name = models.CharField(max_length=255, help_text="ชื่อสถานที่ท่องเที่ยว / ร้าน / จุดเช็คอิน")
    location = models.CharField(max_length=255, blank=True, default="", help_text="ที่ตั้ง / จังหวัด / พิกัด")
    category = models.CharField(max_length=100, blank=True, default="สถานที่ท่องเที่ยว", help_text="หมวดหมู่ เช่น ธรรมชาติ, คาเฟ่, แคมป์ปิ้ง")
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="คะแนนดาวความประทับใจ 1-5 ดาว",
    )
    content = models.TextField(blank=True, default="", help_text="รีวิวบรรยากาศ ไฮไลท์ และสิ่งที่น่าสนใจ")
    image_url = models.URLField(blank=True, default="", help_text="ลิงก์รูปถ่ายสถานที่")
    tagged_users = models.ManyToManyField(User, related_name="tagged_in_posts", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "travel_posts"
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.rating}★] {self.place_name} โดย @{self.author.username}"


# Alias for backward compatibility
Review = TravelPost
Place = TravelPost
Product = TravelPost
