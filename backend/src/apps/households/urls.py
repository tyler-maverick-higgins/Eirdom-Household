from django.urls import path

from .views import (
    HouseholdDetailView,
    HouseholdInvitationAcceptView,
    HouseholdInvitationCancelView,
    HouseholdInvitationCreateView,
    HouseholdInvitationResendView,
    HouseholdInvitationValidationView,
    HouseholdListView,
    HouseholdMemberAdministrationView,
    HouseholdMembershipUpdateView,
    HouseholdOwnershipTransferView,
    HouseholdSettingsUpdateView,
)

app_name = "households"

urlpatterns = [
    path(
        "",
        HouseholdListView.as_view(),
        name="household-list",
    ),
    path(
        "<int:household_id>/settings/",
        HouseholdSettingsUpdateView.as_view(),
        name="household-settings",
    ),
    path(
        "<int:household_id>/members/",
        HouseholdMemberAdministrationView.as_view(),
        name="member-administration",
    ),
    path(
        "<int:household_id>/members/<int:membership_id>/",
        HouseholdMembershipUpdateView.as_view(),
        name="membership-update",
    ),
    path(
        "<int:household_id>/ownership/transfer/",
        HouseholdOwnershipTransferView.as_view(),
        name="ownership-transfer",
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
        "invitations/<int:invitation_id>/resend/",
        HouseholdInvitationResendView.as_view(),
        name="invitation-resend",
    ),
    path(
        "invitations/<int:invitation_id>/cancel/",
        HouseholdInvitationCancelView.as_view(),
        name="invitation-cancel",
    ),
    path(
        "invitations/<str:token>/",
        HouseholdInvitationValidationView.as_view(),
        name="invitation-validate",
    ),
    path(
        "invitations/<str:token>/accept/",
        HouseholdInvitationAcceptView.as_view(),
        name="invitation-accept",
    ),
]
