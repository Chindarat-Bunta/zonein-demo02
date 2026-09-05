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
