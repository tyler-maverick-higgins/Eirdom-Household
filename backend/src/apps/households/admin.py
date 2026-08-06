from django.contrib import admin
from django.db.models import Count
from django.utils import timezone

from .models import Household, HouseholdMembership


class TimestampedAdmin(admin.ModelAdmin):
    readonly_fields = (
        "created_at",
        "updated_at",
    )

    @admin.display(ordering="created_at")
    def created(self, obj):
        return timezone.localtime(obj.created_at).strftime("%Y-%m-%d %I:%M %p")

    @admin.display(ordering="updated_at")
    def updated(self, obj):
        return timezone.localtime(obj.updated_at).strftime("%Y-%m-%d %I:%M %p")

    list_display = (
        "created",
        "updated",
    )


class HouseholdMembershipInline(admin.TabularInline):
    model = HouseholdMembership
    fields = (
        "user",
        "role",
        "is_active",
        "created_at",
    )
    readonly_fields = ("created_at",)
    autocomplete_fields = ("user",)
    extra = 0
    show_change_link = True


@admin.register(Household)
class HouseholdAdmin(TimestampedAdmin):
    list_display = (
        "name",
        "slug",
        "member_count",
        "created",
        "updated",
    )
    search_fields = (
        "name",
        "slug",
    )
    ordering = ("name",)
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    prepopulated_fields = {"slug": ("name",)}
    inlines = (HouseholdMembershipInline,)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(
            membership_count=Count("memberships"),
        )

    @admin.display(
        description="Total memberships",
        ordering="membership_count",
    )
    def member_count(self, obj: Household) -> int:
        return getattr(obj, "membership_count", 0)


@admin.register(HouseholdMembership)
class HouseholdMembershipAdmin(TimestampedAdmin):
    list_display = (
        "user",
        "household",
        "role",
        "is_active",
        "created",
        "updated",
    )
    list_filter = (
        "role",
        "is_active",
        "household",
    )
    search_fields = (
        "user__username",
        "user__email",
        "household__name",
        "household__slug",
    )
    ordering = (
        "household",
        "created_at",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    autocomplete_fields = (
        "user",
        "household",
    )
    list_select_related = (
        "user",
        "household",
    )
