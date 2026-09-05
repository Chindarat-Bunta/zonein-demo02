from django.contrib import admin
from .models import Place, Review


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ("name", "location", "category", "created_at")
    search_fields = ("name", "location", "category", "description")
    list_filter = ("category", "created_at")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("place", "author", "rating", "created_at")
    search_fields = ("place__name", "author__username", "content")
    list_filter = ("rating", "created_at")
