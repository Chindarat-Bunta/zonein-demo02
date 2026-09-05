from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction
from django.db.models import Avg, Count


class Place(models.Model):
    """Place / Location post that can be recommended and reviewed."""

    name = models.CharField(max_length=255, help_text="ชื่อสถานที่ / ชื่อโพสต์แนะนำ")
    category = models.CharField(max_length=100, blank=True, default="สถานที่ท่องเที่ยว", help_text="หมวดหมู่ เช่น คาเฟ่, สวนสาธารณะ, แคมป์ปิ้ง")
    location = models.CharField(max_length=255, blank=True, default="", help_text="ที่ตั้ง / จังหวัด / พิกัด")
    description = models.TextField(blank=True, default="", help_text="ไฮไลท์และรายละเอียดว่าที่นี่มีอะไรน่าสนใจ")
    image_url = models.URLField(blank=True, default="")
    average_rating = models.FloatField(default=0.0)
    review_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "places"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.location})" if self.location else self.name

    @transaction.atomic
    def update_rating_stats(self):
        """Recalculate and update cached average_rating and review_count atomically."""
        stats = self.reviews.aggregate(
            avg_rating=Avg("rating"),
            count=Count("id"),
        )
        self.average_rating = round(stats["avg_rating"] or 0.0, 2)
        self.review_count = stats["count"] or 0
        self.save(update_fields=["average_rating", "review_count", "updated_at"])


# Alias for backward compatibility
Product = Place


class Review(models.Model):
    """User review with 1-5 star rating, comment, and tagged friends for a place."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    target = models.ForeignKey(
        Place, on_delete=models.CASCADE, related_name="reviews"
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="คะแนนดาว 1-5 ดาว",
    )
    comment = models.TextField(blank=True, default="")
    tagged_users = models.ManyToManyField(
        User, related_name="tagged_reviews", blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "reviews"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "target"],
                name="unique_user_target_review",
            )
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"Review by {self.user.username} on {self.target.name} ({self.rating} stars)"
