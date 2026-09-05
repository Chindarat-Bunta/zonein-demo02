from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction
from django.db.models import Avg, Count


class Product(models.Model):
    """Product/Service target that can be reviewed."""

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    image_url = models.URLField(blank=True, default="")
    average_rating = models.FloatField(default=0.0)
    review_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "products"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

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


class Review(models.Model):
    """User review with 1-5 star rating and comment for a product/service."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    target = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating must be an integer between 1 and 5",
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
