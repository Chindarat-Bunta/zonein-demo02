import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Place",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255, verbose_name="ชื่อสถานที่")),
                (
                    "slug",
                    models.SlugField(blank=True, max_length=255, verbose_name="Slug"),
                ),
                (
                    "category",
                    models.CharField(
                        blank=True,
                        default="travel",
                        max_length=100,
                        verbose_name="หมวดหมู่",
                    ),
                ),
                (
                    "description",
                    models.TextField(blank=True, default="", verbose_name="รายละเอียดสถานที่"),
                ),
                (
                    "address",
                    models.CharField(
                        blank=True, default="", max_length=255, verbose_name="ที่อยู่ / พิกัดตำบล-อำเภอ"
                    ),
                ),
                (
                    "latitude",
                    models.DecimalField(
                        blank=True,
                        decimal_places=7,
                        max_digits=10,
                        null=True,
                        verbose_name="ละติจูด (Google Maps)",
                    ),
                ),
                (
                    "longitude",
                    models.DecimalField(
                        blank=True,
                        decimal_places=7,
                        max_digits=10,
                        null=True,
                        verbose_name="ลองจิจูด (Google Maps)",
                    ),
                ),
                (
                    "cover_image_url",
                    models.TextField(
                        blank=True, default="", verbose_name="รูปภาพปกสถานที่"
                    ),
                ),
                (
                    "cover_image_public_id",
                    models.CharField(
                        blank=True, default="", max_length=200, verbose_name="Cloudinary Cover ID"
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="สร้างเมื่อ"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="แก้ไขล่าสุดเมื่อ"),
                ),
                (
                    "author",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="places",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="ผู้สร้างโพสต์",
                    ),
                ),
            ],
            options={
                "verbose_name": "สถานที่ / โพสต์",
                "verbose_name_plural": "สถานที่ / โพสต์ทั้งหมด",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="PlaceImage",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "image_url",
                    models.URLField(
                        max_length=500, verbose_name="URL รูปภาพ (Cloudinary)"
                    ),
                ),
                (
                    "public_id",
                    models.CharField(
                        blank=True, max_length=200, verbose_name="Cloudinary Public ID"
                    ),
                ),
                (
                    "caption",
                    models.CharField(
                        blank=True, max_length=255, verbose_name="คำอธิบายภาพ"
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="อัปโหลดเมื่อ"),
                ),
                (
                    "place",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="images",
                        to="web.place",
                        verbose_name="สถานที่",
                    ),
                ),
            ],
            options={
                "verbose_name": "รูปภาพสถานที่",
                "verbose_name_plural": "รูปภาพสถานที่ทั้งหมด",
                "ordering": ["created_at"],
            },
        ),
        migrations.CreateModel(
            name="Review",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "rating",
                    models.PositiveSmallIntegerField(
                        help_text="คะแนนความประทับใจ 1-5 ดาว",
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(5),
                        ],
                        verbose_name="คะแนนดาว (1-5)",
                    ),
                ),
                (
                    "comment",
                    models.TextField(
                        blank=True,
                        default="",
                        help_text="ข้อความรีวิวบรรยากาศและประสบการณ์",
                        verbose_name="ข้อความรีวิว",
                    ),
                ),
                (
                    "image_url",
                    models.TextField(
                        blank=True,
                        default="",
                        help_text="รูปถ่ายสถานที่ประกอบรีวิว",
                        verbose_name="รูปถ่ายสถานที่ประกอบรีวิว",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="เขียนเมื่อ"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="แก้ไขเมื่อ"),
                ),
                (
                    "place",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reviews",
                        to="web.place",
                        verbose_name="สถานที่ที่ถูกรีวิว",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reviews",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="ผู้รีวิว",
                    ),
                ),
            ],
            options={
                "verbose_name": "รีวิว",
                "verbose_name_plural": "รีวิวทั้งหมด",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="Comment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("content", models.TextField(help_text="ข้อความความคิดเห็น", verbose_name="ข้อความความคิดเห็น")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="คอมเมนต์เมื่อ")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="แก้ไขเมื่อ")),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="comments",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="ผู้คอมเมนต์",
                    ),
                ),
                (
                    "review",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="comments",
                        to="web.review",
                        verbose_name="รีวิวที่คอมเมนต์",
                    ),
                ),
            ],
            options={
                "verbose_name": "ความคิดเห็น (Comment)",
                "verbose_name_plural": "ความคิดเห็นทั้งหมด (Comments)",
                "ordering": ["created_at"],
            },
        ),
        migrations.CreateModel(
            name="UserProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "nickname",
                    models.CharField(
                        blank=True, max_length=100, verbose_name="ชื่อเล่น / ชื่อที่แสดง"
                    ),
                ),
                (
                    "avatar_url",
                    models.URLField(
                        blank=True,
                        max_length=500,
                        verbose_name="รูปโปรไฟล์ (Cloudinary/OAuth URL)",
                    ),
                ),
                (
                    "avatar_public_id",
                    models.CharField(
                        blank=True, max_length=200, verbose_name="Cloudinary Public ID"
                    ),
                ),
                (
                    "bio",
                    models.TextField(
                        blank=True, max_length=500, verbose_name="ข้อความ Bio แนะนำตัว"
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="สร้างเมื่อ"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="แก้ไขล่าสุดเมื่อ"),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "โปรไฟล์ผู้ใช้",
                "verbose_name_plural": "โปรไฟล์ผู้ใช้ทั้งหมด",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="PlaceLike",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="กดไลก์เมื่อ"),
                ),
                (
                    "place",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="likes",
                        to="web.place",
                        verbose_name="สถานที่ที่ถูกใจ",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="likes",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="ผู้ใช้",
                    ),
                ),
            ],
            options={
                "verbose_name": "การกดไลก์ (Like)",
                "verbose_name_plural": "การกดไลก์ทั้งหมด (Likes)",
                "ordering": ["-created_at"],
                "unique_together": {("user", "place")},
            },
        ),
        migrations.CreateModel(
            name="Wishlist",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="บันทึกเมื่อ"),
                ),
                (
                    "place",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="wishlisted_by",
                        to="web.place",
                        verbose_name="สถานที่โปรด",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="wishlists",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="ผู้ใช้",
                    ),
                ),
            ],
            options={
                "verbose_name": "รายการโปรด (Wishlist)",
                "verbose_name_plural": "รายการโปรดทั้งหมด (Wishlists)",
                "ordering": ["-created_at"],
                "unique_together": {("user", "place")},
            },
        ),
    ]
