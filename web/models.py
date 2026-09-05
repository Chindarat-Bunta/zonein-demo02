from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg, Count


class Place(models.Model):
    """
    Travel destination / location place model.
    สถานที่ท่องเที่ยว จุดเช็คอิน คาเฟ่ และร้านอาหาร
    """
    name = models.CharField(max_length=255, help_text="ชื่อสถานที่ท่องเที่ยว")
    location = models.CharField(max_length=255, help_text="ที่ตั้ง / จังหวัด / พิกัด")
    category = models.CharField(max_length=100, default="สถานที่ท่องเที่ยว", blank=True, help_text="หมวดหมู่")
    description = models.TextField(blank=True, default="", help_text="คำอธิบายสถานที่โดยย่อ")
    image_url = models.TextField(blank=True, default="", help_text="รูปภาพหน้าปกสถานที่")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "places"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.location})"

    @property
    def average_rating(self):
        """Calculate average rating for this place."""
        res = self.reviews.aggregate(avg=Avg("rating"))
        return round(res["avg"], 1) if res["avg"] is not None else 0.0

    @property
    def reviews_count(self):
        """Count total reviews for this place."""
        return self.reviews.count()


class Review(models.Model):
    """
    Review and rating given to a place by a user.
    รีวิวและคะแนนความประทับใจของสถานที่
    """
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name="reviews")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="คะแนนความประทับใจ 1-5 ดาว",
    )
    content = models.TextField(blank=True, default="", help_text="ข้อความรีวิวบรรยากาศและประสบการณ์")
    image_url = models.TextField(blank=True, default="", help_text="รูปถ่ายสถานที่ประกอบรีวิว")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "reviews"
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.rating}★] {self.author.username} on {self.place.name}"


# Alias for backward compatibility
TravelPost = Review
