from django.contrib import admin
from .models import Category, Location, Place


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "icon", "color")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("city", "zone", "slug")
    prepopulated_fields = {"slug": ("city", "zone")}
    search_fields = ("city", "zone")
    list_filter = ("city",)


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
    list_filter = ("category", "location__city", "location", "price_level", "is_featured")
    search_fields = ("name", "description", "address", "tags")
    prepopulated_fields = {"slug": ("name",)}
