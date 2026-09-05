from django.contrib import admin
from .models import Place, Review


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "location", "average_rating", "review_count", "created_at")
    search_fields = ("name", "category", "location", "description")
    list_filter = ("category", "created_at")
    readonly_fields = ("average_rating", "review_count", "created_at", "updated_at")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("target", "user", "rating", "created_at", "updated_at")
    list_filter = ("rating", "created_at")
    search_fields = ("target__name", "user__username", "comment")
    filter_horizontal = ("tagged_users",)
    readonly_fields = ("created_at", "updated_at")
