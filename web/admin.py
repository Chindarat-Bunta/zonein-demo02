from django.contrib import admin
from .models import (
    Comment,
    Notification,
    Place,
    PlaceImage,
    PlaceLike,
    Review,
    UserProfile,
    Wishlist,
)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "nickname", "avatar_url", "created_at")
    search_fields = ("user__username", "nickname", "bio")


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "author", "address", "created_at")
    list_filter = ("category", "created_at")
    search_fields = ("name", "description", "address", "author__username")


@admin.register(PlaceImage)
class PlaceImageAdmin(admin.ModelAdmin):
    list_display = ("place", "caption", "created_at")
    search_fields = ("place__name", "caption")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("place", "user", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("place__name", "user__username", "comment")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("review", "author", "created_at")
    search_fields = ("author__username", "content")
    list_filter = ("created_at",)


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("user", "place", "created_at")
    search_fields = ("user__username", "place__name")


@admin.register(PlaceLike)
class PlaceLikeAdmin(admin.ModelAdmin):
    list_display = ("user", "place", "created_at")
    search_fields = ("user__username", "place__name")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "actor", "action_type", "post", "recipient", "is_read", "created_at")
    list_filter = ("action_type", "is_read", "created_at")
    search_fields = ("actor__username", "recipient__username", "post__name", "message")
    list_editable = ("is_read",)
    readonly_fields = ("created_at", "updated_at")
