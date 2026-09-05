from django.contrib import admin
from .models import Product, Review


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "average_rating", "review_count", "created_at")
    search_fields = ("name", "description")
    readonly_fields = ("average_rating", "review_count", "created_at", "updated_at")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("target", "user", "rating", "created_at", "updated_at")
    list_filter = ("rating", "created_at")
    search_fields = ("target__name", "user__username", "comment")
    readonly_fields = ("created_at", "updated_at")
