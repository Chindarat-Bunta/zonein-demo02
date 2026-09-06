from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Place(models.Model):
    PRICE_CHOICES = [
        (1, "฿ (ประหยัด)"),
        (2, "฿฿ (ปานกลาง)"),
        (3, "฿฿฿ (พรีเมียม)"),
        (4, "฿฿฿฿ (หรูหรา)"),
    ]

    name = models.CharField(max_length=200, verbose_name="ชื่อสถานที่")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="Slug")
    description = models.TextField(verbose_name="คำบรรยาย / รีวิวสรุป", blank=True, default="")
    address = models.CharField(max_length=300, verbose_name="ที่อยู่", blank=True, default="")
    location = models.CharField(max_length=200, verbose_name="ทำเล/ย่าน", blank=True, default="")
    category = models.CharField(max_length=100, verbose_name="หมวดหมู่", blank=True, default="")
    image_url = models.URLField(max_length=500, verbose_name="URL รูปภาพ", blank=True, default="")
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=4.5,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
        verbose_name="คะแนนเรตติ้ง (0.0-5.0)",
    )
    review_count = models.PositiveIntegerField(default=0, verbose_name="จำนวนรีวิว")
    price_level = models.IntegerField(
        choices=PRICE_CHOICES, default=2, verbose_name="ระดับราคา"
    )
    tags = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="คั่นด้วยเครื่องหมายจุลภาค เช่น กาแฟดี, มีที่จอดรถ, วิวหลักล้าน",
        verbose_name="แท็กคำค้นหา",
    )
    is_featured = models.BooleanField(default=False, verbose_name="สถานที่แนะนำ")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "สถานที่"
        verbose_name_plural = "สถานที่ทั้งหมด"
        ordering = ["-rating", "-review_count"]

    def __str__(self):
        return self.name

    @property
    def price_display(self):
        return "฿" * self.price_level

    @property
    def tag_list(self):
        if not self.tags:
            return []
        return [t.strip() for t in self.tags.split(",") if t.strip()]


class Wishlist(models.Model):
    user = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="wishlists",
        verbose_name="ผู้ใช้งาน",
    )
    session_key = models.CharField(
        max_length=40,
        blank=True,
        null=True,
        verbose_name="Session Key (สำหรับผู้ใช้ทั่วไป)",
    )
    place = models.ForeignKey(
        Place,
        on_delete=models.CASCADE,
        related_name="wishlists",
        verbose_name="สถานที่",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="วันที่บันทึก")

    class Meta:
        verbose_name = "สถานที่โปรด (Wishlist)"
        verbose_name_plural = "รายการสถานที่โปรดทั้งหมด"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "place"],
                name="unique_user_place_wishlist",
                condition=models.Q(user__isnull=False),
            ),
            models.UniqueConstraint(
                fields=["session_key", "place"],
                name="unique_session_place_wishlist",
                condition=models.Q(session_key__isnull=False),
            ),
        ]

    def __str__(self):
        user_display = (
            self.user.username if self.user else f"Guest ({self.session_key})"
        )
        return f"{user_display} -> {self.place.name}"
