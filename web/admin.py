from django.contrib import admin
from .models import TravelPost


@admin.register(TravelPost)
class TravelPostAdmin(admin.ModelAdmin):
    list_display = ("place_name", "category", "location", "rating", "author", "created_at")
    search_fields = ("place_name", "location", "category", "content", "author__username")
    list_filter = ("rating", "category", "created_at")
    filter_horizontal = ("tagged_users",)
    readonly_fields = ("created_at", "updated_at")
