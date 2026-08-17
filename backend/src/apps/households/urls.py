from django.urls import path

from .views import HouseholdInvitationCreateView, HouseholdListView

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
]
