from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify


# ==============================================================================
# 1. UserProfile Model (ระบบสมาชิก: รูปโปรไฟล์ Cloudinary, ชื่อเล่น, Bio)
# ==============================================================================
class UserProfile(models.Model):
    """
    Extends Django's User model with Zone In specific fields:
    - Custom nickname / display name
    - Profile picture stored via Cloudinary or OAuth
    - Bio introduction
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    nickname = models.CharField(max_length=100, blank=True, verbose_name="ชื่อเล่น / ชื่อที่แสดง")
    avatar_url = models.URLField(max_length=500, blank=True, verbose_name="รูปโปรไฟล์ (Cloudinary/OAuth URL)")
    avatar_public_id = models.CharField(max_length=200, blank=True, verbose_name="Cloudinary Public ID")
    bio = models.TextField(max_length=500, blank=True, verbose_name="ข้อความ Bio แนะนำตัว")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="สร้างเมื่อ")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="แก้ไขล่าสุดเมื่อ")

    class Meta:
        verbose_name = "โปรไฟล์ผู้ใช้"
        verbose_name_plural = "โปรไฟล์ผู้ใช้ทั้งหมด"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Profile of {self.get_display_name()} (@{self.user.username})"

    def get_display_name(self):
        return self.nickname or self.user.first_name or self.user.username


@receiver(post_save, sender=User)
def create_or_save_user_profile(sender, instance, created, **kwargs):
    """Automatically create or save UserProfile whenever a User is created/saved."""
    if created:
        UserProfile.objects.create(user=instance)
    elif hasattr(instance, "profile"):
        instance.profile.save()


# ==============================================================================
# 2. Place / Post Model (สถานที่ท่องเที่ยว / โพสต์แนะนำสถานที่)
# ==============================================================================
class Place(models.Model):
    """
    Represents a place or travel post created by users:
    - Title, category, description, and address / location
    - Coordinates (latitude & longitude) for Google Maps integration
    - Cover image hosted via Cloudinary
    - Author relation
    """
    CATEGORY_CHOICES = [
        ("cafe", "คาเฟ่ (Cafe)"),
        ("restaurant", "ร้านอาหาร (Restaurant)"),
        ("travel", "สถานที่ท่องเที่ยว (Travel/Attraction)"),
        ("hotel", "ที่พัก / โรงแรม (Hotel/Resort)"),
        ("nature", "ธรรมชาติ / แคมป์ปิ้ง (Nature/Camping)"),
        ("other", "อื่นๆ (Other)"),
    ]

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="places",
        null=True,
        blank=True,
        verbose_name="ผู้สร้างโพสต์"
    )
    name = models.CharField(max_length=255, verbose_name="ชื่อสถานที่")
    slug = models.SlugField(max_length=255, blank=True, db_index=True, verbose_name="Slug")
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, default="travel", blank=True, verbose_name="หมวดหมู่")
    description = models.TextField(blank=True, default="", verbose_name="รายละเอียดสถานที่")
    address = models.CharField(max_length=255, blank=True, default="", verbose_name="ที่อยู่ / พิกัดตำบล-อำเภอ")
    # Google Maps coordinates
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True, verbose_name="ละติจูด (Google Maps)")
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True, verbose_name="ลองจิจูด (Google Maps)")
    # Cloudinary cover image
    cover_image_url = models.TextField(blank=True, default="", verbose_name="รูปภาพปกสถานที่")
    cover_image_public_id = models.CharField(max_length=200, blank=True, default="", verbose_name="Cloudinary Cover ID")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="สร้างเมื่อ")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="แก้ไขล่าสุดเมื่อ")

    class Meta:
        verbose_name = "สถานที่ / โพสต์"
        verbose_name_plural = "สถานที่ / โพสต์ทั้งหมด"
        ordering = ["-created_at"]

    def __str__(self):
        cat = dict(self.CATEGORY_CHOICES).get(self.category, self.category)
        return f"{self.name} ({cat})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    @property
    def location(self):
        return self.address

    @location.setter
    def location(self, val):
        self.address = val

    @property
    def image_url(self):
        return self.cover_image_url

    @image_url.setter
    def image_url(self, val):
        self.cover_image_url = val

    @property
    def average_rating(self):
        """Calculate average rating from reviews (returns 0.0 if no reviews)."""
        aggregate = self.reviews.aggregate(models.Avg("rating"))
        avg = aggregate.get("rating__avg")
        return round(float(avg), 1) if avg is not None else 0.0

    @property
    def review_count(self):
        return self.reviews.count()

    @property
    def reviews_count(self):
        return self.reviews.count()

    @property
    def likes_count(self):
        return self.likes.count()

    @property
    def wishlist_count(self):
        return self.wishlisted_by.count()

    @property
    def maps_navigation_url(self):
        """Google Maps direct navigation link (เปิดนำทางทันที)"""
        if self.latitude and self.longitude:
            return f"https://www.google.com/maps/dir/?api=1&destination={self.latitude},{self.longitude}"
        import urllib.parse
        dest = f"{self.name} {self.address}".strip()
        return f"https://www.google.com/maps/dir/?api=1&destination={urllib.parse.quote_plus(dest)}"

    @property
    def maps_search_url(self):
        """Google Maps search link (ดูตำแหน่งบน Google Maps)"""
        if self.latitude and self.longitude:
            return f"https://www.google.com/maps/search/?api=1&query={self.latitude},{self.longitude}"
        import urllib.parse
        dest = f"{self.name} {self.address}".strip()
        return f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote_plus(dest)}"

    @property
    def maps_embed_url(self):
        """Google Maps Embed iframe URL for map preview"""
        if self.latitude and self.longitude:
            return f"https://maps.google.com/maps?q={self.latitude},{self.longitude}&hl=th&z=15&output=embed"
        import urllib.parse
        dest = f"{self.name} {self.address}".strip()
        return f"https://maps.google.com/maps?q={urllib.parse.quote_plus(dest)}&hl=th&z=15&output=embed"

    @property
    def rating_breakdown(self):
        """Calculate review counts and percentages for each star rating (5 down to 1)"""
        total = self.reviews_count
        counts = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
        for r in self.reviews.all():
            if r.rating in counts:
                counts[r.rating] += 1
        breakdown = []
        for star in range(5, 0, -1):
            cnt = counts[star]
            pct = round((cnt / total * 100)) if total > 0 else 0
            breakdown.append({
                "star": star,
                "count": cnt,
                "percentage": pct,
            })
        return breakdown


# ==============================================================================
# 3. PlaceImage Model (รูปภาพเพิ่มเติมของสถานที่ / แกลเลอรี Cloudinary)
# ==============================================================================
class PlaceImage(models.Model):
    """Gallery images for a place, stored in Cloudinary."""
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name="images", verbose_name="สถานที่")
    image_url = models.URLField(max_length=500, verbose_name="URL รูปภาพ (Cloudinary)")
    public_id = models.CharField(max_length=200, blank=True, verbose_name="Cloudinary Public ID")
    caption = models.CharField(max_length=255, blank=True, verbose_name="คำอธิบายภาพ")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="อัปโหลดเมื่อ")

    class Meta:
        verbose_name = "รูปภาพสถานที่"
        verbose_name_plural = "รูปภาพสถานที่ทั้งหมด"
        ordering = ["created_at"]

    def __str__(self):
        return f"Image for {self.place.name}"


# ==============================================================================
# 4. Review Model (ระบบเรตติ้ง: 1-5 ดาว, ข้อความรีวิว, User ID, Place ID)
# ==============================================================================
class Review(models.Model):
    """
    User ratings and reviews for places:
    - 1 to 5 star rating
    - Text review
    - Link to User and Place
    - Image attachment
    """
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name="reviews", verbose_name="สถานที่ที่ถูกรีวิว")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews", verbose_name="ผู้รีวิว")
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="คะแนนดาว (1-5)",
        help_text="คะแนนความประทับใจ 1-5 ดาว",
    )
    comment = models.TextField(blank=True, default="", verbose_name="ข้อความรีวิว", help_text="ข้อความรีวิวบรรยากาศและประสบการณ์")
    image_url = models.TextField(blank=True, default="", verbose_name="รูปถ่ายสถานที่ประกอบรีวิว", help_text="รูปถ่ายสถานที่ประกอบรีวิว")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="เขียนเมื่อ")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="แก้ไขเมื่อ")

    class Meta:
        verbose_name = "รีวิว"
        verbose_name_plural = "รีวิวทั้งหมด"
        ordering = ["-created_at"]

    def __str__(self):
        return f"★ {self.rating} by {self.user.username} for {self.place.name}"

    @property
    def author(self):
        return self.user

    @author.setter
    def author(self, val):
        self.user = val

    @property
    def content(self):
        return self.comment

    @content.setter
    def content(self, val):
        self.comment = val


# ==============================================================================
# 5. Comment Model (ระบบคอมเมนต์ต่อรีวิว)
# ==============================================================================
class Comment(models.Model):
    """
    Comment left by viewers on a travel review.
    ความคิดเห็นของคนที่เข้ามาดูรีวิว
    """
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="comments", verbose_name="รีวิวที่คอมเมนต์")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments", verbose_name="ผู้คอมเมนต์")
    content = models.TextField(verbose_name="ข้อความความคิดเห็น", help_text="ข้อความความคิดเห็น")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="คอมเมนต์เมื่อ")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="แก้ไขเมื่อ")

    class Meta:
        verbose_name = "ความคิดเห็น (Comment)"
        verbose_name_plural = "ความคิดเห็นทั้งหมด (Comments)"
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.author.username} on review #{self.review_id}: {self.content[:30]}"


# ==============================================================================
# 6. Wishlist Model (ระบบสถานที่โปรด: User ID, Place ID)
# ==============================================================================
class Wishlist(models.Model):
    """User wishlist / bookmarks for places."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wishlists", verbose_name="ผู้ใช้")
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name="wishlisted_by", verbose_name="สถานที่โปรด")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="บันทึกเมื่อ")

    class Meta:
        verbose_name = "รายการโปรด (Wishlist)"
        verbose_name_plural = "รายการโปรดทั้งหมด (Wishlists)"
        unique_together = ("user", "place")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} saved {self.place.name}"


# ==============================================================================
# 7. PlaceLike Model (ระบบ Like / กดหัวใจ: User ID, Place ID)
# ==============================================================================
class PlaceLike(models.Model):
    """User likes / hearts for places."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes", verbose_name="ผู้ใช้")
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name="likes", verbose_name="สถานที่ที่ถูกใจ")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="กดไลก์เมื่อ")

    class Meta:
        verbose_name = "การกดไลก์ (Like)"
        verbose_name_plural = "การกดไลก์ทั้งหมด (Likes)"
        unique_together = ("user", "place")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} liked {self.place.name}"


# ==============================================================================
# 8. Notification Model (ระบบการแจ้งเตือน)
# ==============================================================================
class Notification(models.Model):
    """
    ตาราง Notification เก็บข้อมูลการแจ้งเตือน:
    - ใครเป็นคนกระทำ (actor / sender): ผู้ใช้ที่ทำแอคชัน (เช่น กดไลก์, เขียนรีวิว)
    - ผู้รับการแจ้งเตือน (recipient / user): เจ้าของโพสต์ที่ได้รับการแจ้งเตือน
    - ทำแอคชันอะไร (action_type): ประเภทแอคชัน เช่น like (กดไลก์), review (รีวิว), comment (คอมเมนต์), follow (ติดตาม)
    - กระทำกับโพสต์ไหน (post / place): โพสต์หรือสถานที่ที่เกี่ยวข้อง
    - ผู้ใช้กดอ่านหรือยัง (is_read): สถานะว่าเปิดอ่านหรือยัง (True/False)
    """
    ACTION_CHOICES = [
        ("like", "กดไลก์ (Like)"),
        ("review", "เขียนรีวิว (Review)"),
        ("comment", "แสดงความคิดเห็น (Comment)"),
        ("follow", "ติดตาม (Follow)"),
        ("other", "อื่นๆ (Other)"),
    ]

    actor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications_sent",
        verbose_name="ใครเป็นคนกระทำ (Actor / Sender)"
    )
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications_received",
        verbose_name="ผู้รับการแจ้งเตือน (Recipient)"
    )
    action_type = models.CharField(
        max_length=50,
        choices=ACTION_CHOICES,
        default="like",
        verbose_name="ทำแอคชันอะไร (Action Type)",
        help_text="ประเภทของแอคชัน เช่น like, review, comment, follow"
    )
    post = models.ForeignKey(
        Place,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
        verbose_name="กระทำกับโพสต์ไหน (Target Post / Place)"
    )
    is_read = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="สถานะกดอ่านแล้วหรือยัง (is_read)"
    )
    message = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="ข้อความแจ้งเตือน"
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="เวลาที่เกิดการกระทำ")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="เวลาที่อัปเดตล่าสุด")

    class Meta:
        verbose_name = "การแจ้งเตือน (Notification)"
        verbose_name_plural = "การแจ้งเตือนทั้งหมด (Notifications)"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient", "is_read"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        post_info = f" บนโพสต์ '{self.post.name}'" if self.post else ""
        return f"{self.actor.username} {self.get_action_type_display()}{post_info} -> {self.recipient.username} ({'อ่านแล้ว' if self.is_read else 'ยังไม่อ่าน'})"

    @property
    def sender(self):
        return self.actor

    @property
    def place(self):
        return self.post

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=["is_read", "updated_at"])

    @property
    def summary_text(self):
        if self.message:
            return self.message

        actor_name = getattr(self.actor, "profile", None)
        actor_display = actor_name.get_display_name() if actor_name else self.actor.username
        post_name = f"'{self.post.name}'" if self.post else "โพสต์ของคุณ"

        if self.action_type == "like":
            return f"{actor_display} ได้กดไลก์ {post_name}"
        elif self.action_type == "review":
            return f"{actor_display} ได้เขียนรีวิวบน {post_name}"
        elif self.action_type == "comment":
            return f"{actor_display} ได้แสดงความคิดเห็นบน {post_name}"
        elif self.action_type == "follow":
            return f"{actor_display} ได้เริ่มติดตามคุณ"
        return f"{actor_display} มีการเคลื่อนไหวใหม่บน {post_name}"


# ==============================================================================
# Backward compatibility aliases
# ==============================================================================
TravelPost = Place
PostLike = PlaceLike
