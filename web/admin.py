from django.contrib import admin
from .models import PostComment, PostLike, TravelPost


@admin.register(TravelPost)
class TravelPostAdmin(admin.ModelAdmin):
    list_display = ("place_name", "location", "rating", "likes_count", "comments_count", "author", "created_at")
    search_fields = ("place_name", "location", "content", "author__username")
    list_filter = ("rating", "created_at")
    readonly_fields = ("created_at", "updated_at")


@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ("user", "post", "created_at")
    search_fields = ("user__username", "post__place_name")
    list_filter = ("created_at",)


@admin.register(PostComment)
class PostCommentAdmin(admin.ModelAdmin):
    list_display = ("user", "post", "content", "created_at")
    search_fields = ("user__username", "post__place_name", "content")
    list_filter = ("created_at",)

