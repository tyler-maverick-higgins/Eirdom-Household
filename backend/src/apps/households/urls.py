from django.urls import path

from .views import HouseholdInvitationCreateView

app_name = "households"

urlpatterns = [
    path(
        "<int:household_id>/invitations/",
        HouseholdInvitationCreateView.as_view(),
        name="invitation-create",
    )
]
