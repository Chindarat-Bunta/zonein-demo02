from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """
    Profile extension model for User containing nickname, bio,
    and Cloudinary avatar information.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    nickname = models.CharField(max_length=100, blank=True, default="", verbose_name="ชื่อเล่น / ชื่อที่แสดง")
    bio = models.TextField(max_length=500, blank=True, default="", verbose_name="ข้อความ Bio แนะนำตัว")
    avatar_url = models.URLField(max_length=500, blank=True, default="", verbose_name="รูปโปรไฟล์ Cloudinary URL")
    avatar_public_id = models.CharField(max_length=255, blank=True, default="", verbose_name="Cloudinary Public ID")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.username}"

    def get_display_name(self):
        if self.nickname:
            return self.nickname
        if self.user.first_name:
            return self.user.first_name
        return self.user.username


@receiver(post_save, sender=User)
def create_or_save_user_profile(sender, instance, created, **kwargs):
    """Ensure UserProfile is automatically created when a User is created."""
    if created:
        UserProfile.objects.create(user=instance)
    else:
        if hasattr(instance, "profile"):
            instance.profile.save()
