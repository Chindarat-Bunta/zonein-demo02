from django.contrib import admin
from .models import Place, Wishlist


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "location",
        "rating",
        "review_count",
        "price_level",
        "is_featured",
    )
    list_filter = (
        "category",
        "price_level",
        "is_featured",
    )
    search_fields = ("name", "description", "address", "tags")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("place", "user", "session_key", "created_at")
    list_filter = ("created_at",)
    search_fields = ("place__name", "user__username", "session_key")
