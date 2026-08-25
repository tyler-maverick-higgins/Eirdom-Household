from django.urls import path

from .views import (
    HouseholdDetailView,
    HouseholdInvitationCreateView,
    HouseholdInvitationValidationView,
    HouseholdListView,
)

app_name = "households"

urlpatterns = [
    path(
        "",
        HouseholdListView.as_view(),
        name="household-list",
    ),
    path(
        "<int:household_id>/invitations/",
        HouseholdInvitationCreateView.as_view(),
        name="invitation-create",
    ),
    path(
        "<int:pk>/",
        HouseholdDetailView.as_view(),
        name="household-detail",
    ),
    path(
        "invitations/<str:token>/",
        HouseholdInvitationValidationView.as_view(),
        name="invitation-validate",
    ),
]
