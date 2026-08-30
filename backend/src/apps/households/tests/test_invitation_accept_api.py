from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.households.models import (
    Household,
    HouseholdInvitation,
    HouseholdMembership,
)


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def inviter():
    return User.objects.create_user(
        username="owner",
        email="owner@example.com",
        first_name="Household",
        last_name="Owner",
        password="test-password-123",
    )


@pytest.fixture
def invitee():
    return User.objects.create_user(
        username="invitee",
        email="invitee@example.com",
        first_name="Invited",
        last_name="User",
        password="test-password-123",
    )


@pytest.fixture
def wrong_user():
    return User.objects.create_user(
        username="wrong-user",
        email="wrong@example.com",
        first_name="Wrong",
        last_name="User",
        password="test-password-123",
    )


@pytest.fixture
def household():
    return Household.objects.create(
        name="Higgins Household",
    )


@pytest.fixture
def invitation(household, inviter):
    HouseholdMembership.objects.create(
        household=household,
        user=inviter,
        role=HouseholdMembership.Roles.OWNER,
    )

    invitation = HouseholdInvitation.objects.create(
        household=household,
        email="invitee@example.com",
        role=HouseholdMembership.Roles.MEMBER,
        invited_by=inviter,
    )

    token = invitation.generate_token()

    invitation.save(
        update_fields=[
            "token_hash",
            "expires_at",
            "updated_at",
        ]
    )

    return invitation, token


def invitation_accept_url(token):
    return reverse(
        "households:invitation-accept",
        kwargs={"token": token},
    )


@pytest.mark.django_db
def test_accept_invitation_requires_authentication(
    api_client,
    invitation,
):
    _, token = invitation

    response = api_client.post(
        invitation_accept_url(token),
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_valid_invitation_creates_membership(
    api_client,
    household,
    invitation,
    invitee,
):
    invitation_record, token = invitation

    api_client.force_authenticate(user=invitee)

    response = api_client.post(
        invitation_accept_url(token),
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    membership = HouseholdMembership.objects.get(
        household=household,
        user=invitee,
    )

    assert membership.is_active is True
    assert membership.role == HouseholdMembership.Roles.MEMBER

    invitation_record.refresh_from_db()

    assert invitation_record.status == HouseholdInvitation.Status.ACCEPTED
    assert invitation_record.accepted_at is not None


@pytest.mark.django_db
def test_accept_invitation_returns_membership_details(
    api_client,
    household,
    invitation,
    invitee,
):
    _, token = invitation

    api_client.force_authenticate(user=invitee)

    response = api_client.post(
        invitation_accept_url(token),
        format="json",
    )

    membership = HouseholdMembership.objects.get(
        household=household,
        user=invitee,
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {
        "household_id": household.pk,
        "household_name": household.name,
        "membership_id": membership.pk,
        "role": HouseholdMembership.Roles.MEMBER,
        "status": HouseholdInvitation.Status.ACCEPTED,
    }


@pytest.mark.django_db
def test_invitation_role_is_applied_to_membership(
    api_client,
    household,
    invitation,
    invitee,
):
    invitation_record, token = invitation

    invitation_record.role = HouseholdMembership.Roles.ADMINISTRATOR
    invitation_record.save(
        update_fields=[
            "role",
            "updated_at",
        ]
    )

    api_client.force_authenticate(user=invitee)

    response = api_client.post(
        invitation_accept_url(token),
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    membership = HouseholdMembership.objects.get(
        household=household,
        user=invitee,
    )

    assert membership.role == (HouseholdMembership.Roles.ADMINISTRATOR)


@pytest.mark.django_db
def test_wrong_user_email_cannot_accept_invitation(
    api_client,
    invitation,
    wrong_user,
):
    _, token = invitation

    api_client.force_authenticate(user=wrong_user)

    response = api_client.post(
        invitation_accept_url(token),
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data["detail"] == ("This invitation was sent to a different email address.")

    assert (
        HouseholdMembership.objects.filter(
            user=wrong_user,
        ).exists()
        is False
    )


@pytest.mark.django_db
def test_email_comparison_is_case_insensitive(
    api_client,
    invitation,
    invitee,
):
    invitation_record, token = invitation

    invitation_record.email = "INVITEE@EXAMPLE.COM"
    invitation_record.save(
        update_fields=[
            "email",
            "updated_at",
        ]
    )

    api_client.force_authenticate(user=invitee)

    response = api_client.post(
        invitation_accept_url(token),
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_invalid_token_is_rejected(
    api_client,
    invitee,
):
    api_client.force_authenticate(user=invitee)

    response = api_client.post(
        invitation_accept_url("not-a-real-invitation-token"),
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "token" in response.data


@pytest.mark.django_db
def test_expired_invitation_is_rejected(
    api_client,
    invitation,
    invitee,
):
    invitation_record, token = invitation

    invitation_record.expires_at = timezone.now() - timedelta(minutes=1)
    invitation_record.save(
        update_fields=[
            "expires_at",
            "updated_at",
        ]
    )

    api_client.force_authenticate(user=invitee)

    response = api_client.post(
        invitation_accept_url(token),
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "token" in response.data

    invitation_record.refresh_from_db()

    assert invitation_record.status == (HouseholdInvitation.Status.PENDING)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "invitation_status",
    [
        HouseholdInvitation.Status.ACCEPTED,
        HouseholdInvitation.Status.DECLINED,
        HouseholdInvitation.Status.CANCELED,
    ],
)
def test_non_pending_invitation_is_rejected(
    api_client,
    invitation,
    invitee,
    invitation_status,
):
    invitation_record, token = invitation

    invitation_record.status = invitation_status
    invitation_record.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )

    api_client.force_authenticate(user=invitee)

    response = api_client.post(
        invitation_accept_url(token),
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "token" in response.data


@pytest.mark.django_db
def test_inactive_membership_is_reactivated(
    api_client,
    household,
    invitation,
    invitee,
):
    _, token = invitation

    membership = HouseholdMembership.objects.create(
        household=household,
        user=invitee,
        role=HouseholdMembership.Roles.GUEST,
        is_active=False,
    )

    api_client.force_authenticate(user=invitee)

    response = api_client.post(
        invitation_accept_url(token),
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    membership.refresh_from_db()

    assert membership.is_active is True
    assert membership.role == HouseholdMembership.Roles.MEMBER


@pytest.mark.django_db
def test_existing_active_membership_is_updated_idempotently(
    api_client,
    household,
    invitation,
    invitee,
):
    invitation_record, token = invitation

    invitation_record.role = HouseholdMembership.Roles.ADMINISTRATOR
    invitation_record.save(
        update_fields=[
            "role",
            "updated_at",
        ]
    )

    membership = HouseholdMembership.objects.create(
        household=household,
        user=invitee,
        role=HouseholdMembership.Roles.MEMBER,
        is_active=True,
    )

    api_client.force_authenticate(user=invitee)

    response = api_client.post(
        invitation_accept_url(token),
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    membership.refresh_from_db()

    assert membership.is_active is True
    assert membership.role == (HouseholdMembership.Roles.ADMINISTRATOR)

    assert (
        HouseholdMembership.objects.filter(
            household=household,
            user=invitee,
        ).count()
        == 1
    )


@pytest.mark.django_db
def test_accepted_invitation_cannot_be_reused(
    api_client,
    invitation,
    invitee,
):
    invitation_record, token = invitation

    api_client.force_authenticate(user=invitee)

    first_response = api_client.post(
        invitation_accept_url(token),
        format="json",
    )

    assert first_response.status_code == status.HTTP_200_OK

    invitation_record.refresh_from_db()

    assert invitation_record.status == (HouseholdInvitation.Status.ACCEPTED)

    second_response = api_client.post(
        invitation_accept_url(token),
        format="json",
    )

    assert second_response.status_code == (status.HTTP_400_BAD_REQUEST)
    assert "token" in second_response.data


@pytest.mark.django_db
def test_acceptance_sets_accepted_at_close_to_current_time(
    api_client,
    invitation,
    invitee,
):
    invitation_record, token = invitation

    before_acceptance = timezone.now()

    api_client.force_authenticate(user=invitee)

    response = api_client.post(
        invitation_accept_url(token),
        format="json",
    )

    after_acceptance = timezone.now()

    assert response.status_code == status.HTTP_200_OK

    invitation_record.refresh_from_db()

    assert invitation_record.accepted_at is not None
    assert before_acceptance <= invitation_record.accepted_at
    assert invitation_record.accepted_at <= after_acceptance
