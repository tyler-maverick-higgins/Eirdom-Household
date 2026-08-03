from django.contrib import admin

from .models import Household


@admin.register(Household)
class HouseholdAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "name",
        "slug",
    )
    ordering = (
        "name",
        "created_at",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
