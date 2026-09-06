from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="ชื่อหมวดหมู่")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="Slug")
    icon = models.CharField(
        max_length=50, default="fa-compass", verbose_name="FontAwesome Icon"
    )
    color = models.CharField(max_length=20, default="#3b82f6", verbose_name="สีธีม")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "หมวดหมู่"
        verbose_name_plural = "หมวดหมู่ทั้งหมด"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Location(models.Model):
    city = models.CharField(max_length=100, verbose_name="เมือง/จังหวัด")
    zone = models.CharField(max_length=100, verbose_name="ย่าน/ทำเล")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="Slug")

    class Meta:
        verbose_name = "ทำเล/ย่าน"
        verbose_name_plural = "ทำเล/ย่านทั้งหมด"
        ordering = ["city", "zone"]

    def __str__(self):
        return f"{self.city} - {self.zone}"


class Place(models.Model):
    PRICE_CHOICES = [
        (1, "฿ (ประหยัด)"),
        (2, "฿฿ (ปานกลาง)"),
        (3, "฿฿฿ (พรีเมียม)"),
        (4, "฿฿฿฿ (หรูหรา)"),
    ]

    name = models.CharField(max_length=200, verbose_name="ชื่อสถานที่")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="Slug")
    description = models.TextField(verbose_name="คำบรรยาย / รีวิวสรุป")
    address = models.CharField(max_length=300, verbose_name="ที่อยู่")
    image_url = models.URLField(max_length=500, verbose_name="URL รูปภาพ", blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name="places",
        verbose_name="หมวดหมู่",
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        related_name="places",
        verbose_name="ทำเล/ย่าน",
    )
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
        help_text="คั่นด้วยเครื่องหมายจุลภาค เช่น กาแฟดี, มีที่จอดรถ, วิวหลักล้าน",
        verbose_name="แท็กคำค้นหา",
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name="ละติจูด (Latitude)",
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name="ลองจิจูด (Longitude)",
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

    @property
    def has_coordinates(self):
        if self.latitude is not None and self.longitude is not None:
            try:
                lat = float(self.latitude)
                lng = float(self.longitude)
                return -90.0 <= lat <= 90.0 and -180.0 <= lng <= 180.0
            except (ValueError, TypeError):
                return False
        return False

    @property
    def maps_navigation_url(self):
        import urllib.parse

        if self.has_coordinates:
            lat = f"{float(self.latitude):.6f}".rstrip("0").rstrip(".")
            lng = f"{float(self.longitude):.6f}".rstrip("0").rstrip(".")
            return f"https://www.google.com/maps/dir/?api=1&destination={lat},{lng}"
        # Fallback to destination name or address
        query = self.name
        if self.address:
            query = f"{self.name} {self.address}"
        encoded_dest = urllib.parse.quote_plus(query)
        return f"https://www.google.com/maps/dir/?api=1&destination={encoded_dest}"


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
